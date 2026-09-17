from ultralytics import YOLO

model = YOLO(
    "runs/detect/results/pcb_first_model/weights/best.pt"
)

metrics = model.val(
    data="dataset/pcb/data.yaml",
    split="test",
    imgsz=640,
    batch=4,
    device="cpu",
    plots=True
)

print("\n======================================")
print("PER-CLASS PERFORMANCE")
print("======================================")

names = model.names

for i, name in names.items():
    precision = metrics.box.p[i]
    recall = metrics.box.r[i]
    map50 = metrics.box.ap50[i]
    map5095 = metrics.box.ap[i]

    print(
        f"{i:2d} {name:15s} "
        f"Precision={precision:.3f} "
        f"Recall={recall:.3f} "
        f"mAP50={map50:.3f} "
        f"mAP50-95={map5095:.3f}"
    )

print("======================================")