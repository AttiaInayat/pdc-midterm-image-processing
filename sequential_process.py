import os
import time
from PIL import Image, ImageDraw, ImageFont

# Define paths
input_folder = 'images_dataset'
output_folder = 'output_seq'
watermark_text = "© AttiaAI"

# Start timer
start_time = time.time()

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Loop through class folders
for class_name in os.listdir(input_folder):
    class_path = os.path.join(input_folder, class_name)
    output_class_path = os.path.join(output_folder, class_name)

    # Skip non-folder files
    if not os.path.isdir(class_path):
        continue

    os.makedirs(output_class_path, exist_ok=True)

    for img_name in os.listdir(class_path):
        img_path = os.path.join(class_path, img_name)
        try:
            # Open and resize
            img = Image.open(img_path).convert("RGBA")
            img = img.resize((128, 128))

            # Add watermark
            draw = ImageDraw.Draw(img)
            font_size = 12
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            # ✅ Use textbbox instead of textsize (for Pillow >= 10)
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x, y = img.width - text_w - 5, img.height - text_h - 5

            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 180))

            # Save processed image
            output_path = os.path.join(output_class_path, img_name)
            img.convert("RGB").save(output_path, "JPEG")

        except Exception as e:
            print(f"Error processing {img_path}: {e}")

# Stop timer
end_time = time.time()
total_time = end_time - start_time

print(f"Sequential Processing Time: {total_time:.2f} seconds")
