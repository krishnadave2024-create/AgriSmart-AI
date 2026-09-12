import os
import pandas as pd
from sklearn.model_selection import train_test_split

def create_manifests():
    base_dir = os.path.join("data", "external", "development_dataset", "raw")
    if not os.path.exists(base_dir):
        print("Dataset directory not found.")
        return
        
    classes = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    records = []
    
    for cls in classes:
        cls_dir = os.path.join(base_dir, cls)
        for img in os.listdir(cls_dir):
            records.append({
                "image_path": os.path.join(cls_dir, img).replace("\\", "/"),
                "class_label": cls,
                "source": "ayerr/plant-disease-classification"
            })
            
    df = pd.DataFrame(records)
    if len(df) == 0:
        print("No images found.")
        return
        
    train_df, temp_df = train_test_split(df, test_size=0.3, stratify=df['class_label'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['class_label'], random_state=42)
    
    train_df['split'] = 'train'
    val_df['split'] = 'validation'
    test_df['split'] = 'test'
    
    os.makedirs(os.path.join("data", "manifests"), exist_ok=True)
    
    train_df.to_csv(os.path.join("data", "manifests", "development_train.csv"), index=False)
    val_df.to_csv(os.path.join("data", "manifests", "development_validation.csv"), index=False)
    test_df.to_csv(os.path.join("data", "manifests", "development_test.csv"), index=False)
    
    print("Manifests created.")

if __name__ == "__main__":
    create_manifests()
