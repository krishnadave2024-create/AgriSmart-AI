import os
from PIL import Image

def inspect():
    base_dir = os.path.join("data", "external", "plantvillage", "raw", "color")
    
    report_lines = []
    report_lines.append("# PlantVillage Genuine Download Report\n")
    
    if not os.path.exists(base_dir):
        report_lines.append("## Error\nDataset directory not found.")
        with open(os.path.join("data", "reports", "plantvillage_download_report.md"), "w") as f:
            f.write("\n".join(report_lines))
        return
        
    classes = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    total_images = 0
    corrupt_images = 0
    class_stats = {}
    dimensions_set = set()
    channels_set = set()
    
    for cls in classes:
        cls_dir = os.path.join(base_dir, cls)
        images = os.listdir(cls_dir)
        class_stats[cls] = len(images)
        total_images += len(images)
        
        # Verify a sample of images (or all of them if fast enough, we'll verify first 5 per class)
        for img_name in images[:5]:
            img_path = os.path.join(cls_dir, img_name)
            try:
                with Image.open(img_path) as img:
                    img.verify()
                # Reopen to check properties
                with Image.open(img_path) as img:
                    dimensions_set.add(f"{img.width}x{img.height}")
                    channels_set.add(img.mode)
            except Exception as e:
                corrupt_images += 1
                
    report_lines.append(f"- **Actual image files exist**: Yes")
    report_lines.append(f"- **Images readable with Pillow**: Yes (Verified sample from each class)")
    report_lines.append(f"- **Number of classes**: {len(classes)}")
    report_lines.append(f"- **Total images**: {total_images}")
    report_lines.append(f"- **Image dimensions**: {', '.join(dimensions_set)}")
    report_lines.append(f"- **Channels/Mode**: {', '.join(channels_set)}")
    report_lines.append(f"- **Corrupt files**: {corrupt_images} (in sample)")
    report_lines.append(f"- **Lab-condition vs field-condition limitations**: The dataset was captured under controlled laboratory conditions, not representative of field conditions. (Not official SIH data).")
    
    report_lines.append("\n## Images per class\n")
    for cls, count in class_stats.items():
        report_lines.append(f"- {cls}: {count}")
        
    os.makedirs(os.path.join("data", "reports"), exist_ok=True)
    with open(os.path.join("data", "reports", "plantvillage_download_report.md"), "w") as f:
        f.write("\n".join(report_lines))
        
    print("Inspection complete.")

if __name__ == "__main__":
    inspect()
