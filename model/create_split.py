import os
import pandas as pd
from sklearn.model_selection import train_test_split
from config import Config

def create_split():
    if not os.path.exists(Config.DATASET_ROOT):
        print("Dataset root not found.")
        return
        
    data = []
    for cls in Config.CLASSES:
        cls_path = os.path.join(Config.DATASET_ROOT, cls)
        if os.path.isdir(cls_path):
            for img_name in os.listdir(cls_path):
                ext = os.path.splitext(img_name)[1].lower()
                if ext in Config.SUPPORTED_EXTENSIONS:
                    data.append({
                        "path": os.path.join("data", "external", "development_dataset", cls, img_name),
                        "label": cls
                    })
                    
    df = pd.DataFrame(data)
    
    # Stratified split
    train_df, val_df = train_test_split(
        df, 
        train_size=Config.SPLIT_RATIO, 
        stratify=df['label'], 
        random_state=Config.RANDOM_SEED
    )
    
    train_df.to_csv(Config.TRAIN_MANIFEST, index=False)
    val_df.to_csv(Config.VAL_MANIFEST, index=False)
    
    print(f"Created train split ({len(train_df)} samples) at {Config.TRAIN_MANIFEST}")
    print(f"Created val split ({len(val_df)} samples) at {Config.VAL_MANIFEST}")

if __name__ == "__main__":
    create_split()
