from huggingface_hub import snapshot_download

dataset_path = snapshot_download(
    repo_id="Arshia82sbn/pcb-object-detection-dataset",
    repo_type="dataset",
    local_dir="dataset/pcb_source"
)

print("Dataset downloaded successfully!")
print("Location:")
print(dataset_path)