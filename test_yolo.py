from ultralytics import YOLO

# Load a pre-trained YOLO model
model = YOLO("yolo26n.pt")

# Run YOLO on our test image
results = model("test_images/test.jpg")

# Save the result image
for result in results:
    result.save("results/result.jpg")

print("Detection completed!")
print("Result saved to results/result.jpg")