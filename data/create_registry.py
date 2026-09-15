import os
import json
import csv

def create_registry():
    manifest_path = os.path.join(os.path.dirname(__file__), "manifests", "plantvillage_clean_manifest.csv")
    registry_path = os.path.join(os.path.dirname(__file__), "class_registry.json")
    
    classes = {}
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cls = row['class_label']
            if cls not in classes:
                classes[cls] = {
                    "class_label": cls,
                    "crop": row['crop'],
                    "disease": row['disease'],
                    "is_healthy": row['disease'].lower() == 'healthy'
                }
                
    # Sort alphabetically to be deterministic
    sorted_classes = sorted(classes.keys())
    
    registry = {}
    for i, cls in enumerate(sorted_classes):
        registry[str(i)] = classes[cls]
        registry[str(i)]["index"] = i
        
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=4)
        
    print(f"Authoritative class registry created at {registry_path} with {len(registry)} classes.")

if __name__ == "__main__":
    create_registry()
