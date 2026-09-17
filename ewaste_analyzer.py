from ultralytics import YOLO
from component_database import COMPONENT_DATABASE
from price_database import PRICE_DATABASE
from grouping import get_groups
import cv2
import os

# ============================================================
# E-WASTE AI ANALYZER - VERSION 2
# Detection + Component Information
# ============================================================

MODEL_PATH = "runs/detect/results/pcb_first_model/weights/best.pt"

print("Loading E-Waste AI model...")

model = YOLO(MODEL_PATH)

print("Model loaded successfully!")
print("Component database loaded:", len(COMPONENT_DATABASE), "components")

# ------------------------------------------------------------
# Ask for image
# ------------------------------------------------------------

image_path = input(
    "\nEnter the full path of your PCB image:\n> "
).strip().strip('"')

if not os.path.exists(image_path):
    print("\nERROR: Image not found!")
    print("Please check the image path.")
    exit()

# ------------------------------------------------------------
# Detection
# ------------------------------------------------------------

print("\nAnalyzing image...")

results = model.predict(
    source=image_path,
    conf=0.25,
    imgsz=640,
    max_det=500,
    save=False
)

result = results[0]

# ------------------------------------------------------------
# Count components
# ------------------------------------------------------------

component_counts = {}

total_min_value = 0
total_max_value = 0

group_counts = {
    "reusable": 0,
    "recyclable": 0,
    "pure_waste": 0,
    "metal_bearing": 0
}

image = result.orig_img.copy()

for box in result.boxes:

    class_id = int(box.cls[0])
    confidence = float(box.conf[0])

    component_name = model.names[class_id]

    # Count
    if component_name not in component_counts:
        component_counts[component_name] = 0

    component_counts[component_name] += 1

    # Bounding box
    x1, y1, x2, y2 = map(
        int,
        box.xyxy[0]
    )

    # Draw rectangle
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (255, 255, 255),
        2
    )

    # Draw label
    label = f"{component_name} {confidence * 100:.1f}%"

    cv2.putText(
        image,
        label,
        (x1, max(y1 - 8, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

# ------------------------------------------------------------
# Save image
# ------------------------------------------------------------

os.makedirs("results", exist_ok=True)

output_path = "results/ewaste_analysis.jpg"

cv2.imwrite(
    output_path,
    image
)

# ------------------------------------------------------------
# E-WASTE SUMMARY
# ------------------------------------------------------------

print("\n")
print("=" * 70)
print("                    E-WASTE AI SUMMARY")
print("=" * 70)

if not component_counts:

    print("\nNo components detected.")

else:

    total = sum(component_counts.values())

    print(f"\nTotal detected components: {total}")

    print("\nDetected components:")
    print("-" * 70)

    for component, count in sorted(component_counts.items()):

        info = COMPONENT_DATABASE.get(component)
        price = PRICE_DATABASE.get(component)
        
        groups = get_groups(component)

        for group in groups:
            group_counts[group] += count

        print(f"\n{component.upper()}")
        print(f"  Quantity       : {count}")

        if info:

            print(f"  Category       : {info['category']}")
            print(f"  Reuse          : {info['reuse']}")
            print(f"  Material       : {info['material']}")
            print(f"  Metal          : {info['metal']}")

        else:

            print("  No database information available.")

        if price:

            min_value = count * price["min_price"]
            max_value = count * price["max_price"]

            total_min_value += min_value
            total_max_value += max_value

            print(
                f"  Estimated value: "
                f"₹{min_value:.2f} - ₹{max_value:.2f}"
            )

        else:

            print("  Price data     : Not available")


# ------------------------------------------------------------
# VALUE ESTIMATE
# ------------------------------------------------------------

# ------------------------------------------------------------
# AUTOMATIC GROUPING
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("                    SCRAP GROUPING")
print("=" * 70)

print(f"\nReusable       : {group_counts['reusable']}")
print(f"Recyclable     : {group_counts['recyclable']}")
print(f"Pure waste     : {group_counts['pure_waste']}")
print(f"Metal-bearing  : {group_counts['metal_bearing']}")

print("\n" + "=" * 70)
print("                    VALUE ESTIMATE")
print("=" * 70)

print(
    "\nEstimated total component value:"
)

print(
    f"₹{total_min_value:.2f} - ₹{total_max_value:.2f}"
)

print(
    "\nNOTE: This is an approximate prototype estimate."
)

print(
    "Actual value depends on condition, weight, type, "
    "material composition and local market rates."
)

print("\nAnnotated image:")
print(os.path.abspath(output_path))

print("\nAnalysis completed!")
print("=" * 70)