from ultralytics import YOLO

# Load a small pretrained YOLO model
model = YOLO("yolo11n.pt")

# Train on our PCB dataset
results = model.train(
    data="dataset/pcb/data.yaml",
    epochs=10,
    imgsz=640,
    batch=4,
    device="cpu",
    workers=2,
    project="results",
    name="pcb_first_model"
)

print("\nTraining completed!")
print("Best model should be saved inside:")
print("results/pcb_first_model/weights/best.pt")