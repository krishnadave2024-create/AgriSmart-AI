import os
from PIL import Image
from config import Config

def check_quality():
    issues = {
        "corrupted": [],
        "unsupported_format": [],
        "empty_folders": [],
        "invalid_dimensions": []
    }
    
    if not os.path.exists(Config.DATASET_ROOT):
        print("Dataset root not found.")
        return
        
    for cls in os.listdir(Config.DATASET_ROOT):
        cls_path = os.path.join(Config.DATASET_ROOT, cls)
        if os.path.isdir(cls_path):
            images = os.listdir(cls_path)
            if len(images) == 0:
                issues["empty_folders"].append(cls)
            
            for img_name in images:
                img_path = os.path.join(cls_path, img_name)
                ext = os.path.splitext(img_name)[1].lower()
                
                if ext not in Config.SUPPORTED_EXTENSIONS:
                    issues["unsupported_format"].append(img_path)
                    continue
                
                try:
                    with Image.open(img_path) as img:
                        img.verify()
                        # We would need to reopen it to check dimensions properly after verify, 
                        # but we'll assume verify catches major issues.
                        # For dimension check, let's reopen
                    with Image.open(img_path) as img:
                        if img.width <= 0 or img.height <= 0:
                            issues["invalid_dimensions"].append(img_path)
                except Exception as e:
                    issues["corrupted"].append(img_path)
    
    print("Data Quality Report:")
    print(f"Corrupted Images: {len(issues['corrupted'])}")
    print(f"Unsupported Formats: {len(issues['unsupported_format'])}")
    print(f"Empty Folders: {len(issues['empty_folders'])}")
    print(f"Invalid Dimensions: {len(issues['invalid_dimensions'])}")
    
    if any(issues.values()):
        print("Issues found. Check script for details.")
    else:
        print("All quality checks passed.")

if __name__ == "__main__":
    check_quality()
