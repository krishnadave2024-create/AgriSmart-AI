"""
Phase 6 — Multi-Crop Disease Detection: Dataset & Transforms
=============================================================
Replaces the old binary dataset.py with a proper multi-class dataset.
"""

import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms

# ImageNet statistics — used for transfer learning from pretrained weights
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
IMAGE_SIZE = 224  # EfficientNet-B0 default


import json

class PlantDiseaseDataset(Dataset):
    """
    Multi-class plant disease dataset loaded from a CSV manifest.
    
    Manifest must have columns: relative_path, class_label
    relative_path must be relative to project root.
    """
    def __init__(self, manifest_path: str, transform=None):
        self.df = pd.read_csv(manifest_path)
        self.transform = transform
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        registry_path = os.path.join(self.project_root, "data", "class_registry.json")
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            
        # Create mappings from the authoritative registry
        self.class_to_idx = {v['class_label']: v['index'] for v in registry.values()}
        self.idx_to_class = {v['index']: v['class_label'] for v in registry.values()}
        self.all_classes = [self.idx_to_class[i] for i in range(len(self.idx_to_class))]
        
        # Validate all paths exist
        missing = []
        for _, row in self.df.iterrows():
            full_path = os.path.join(self.project_root, "data", row['relative_path'])
            if not os.path.exists(full_path):
                missing.append(row['relative_path'])
        if missing:
            print(f"WARNING: {len(missing)} images not found (first 3: {missing[:3]})")
            
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        full_path = os.path.join(self.project_root, "data", row['relative_path'])
        
        try:
            image = Image.open(full_path).convert('RGB')
        except Exception as e:
            # Return a black image if file is corrupt — will be flagged in training
            image = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), color=(0, 0, 0))
        
        if self.transform:
            image = self.transform(image)
            
        label_idx = self.class_to_idx[row['class_label']]
        return image, label_idx


def get_transforms(is_train: bool = True) -> transforms.Compose:
    """
    Returns image transforms for training or evaluation.
    
    Training: realistic augmentations that don't destroy disease characteristics.
    Evaluation: deterministic resize + normalize only.
    
    Disease-safe augmentation rationale:
    - Horizontal flip: safe (disease spots appear on either side)
    - Vertical flip: safe (same reasoning)
    - Color jitter (mild): safe (accounts for lighting variation)
    - Random rotation (±15°): safe (disease visible at any orientation)
    - Random crop: safe (simulates partial leaf photos)
    AVOIDED:
    - Heavy colour shifts (would destroy disease colour cues)
    - Heavy blur (hides disease texture)
    - Aggressive crops (might remove disease regions)
    """
    if is_train:
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),  # slightly larger for crop
            transforms.RandomCrop(IMAGE_SIZE),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.02),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])


def get_dataloader(manifest_path: str,
                   batch_size: int = 32, is_train: bool = True,
                   num_workers: int = 0) -> DataLoader:
    transform = get_transforms(is_train=is_train)
    dataset = PlantDiseaseDataset(manifest_path, transform=transform)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=is_train,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
