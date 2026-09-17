import os
import yaml
from collections import Counter

label_dir = "dataset/pcb/train/labels"
yaml_file = "dataset/pcb/data.yaml"

# Load class names
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)

class_names = data["names"]

# Count every class
counts = Counter()

for filename in os.listdir(label_dir):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(label_dir, filename)

    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) >= 5:
                class_id = int(parts[0])
                counts[class_id] += 1

print("\nPCB DATASET CLASS DISTRIBUTION")
print("=" * 45)

for class_id, class_name in enumerate(class_names):
    print(f"{class_id:2d}  {class_name:15s} : {counts[class_id]}")

print("=" * 45)
print("Total annotations:", sum(counts.values()))