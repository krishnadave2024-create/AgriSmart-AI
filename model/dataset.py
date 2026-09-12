import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms

class PlantDiseaseDataset(Dataset):
    def __init__(self, manifest_path, transform=None):
        self.df = pd.read_csv(manifest_path)
        self.transform = transform
        
        self.all_classes = sorted(self.df['class_label'].unique().tolist())
        self.class_to_idx = {cls: i for i, cls in enumerate(self.all_classes)}
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_path = row['image_path']
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(project_root, image_path)
        
        image = Image.open(full_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        label_idx = self.class_to_idx[row['class_label']]
        return image, label_idx

def get_transforms(is_train=True):
    if is_train:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    else:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

def get_dataloader(manifest_path, batch_size=4, is_train=True):
    transform = get_transforms(is_train=is_train)
    dataset = PlantDiseaseDataset(manifest_path, transform=transform)
    return DataLoader(dataset, batch_size=batch_size, shuffle=is_train)
