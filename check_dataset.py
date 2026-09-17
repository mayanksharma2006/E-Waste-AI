import os
import cv2
import yaml

# Dataset locations
image_dir = "dataset/pcb/train/images"
label_dir = "dataset/pcb/train/labels"
yaml_file = "dataset/pcb/data.yaml"
output_file = "results/annotation_check.jpg"

# Read class names
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)

class_names = data["names"]

# Find the first image
image_files = [
    f for f in os.listdir(image_dir)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

image_files.sort()

if not image_files:
    raise RuntimeError("No training images found!")

image_name = image_files[0]

image_path = os.path.join(image_dir, image_name)

# Corresponding label
label_name = os.path.splitext(image_name)[0] + ".txt"
label_path = os.path.join(label_dir, label_name)

# Load image
image = cv2.imread(image_path)

if image is None:
    raise RuntimeError(f"Could not read image: {image_path}")

height, width = image.shape[:2]

# Read YOLO labels
with open(label_path, "r") as f:
    lines = f.readlines()

# Draw each annotation
for line in lines:
    parts = line.strip().split()

    if len(parts) != 5:
        continue

    class_id = int(parts[0])
    x_center = float(parts[1])
    y_center = float(parts[2])
    box_width = float(parts[3])
    box_height = float(parts[4])

    # Convert YOLO coordinates to pixels
    x_center *= width
    y_center *= height
    box_width *= width
    box_height *= height

    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)
    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)

    # Draw bounding box
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 255, 255), 2)

    # Component name
    name = class_names[class_id]

    cv2.putText(
        image,
        name,
        (x1, max(y1 - 5, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

# Create results folder if necessary
os.makedirs("results", exist_ok=True)

# Save result
cv2.imwrite(output_file, image)

print("Annotation check completed!")
print("Image:", image_name)
print("Annotations:", len(lines))
print("Saved to:", output_file)