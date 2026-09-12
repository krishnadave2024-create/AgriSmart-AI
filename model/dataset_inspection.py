import os
import json
from config import Config
from PIL import Image

def inspect_dataset():
    stats = {
        "dataset_name": Config.DATASET_NAME,
        "type": Config.DATASET_TYPE,
        "total_images": 0,
        "num_classes": 0,
        "classes": [],
        "images_per_class": {},
        "image_formats": set(),
        "image_dimensions": set(),
        "corrupted_images": [],
        "empty_directories": []
    }
    
    if not os.path.exists(Config.DATASET_ROOT):
        print("Dataset root not found.")
        return
        
    for cls in os.listdir(Config.DATASET_ROOT):
        cls_path = os.path.join(Config.DATASET_ROOT, cls)
        if os.path.isdir(cls_path):
            stats["classes"].append(cls)
            stats["num_classes"] += 1
            images = os.listdir(cls_path)
            
            if len(images) == 0:
                stats["empty_directories"].append(cls)
            else:
                stats["images_per_class"][cls] = 0
                for img_name in images:
                    img_path = os.path.join(cls_path, img_name)
                    ext = os.path.splitext(img_name)[1].lower()
                    if ext in Config.SUPPORTED_EXTENSIONS:
                        stats["images_per_class"][cls] += 1
                        stats["total_images"] += 1
                        stats["image_formats"].add(ext)
                        
                        try:
                            with Image.open(img_path) as img:
                                img.verify()
                                stats["image_dimensions"].add(f"{img.width}x{img.height}")
                        except Exception as e:
                            stats["corrupted_images"].append(img_path)

    stats["image_formats"] = list(stats["image_formats"])
    stats["image_dimensions"] = list(stats["image_dimensions"])
    
    report_json_path = os.path.join(Config.BASE_DIR, "data", "reports", "development_dataset_statistics.json")
    report_md_path = os.path.join(Config.BASE_DIR, "data", "reports", "development_dataset_statistics.md")
    
    with open(report_json_path, 'w') as f:
        json.dump(stats, f, indent=4)
        
    with open(report_md_path, 'w') as f:
        f.write(f"# Dataset Statistics Report\n\n")
        f.write(f"- **Name**: {stats['dataset_name']}\n")
        f.write(f"- **Type**: {stats['type']}\n")
        f.write(f"- **Total Images**: {stats['total_images']}\n")
        f.write(f"- **Number of Classes**: {stats['num_classes']}\n")
        f.write(f"\n## Classes\n")
        for cls, count in stats["images_per_class"].items():
            f.write(f"- {cls}: {count} images\n")
        f.write(f"\n## Technical Details\n")
        f.write(f"- **Formats**: {', '.join(stats['image_formats'])}\n")
        f.write(f"- **Dimensions**: {', '.join(stats['image_dimensions'])}\n")
        f.write(f"- **Corrupted Images**: {len(stats['corrupted_images'])}\n")
        f.write(f"- **Empty Directories**: {len(stats['empty_directories'])}\n")

    print(f"Inspection complete. Reports generated at {report_json_path} and {report_md_path}")

if __name__ == "__main__":
    inspect_dataset()
