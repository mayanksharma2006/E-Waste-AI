from ultralytics import YOLO
import os

# Load our trained model
model = YOLO(
    "runs/detect/results/pcb_first_model/weights/best.pt"
)

# Use an image from the TEST dataset
image_folder = "dataset/pcb/test/images"

images = [
    f for f in os.listdir(image_folder)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

if not images:
    raise RuntimeError("No test images found!")

# Take the first test image
image_path = os.path.join(image_folder, images[0])

print("Testing image:", image_path)

# Run detection
results = model.predict(
    source=image_path,
    conf=0.25,
    save=True
)

print("\nDetection completed!")

for result in results:
    print("\nDetected components:")

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        name = model.names[class_id]

        print(
            f"  {name}: {confidence * 100:.1f}%"
        )