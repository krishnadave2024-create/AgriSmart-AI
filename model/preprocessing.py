import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from datasets import load_dataset

class HFPlantVillageDataset(Dataset):
    def __init__(self, manifest_path, transform=None):
        self.df = pd.read_csv(manifest_path)
        self.transform = transform
        
        print("Loading HF Dataset cache for dataloader...")
        # Load the HF dataset so we can access images by index
        self.hf_dataset = load_dataset("mohanty/PlantVillage", "default", split="train")
        
        # Build class-to-idx mapping
        self.all_classes = self.hf_dataset.features['label'].names if 'label' in self.hf_dataset.features else self.hf_dataset.features['labels'].names
        self.class_to_idx = {cls: i for i, cls in enumerate(self.all_classes)}
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_path = row['image_path'] # format: hf://mohanty/PlantVillage/train/1234
        
        # Parse the index from the path
        hf_idx = int(image_path.split('/')[-1])
        
        # Access the image from the HF dataset object
        hf_record = self.hf_dataset[hf_idx]
        image = hf_record['image'].convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        label_idx = self.class_to_idx[row['class_label']]
        return image, label_idx

def get_transforms():
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])

def test_loader():
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "manifests", "development_train.csv")
    if not os.path.exists(manifest_path):
        print("Train manifest not found. Run prepare_hf_dataset.py first.")
        return
        
    transform = get_transforms()
    train_dataset = HFPlantVillageDataset(manifest_path, transform=transform)
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
