import os, sys, json, time, argparse, random
from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
from sklearn.metrics import f1_score, accuracy_score

from dataset import get_dataloader, PlantDiseaseDataset, get_transforms

def parse_args():
    parser = argparse.ArgumentParser(description="Fast GPU Training for Colab")
    parser.add_argument("--data-root", type=str, required=True, help="Path to raw image dir")
    parser.add_argument("--train-manifest", type=str, required=True)
    parser.add_argument("--val-manifest", type=str, required=True)
    parser.add_argument("--test-manifest", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--architecture", type=str, default="efficientnet_b0")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=str, default="auto")
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--max-training-minutes", type=float, default=40.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--smoke-test", action="store_true", help="Run 2 batches only")
    return parser.parse_args()

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def build_model(arch, num_classes, device):
    if arch.lower() == "efficientnet_b0":
        try:
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
            arch_name = "EfficientNet-B0"
        except ImportError:
            arch = "resnet18"
    if arch.lower() == "resnet18" or arch.lower() == "resnet50":
        from torchvision.models import resnet18, ResNet18_Weights, resnet50, ResNet50_Weights
        if arch.lower() == "resnet18":
            model = resnet18(weights=ResNet18_Weights.DEFAULT)
            arch_name = "ResNet-18"
        else:
            model = resnet50(weights=ResNet50_Weights.DEFAULT)
            arch_name = "ResNet-50"
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        
    return model.to(device), arch_name

def evaluate_epoch(model, loader, criterion, device, smoke_test=False):
    model.eval()
    all_preds, all_labels = [], []
    total_loss = 0.0
    
    with torch.no_grad():
        for batch_idx, (inputs, labels) in enumerate(loader):
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * inputs.size(0)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            if smoke_test and batch_idx >= 1: break
            
    avg_loss = total_loss / len(all_labels)
    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    return avg_loss, acc, macro_f1

def main():
    args = parse_args()
    set_seed(args.seed)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("=" * 60)
    print("AgriSmart AI - Fast GPU Training")
    print("=" * 60)
    print(f"CUDA Available:  {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Name:        {torch.cuda.get_device_name(0)}")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"Random Seed:     {args.seed}")
    
    # Verify dataset counts
    train_df = pd.read_csv(args.train_manifest)
    val_df = pd.read_csv(args.val_manifest)
    test_df = pd.read_csv(args.test_manifest)
    
    registry_path = os.path.join(os.path.dirname(args.train_manifest), "..", "class_registry.json")
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    num_classes = len(registry)
    
    print(f"\nTarget Arch:     {args.architecture}")
    print(f"Classes:         {num_classes}")
    print(f"Train/Val/Test:  {len(train_df)} / {len(val_df)} / {len(test_df)}")
    print(f"Learning Rate:   {args.learning_rate}")
    print(f"Epoch Limit:     {args.epochs}")
    print(f"Time Limit:      {args.max_training_minutes} minutes")
    print("-" * 60)
    
    batch_size = 128 if args.batch_size == "auto" and torch.cuda.is_available() else (32 if args.batch_size == "auto" else int(args.batch_size))
    print(f"Selected Batch Size: {batch_size}")
    
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup data
    train_loader = get_dataloader(args.train_manifest, batch_size=batch_size, is_train=True, num_workers=args.num_workers)
    val_loader   = get_dataloader(args.val_manifest, batch_size=batch_size, is_train=False, num_workers=args.num_workers)
    
    model, arch_name = build_model(args.architecture, num_classes, device)
    
    # Class weights
    counts = train_df['class_label'].value_counts()
    class_to_idx = {v['class_label']: v['index'] for v in registry.values()}
    weights = torch.ones(num_classes)
    for cls, idx in class_to_idx.items():
        weights[idx] = len(train_df) / (num_classes * counts.get(cls, 1))
    criterion = nn.CrossEntropyLoss(weight=weights.to(device))
    
    optimizer = optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=1e-4)
    scaler = GradScaler(enabled=torch.cuda.is_available())
    
    best_val_f1 = 0.0
    history = []
    
    start_time = time.time()
    time_limit_seconds = args.max_training_minutes * 60
    
    print("\nStarting Training Loop...")
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            # Check time limit safely
            if (time.time() - start_time) > time_limit_seconds:
                print(f"\n[TIME LIMIT REACHED] Stopping training gracefully at {args.max_training_minutes} min.")
                break
                
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            
            with autocast(enabled=torch.cuda.is_available()):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            train_loss += loss.item() * inputs.size(0)
            
            if args.smoke_test and batch_idx >= 1:
                print("Smoke test: stopping batch loop.")
                break
                
        # Time check break
        if (time.time() - start_time) > time_limit_seconds and batch_idx < len(train_loader) - 1:
            break
            
        train_loss /= (batch_idx + 1) * batch_size
        
        print(f"  Evaluating Epoch {epoch}...")
        val_loss, val_acc, val_macro_f1 = evaluate_epoch(model, val_loader, criterion, device, smoke_test=args.smoke_test)
        
        history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_acc, 4),
            "val_macro_f1": round(val_macro_f1, 4)
        })
        
        print(f"Epoch {epoch:02d}/{args.epochs} | TrainLoss={train_loss:.4f} | ValLoss={val_loss:.4f} | ValAcc={val_acc:.4f} | ValF1={val_macro_f1:.4f}")
        
        if val_macro_f1 >= best_val_f1:
            best_val_f1 = val_macro_f1
            torch.save({
                'model_state_dict': model.state_dict(),
                'architecture': arch_name,
                'epoch': epoch,
                'num_classes': num_classes,
                'val_macro_f1': val_macro_f1
            }, out_dir / "best_model.pth")
            print(f"  [OK] Best model saved.")
            
        if args.smoke_test:
            break
            
    print(f"\nTraining finished in {time.time() - start_time:.0f}s. Best Val F1: {best_val_f1:.4f}")
    with open(out_dir / "training_history.json", 'w') as f:
        json.dump(history, f, indent=2)
        
    print(f"Checkpoints and history saved to {out_dir}")

if __name__ == "__main__":
    main()
