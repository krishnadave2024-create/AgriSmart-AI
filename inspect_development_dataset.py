import os
import hashlib
from PIL import Image

def get_hash(img_path):
    with open(img_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def inspect():
    base_dir = os.path.join("data", "external", "development_dataset", "raw")
    if not os.path.exists(base_dir):
        print("Dataset directory not found.")
        return
        
    classes = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    total_images = 0
    corrupt_images = 0
    zero_byte = 0
    class_stats = {}
    dimensions_set = set()
    channels_set = set()
    hashes = set()
    duplicates = 0
    
    for cls in classes:
        cls_dir = os.path.join(base_dir, cls)
        images = os.listdir(cls_dir)
        class_stats[cls] = 0
        
        for img_name in images:
            img_path = os.path.join(cls_dir, img_name)
            
            # Check zero byte
            if os.path.getsize(img_path) == 0:
                zero_byte += 1
                corrupt_images += 1
                continue
                
            # Check hash
            h = get_hash(img_path)
            if h in hashes:
                duplicates += 1
            hashes.add(h)
            
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    dimensions_set.add(f"{img.width}x{img.height}")
                    channels_set.add(img.mode)
                class_stats[cls] += 1
                total_images += 1
            except Exception:
                corrupt_images += 1

    report_lines = []
    report_lines.append("# Development Dataset Selection & Inspection Report\n")
    report_lines.append("## This is development data only. It is not the official SIH dataset. The official SIH dataset remains unverified.\n")
    report_lines.append(f"- **Source**: Hugging Face (ayerr/plant-disease-classification)")
    report_lines.append(f"- **Total images**: {total_images}")
    report_lines.append(f"- **Number of classes**: {len(classes)}")
    report_lines.append(f"- **Corrupt images**: {corrupt_images} (Zero byte: {zero_byte})")
    report_lines.append(f"- **Duplicates detected (exact hash)**: {duplicates}")
    report_lines.append(f"- **Image dimensions**: {', '.join(dimensions_set)}")
    report_lines.append(f"- **Channels/Mode**: {', '.join(channels_set)}")
    report_lines.append(f"- **Limitations**: This is a smaller dataset limited to a few classes for fast prototyping. Lab conditions. No explicit license found.")
    
    report_lines.append("\n## Class Distribution\n")
    for cls, count in class_stats.items():
        report_lines.append(f"- {cls}: {count}")
        
    os.makedirs(os.path.join("data", "reports"), exist_ok=True)
    report_content = "\n".join(report_lines)
    
    with open(os.path.join("data", "reports", "dataset_inspection_report.md"), "w") as f:
        f.write(report_content)
    with open(os.path.join("data", "reports", "development_dataset_selection_report.md"), "w") as f:
        f.write(report_content)
    with open(os.path.join("data", "reports", "dataset_quality_report.md"), "w") as f:
        f.write("# Dataset Quality\n\nSee dataset_inspection_report.md for full details.\n")
        f.write(f"- Duplicates: {duplicates}\n- Corrupt: {corrupt_images}\n")
        
    with open(os.path.join("data", "README.md"), "w") as f:
        f.write(report_content)
        
    print("Inspection complete. Reports generated.")

if __name__ == "__main__":
    inspect()
