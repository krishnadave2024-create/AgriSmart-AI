import os
import tensorflow_datasets as tfds
from PIL import Image

def extract_tfds_to_disk():
    base_dir = os.path.join("data", "external", "plantvillage", "raw")
    os.makedirs(base_dir, exist_ok=True)
    
    print("Downloading PlantVillage dataset using TFDS...")
    try:
        # download=True will download and prepare the dataset if not already done
        ds, info = tfds.load('plant_village', split='train', with_info=True, as_supervised=False)
    except Exception as e:
        print(f"FAILED TO DOWNLOAD. Error: {e}")
        return False
        
    print("Extracting images to disk...")
    # Map class index to class name
    num_classes = info.features['label'].num_classes
    class_names = info.features['label'].names
    
    for cls in class_names:
        os.makedirs(os.path.join(base_dir, cls), exist_ok=True)
        
    count = 0
    # Process only a subset to avoid full 54,000 extraction time during this session, 
    # but the prompt requires a real dataset. Let's extract them all if it's fast enough,
    # or just enough to prove it works. Wait, the prompt says "Do not use the previous invalid tiny sample. 
    # The development dataset should contain a meaningful number of real images and multiple disease classes."
    # We will extract 50 images per class to save disk space and time, but keep it substantial (1900 images total).
    
    class_counts = {cls: 0 for cls in class_names}
    max_per_class = 50 
    
    import numpy as np
    
    for item in ds.as_numpy_iterator():
        img_array = item['image']
        label_idx = item['label']
        cls_name = class_names[label_idx]
        filename = item['image/filename'].decode('utf-8') if isinstance(item['image/filename'], bytes) else item['image/filename']
        
        if class_counts[cls_name] < max_per_class:
            img = Image.fromarray(img_array)
            img.save(os.path.join(base_dir, cls_name, filename))
            class_counts[cls_name] += 1
            count += 1
            
            if count % 100 == 0:
                print(f"Extracted {count} images...")
                
        # Check if we have extracted max_per_class for all classes
        if all(c >= max_per_class for c in class_counts.values()):
            break

    print(f"Extraction complete. {count} images saved to {base_dir}")
    
    # Save source info
    info_dir = os.path.join("data", "external", "plantvillage", "source_info")
    os.makedirs(info_dir, exist_ok=True)
    with open(os.path.join(info_dir, "provenance.txt"), "w") as f:
        f.write(f"Source: TensorFlow Datasets (plant_village)\n")
        f.write(f"Citation:\n{info.citation}\n")
        f.write(f"Subset Limitation: Extracted {max_per_class} images per class due to time constraints in session.\n")
        
    return True

if __name__ == "__main__":
    extract_tfds_to_disk()
