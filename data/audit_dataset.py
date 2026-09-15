import os
import hashlib
from PIL import Image
import json

def audit_dataset():
    data_dir = os.path.join(os.path.dirname(__file__), "external", "plantvillage")
    
    if not os.path.exists(data_dir):
        print(json.dumps({"error": f"Directory not found: {data_dir}"}))
        return

    classes = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    audit = {
        "dataset_path": data_dir,
        "total_images": 0,
        "total_classes": len(classes),
        "crops": set(),
        "diseases": set(),
        "classes": {},
        "corrupt_files": [],
        "zero_byte_files": [],
        "non_image_files": [],
        "duplicates": []
    }
    
    file_hashes = {}
    duplicate_count = 0
    
    for cls in sorted(classes):
        cls_dir = os.path.join(data_dir, cls)
        
        # Parse crop and disease. PlantVillage format is "Crop___Disease"
        parts = cls.split("___")
        crop = parts[0]
        disease = parts[1] if len(parts) > 1 else "Unknown"
        
        audit["crops"].add(crop)
        audit["diseases"].add(disease)
        
        files = os.listdir(cls_dir)
        cls_stats = {
            "total": len(files),
            "crop": crop,
            "disease": disease
        }
        
        valid_images = 0
        
        for f in files:
            file_path = os.path.join(cls_dir, f)
            
            # Check size
            if os.path.getsize(file_path) == 0:
                audit["zero_byte_files"].append(file_path)
                continue
                
            # Check extension
            if not f.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG')):
                audit["non_image_files"].append(file_path)
                continue
                
            # Check image integrity
            try:
                with Image.open(file_path) as img:
                    img.verify() # verify integrity
            except Exception as e:
                audit["corrupt_files"].append(file_path)
                continue
                
            # Compute Hash for exact duplicate detection
            with open(file_path, "rb") as fp:
                file_hash = hashlib.md5(fp.read()).hexdigest()
                
            if file_hash in file_hashes:
                audit["duplicates"].append({"original": file_hashes[file_hash], "duplicate": file_path})
                duplicate_count += 1
            else:
                file_hashes[file_hash] = file_path
                
            valid_images += 1
            
        cls_stats["valid_images"] = valid_images
        audit["classes"][cls] = cls_stats
        audit["total_images"] += valid_images
        
    audit["crops"] = list(audit["crops"])
    audit["diseases"] = list(audit["diseases"])
    
    report_path = os.path.join(os.path.dirname(__file__), "reports", "audit_stats.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(audit, f, indent=4)
        
    print(f"Audit complete. Stats saved to {report_path}")

if __name__ == "__main__":
    audit_dataset()
