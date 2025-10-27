import os
import time
import multiprocessing
from PIL import Image, ImageDraw, ImageFont

# --- Config ---
input_folder = 'images_dataset'
output_folder = 'output_distributed'
watermark_text = "© AttiaAI"

os.makedirs(output_folder, exist_ok=True)

# --- Image Processing Function ---
def process_image(task):
    img_path, output_path = task
    try:
        img = Image.open(img_path).convert("RGBA")
        img = img.resize((128, 128))

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

    except Exception as e:
        print(f"Error processing {img_path}: {e}")

# --- Collect all image paths ---
def get_all_images():
    image_list = []
    for class_name in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_name)
        if not os.path.isdir(class_path):
            continue
        for img_name in os.listdir(class_path):
            img_path = os.path.join(class_path, img_name)
            out_class_path = os.path.join(output_folder, class_name)
            os.makedirs(out_class_path, exist_ok=True)
            out_path = os.path.join(out_class_path, img_name)
            image_list.append((img_path, out_path))
    return image_list

# --- Node Function ---
def node_worker(node_id, image_subset, return_dict):
    start = time.perf_counter()
    with multiprocessing.Pool() as pool:
        pool.map(process_image, image_subset)
    end = time.perf_counter()
    return_dict[node_id] = (len(image_subset), end - start)

# --- Main Distributed Simulation ---
if __name__ == "__main__":
    print(f"CPU Cores Available: {os.cpu_count()}\n")

    all_images = get_all_images()
    total_images = len(all_images)
    print(f"Total images found: {total_images}")

    # Split dataset equally between 2 logical nodes
    half = total_images // 2
    node1_data = all_images[:half]
    node2_data = all_images[half:]

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    total_start = time.perf_counter()

    # Create and start two simulated nodes
    p1 = multiprocessing.Process(target=node_worker, args=(1, node1_data, return_dict))
    p2 = multiprocessing.Process(target=node_worker, args=(2, node2_data, return_dict))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    total_end = time.perf_counter()
    total_time = total_end - total_start

    # Retrieve node times
    node1_count, node1_time = return_dict[1]
    node2_count, node2_time = return_dict[2]

    # Sequential baseline (replace with your measured sequential time)
    sequential_time = 18.24
    efficiency = sequential_time / total_time

    # --- Output Summary ---
    print(f"\nNode 1 processed {node1_count} images in {node1_time:.2f}s")
    print(f"Node 2 processed {node2_count} images in {node2_time:.2f}s")
    print(f"Total distributed time: {total_time:.2f}s")
    print(f"Efficiency: {efficiency:.2f}x over sequential")
