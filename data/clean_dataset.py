import os
import csv
import hashlib
from PIL import Image

def clean_dataset():
    data_dir = os.path.join(os.path.dirname(__file__), "external", "plantvillage")
    manifest_dir = os.path.join(os.path.dirname(__file__), "manifests")
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, "plantvillage_clean_manifest.csv")
    
    classes = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
    
    records = []
    seen_hashes = {}
    
    print("Starting dataset cleaning...")
    
    duplicate_count = 0
    invalid_count = 0
    clean_count = 0
    
    for cls in classes:
        cls_dir = os.path.join(data_dir, cls)
        parts = cls.split("___")
        crop = parts[0]
        disease = parts[1] if len(parts) > 1 else "Unknown"
        
        files = sorted(os.listdir(cls_dir))
        for f in files:
            file_path = os.path.join(cls_dir, f)
            rel_path = f"external/plantvillage/{cls}/{f}"
            
            # Check size
            if os.path.getsize(file_path) == 0:
                invalid_count += 1
                continue
                
            if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG')):
                invalid_count += 1
                continue
                
            try:
                with Image.open(file_path) as img:
                    img.verify()
                with Image.open(file_path) as img:
                    width, height = img.size
            except Exception:
                invalid_count += 1
                continue
                
            # Compute Hash
            with open(file_path, "rb") as fp:
                file_hash = hashlib.md5(fp.read()).hexdigest()
                
            is_duplicate = False
            if file_hash in seen_hashes:
                is_duplicate = True
                duplicate_count += 1
            else:
                seen_hashes[file_hash] = rel_path
                clean_count += 1
                
            if not is_duplicate:
                records.append({
                    "relative_path": rel_path,
                    "class_label": cls,
                    "crop": crop,
                    "disease": disease,
                    "file_hash": file_hash,
                    "width": width,
                    "height": height,
                    "source": "PlantVillage",
                    "is_duplicate": is_duplicate
                })
                
    # Sort deterministically
    records.sort(key=lambda x: x['relative_path'])
    
    print(f"Writing manifest to {manifest_path}...")
    with open(manifest_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["relative_path", "class_label", "crop", "disease", "file_hash", "width", "height", "source", "is_duplicate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
            
    print(f"Cleaning complete.")
    print(f"Total raw processed: {clean_count + duplicate_count + invalid_count}")
    print(f"Cleaned images written to manifest: {clean_count}")
    print(f"Exact duplicates excluded: {duplicate_count}")
    print(f"Invalid/Corrupt images excluded: {invalid_count}")

if __name__ == "__main__":
    clean_dataset()
