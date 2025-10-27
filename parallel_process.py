import os
import time
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageDraw, ImageFont

# Paths
input_folder = 'images_dataset'
output_base = 'output_parallel'
watermark_text = "© AttiaAI"

# Ensure base output directory exists
os.makedirs(output_base, exist_ok=True)

# Function: process one image
def process_image(task):
    img_path, output_path = task
    try:
        img = Image.open(img_path).convert("RGBA")
        img = img.resize((128, 128))

        # Add watermark
        draw = ImageDraw.Draw(img)
        font_size = 12
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = img.width - text_w - 5, img.height - text_h - 5
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 180))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.convert("RGB").save(output_path, "JPEG")
        return True

    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return False

# Collect all (input_path, output_path) pairs
def get_image_tasks():
    tasks = []
    for class_name in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_name)
        if not os.path.isdir(class_path):
            continue
        for img_name in os.listdir(class_path):
            input_path = os.path.join(class_path, img_name)
            output_dir = os.path.join(output_base, class_name)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, img_name)
            tasks.append((input_path, output_path))
    return tasks

# Run parallel processing with N workers
def run_parallel(num_workers):
    tasks = get_image_tasks()
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        executor.map(process_image, tasks)
    total_time = time.time() - start_time
    return total_time

if __name__ == "__main__":
    worker_counts = [1, 2, 4, 8]
    results = []

    print("\nRunning parallel processing tests...\n")

    for n in worker_counts:
        print(f"Processing with {n} workers...")
        t = run_parallel(n)
        results.append((n, t))
        print(f"Time for {n} workers: {t:.2f} seconds\n")

    # Calculate and print speedup table
    base_time = results[0][1]
    print("Workers | Time (s) | Speedup")
    print("-------- | -------- | -------")
    for n, t in results:
        speedup = base_time / t
        print(f"{n:<7} | {t:<8.2f} | {speedup:.2f}x")
