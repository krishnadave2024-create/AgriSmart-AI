import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms

class LocalPlantDiseaseDataset(Dataset):
    def __init__(self, manifest_path, transform=None):
        self.df = pd.read_csv(manifest_path)
        self.transform = transform
        
        # Build class-to-idx mapping
        self.all_classes = sorted(self.df['class_label'].unique().tolist())
        self.class_to_idx = {cls: i for i, cls in enumerate(self.all_classes)}
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_path = row['image_path']
        
        # We need to construct absolute or relative path from project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Since image_path is like 'data/external/...', we can join it
        full_path = os.path.join(project_root, image_path)
        
        image = Image.open(full_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        label_idx = self.class_to_idx[row['class_label']]
        return image, label_idx

def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

def test_loader():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest_path = os.path.join(project_root, "data", "manifests", "development_train.csv")
    
    if not os.path.exists(manifest_path):
        print("Train manifest not found.")
        return
        
    transform = get_transforms()
    train_dataset = LocalPlantDiseaseDataset(manifest_path, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    
    print(f"Dataset Size: {len(train_dataset)}")
    for images, labels in train_loader:
        print(f"Batch Image Tensor Shape: {images.shape}")
        print(f"Batch Labels: {labels}")
        print(f"Batch Labels Shape: {labels.shape}")
        print(f"Pixel value range: min={images.min().item():.4f}, max={images.max().item():.4f}")
        break

if __name__ == "__main__":
    test_loader()
