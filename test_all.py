from ultralytics import YOLO

model = YOLO(
    "runs/detect/results/pcb_first_model/weights/best.pt"
)

results = model.val(
    data="dataset/pcb/data.yaml",
    split="test",
    imgsz=640,
    batch=4,
    device="cpu"
)

print("\n================================")
print("TESTING COMPLETED")
print("================================")

print("mAP50:", results.box.map50)
print("mAP50-95:", results.box.map)