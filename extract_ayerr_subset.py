import os
import hashlib
from datasets import load_dataset
from PIL import Image

def get_hash(img):
    return hashlib.md5(img.tobytes()).hexdigest()

def extract_subset():
    dataset_id = "ayerr/plant-disease-classification"
    print(f"Loading HF dataset {dataset_id}...")
    
    # We will use streaming to avoid downloading the entire 2.5GB archive if not needed
    try:
        ds = load_dataset(dataset_id, split="train", streaming=True, trust_remote_code=False)
    except Exception as e:
        print(f"FAILED TO LOAD DATASET: {e}")
        return False
        
    base_dir = os.path.join("data", "external", "development_dataset", "raw")
    os.makedirs(base_dir, exist_ok=True)
    
    # ayerr dataset has classes 'diseased' and 'healthy'
    class_names = ["diseased", "healthy"]
    for c in class_names:
        os.makedirs(os.path.join(base_dir, c), exist_ok=True)
        
    max_per_class = 50
    counts = {c: 0 for c in class_names}
    hashes = set()
    total_downloaded = 0
    duplicate_count = 0
    
    for item in ds:
        label_idx = item['label']
        cls = class_names[label_idx]
        
        if counts[cls] < max_per_class:
            img = item['image'].convert('RGB')
            img_hash = get_hash(img)
            
            if img_hash in hashes:
                duplicate_count += 1
                continue
                
            hashes.add(img_hash)
            
            filename = f"{cls}_{counts[cls]:04d}.jpg"
            img.save(os.path.join(base_dir, cls, filename))
            counts[cls] += 1
            total_downloaded += 1
            
        if all(c >= max_per_class for c in counts.values()):
            break
            
    print(f"Successfully downloaded {total_downloaded} images.")
    print(f"Duplicates skipped during download: {duplicate_count}")
    
    info_dir = os.path.join("data", "external", "development_dataset", "source_info")
    os.makedirs(info_dir, exist_ok=True)
    with open(os.path.join(info_dir, "provenance.txt"), "w") as f:
        f.write(f"Source: Hugging Face ({dataset_id})\n")
        f.write(f"Subset Limitation: Extracted {max_per_class} unique images per class for fast prototyping.\n")
        
    return True

if __name__ == "__main__":
    extract_subset()
