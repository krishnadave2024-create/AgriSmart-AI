import os, sys, json, time, random
from pathlib import Path
from collections import Counter
from dataset import get_dataloader
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.metrics import f1_score, accuracy_score

try:
    from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
    ARCH = "EfficientNet-B0"
except ImportError:
    from torchvision.models import resnet50, ResNet50_Weights
    ARCH = "ResNet-50"

from dataset import get_dataloader, PlantDiseaseDataset, get_transforms

# ─── CONFIG ──────────────────────────────────────────────────────────────────
RANDOM_SEED    = 42
BATCH_SIZE     = 32
NUM_EPOCHS     = 10
LEARNING_RATE  = 1e-3
PATIENCE       = 3         # early stopping patience
MIN_LR         = 1e-6
LR_PATIENCE    = 2         # ReduceLROnPlateau patience

PROJECT_ROOT   = Path(__file__).parent.parent
TRAIN_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "train.csv"
VAL_MANIFEST   = PROJECT_ROOT / "data" / "manifests" / "val.csv"
TEST_MANIFEST  = PROJECT_ROOT / "data" / "manifests" / "test.csv"
REGISTRY_PATH  = PROJECT_ROOT / "data" / "class_registry.json"

ARTIFACT_DIR   = PROJECT_ROOT / "model" / "artifacts" / "plant_disease_multiclass"
CHECKPOINT_NAME = "best_model.pth"
# ─────────────────────────────────────────────────────────────────────────────

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def build_model(num_classes: int, device: torch.device):
    try:
        model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        arch = "EfficientNet-B0"
    except Exception:
        model = resnet50(weights=ResNet50_Weights.DEFAULT)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        arch = "ResNet-50 (EfficientNet unavailable)"
    
    return model.to(device), arch

def compute_class_weights(train_df_path: str, num_classes: int, class_to_idx: dict, device: torch.device):
    df = pd.read_csv(train_df_path)
    counts = df['class_label'].value_counts()
    weights = torch.ones(num_classes)
    total = len(df)
    for cls, idx in class_to_idx.items():
        count = counts.get(cls, 1)
        weights[idx] = total / (num_classes * count)
    return weights.to(device)

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
    
    avg_loss = total_loss / (len(all_labels))
    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    return avg_loss, acc, macro_f1

def check_leakage(train_path, val_path, test_path):
    t = pd.read_csv(train_path)['file_hash']
    v = pd.read_csv(val_path)['file_hash']
    te = pd.read_csv(test_path)['file_hash']
    
    s1, s2, s3 = set(t), set(v), set(te)
    if s1.intersection(s2) or s1.intersection(s3) or s2.intersection(s3):
        raise ValueError("CRITICAL ERROR: Data Leakage Detected (overlapping hashes across splits). Stopping.")

def train(smoke_test=False):
    set_seed(RANDOM_SEED)
    
    # 1. Leakage Check & File Verification
    for m in [TRAIN_MANIFEST, VAL_MANIFEST, TEST_MANIFEST, REGISTRY_PATH]:
        if not m.exists():
            print(f"ERROR: File not found: {m}")
            sys.exit(1)
            
    check_leakage(TRAIN_MANIFEST, VAL_MANIFEST, TEST_MANIFEST)
    
    # 2. Load Registry
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    class_to_idx = {v['class_label']: v['index'] for v in registry.values()}
    num_classes = len(registry)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 3. Setup Dataloaders
    train_loader = get_dataloader(str(TRAIN_MANIFEST), batch_size=BATCH_SIZE, is_train=True)
    val_loader   = get_dataloader(str(VAL_MANIFEST), batch_size=BATCH_SIZE, is_train=False)
    test_loader  = get_dataloader(str(TEST_MANIFEST), batch_size=BATCH_SIZE, is_train=False)
    
    print("\n--- Training Configuration ---")
    print(f"Train Count: {len(train_loader.dataset)}")
    print(f"Validation Count: {len(val_loader.dataset)}")
    print(f"Test Count: {len(test_loader.dataset)}")
    print(f"Number of Classes: {num_classes}")
    print(f"Random Seed: {RANDOM_SEED}")
    print(f"Device: {device}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Learning Rate: {LEARNING_RATE}")
    print(f"Epochs: {NUM_EPOCHS} (Smoke Test: {smoke_test})")
    
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_path = ARTIFACT_DIR / CHECKPOINT_NAME
    print(f"Checkpoint Path: {checkpoint_path}")
    print("------------------------------\n")
    
    # 4. Model and Optimizers
    model, arch = build_model(num_classes, device)
    
    # Class imbalance handling
    class_weights = compute_class_weights(str(TRAIN_MANIFEST), num_classes, class_to_idx, device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=LR_PATIENCE, min_lr=MIN_LR)
    
    # 5. Training Loop
    best_val_f1 = 0.0
    best_epoch = 0
    patience_counter = 0
    history = []
    start_time = time.time()
    
    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        train_loss = 0.0
        
        batch_times = []
        
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            b_start = time.time()
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * inputs.size(0)
            
            b_end = time.time()
            batch_times.append(b_end - b_start)
            
            if batch_idx % 10 == 0:
                print(f"  Epoch {epoch} | Batch {batch_idx}/{len(train_loader)} | Loss: {loss.item():.4f}")
                
            if smoke_test and batch_idx >= 1:
                print("Smoke test: stopping after 2 batches.")
                break
                
            if not torch.cuda.is_available() and batch_idx >= 5:
                # If on CPU, we can project the time.
                avg_b_time = sum(batch_times) / len(batch_times)
                proj_time = avg_b_time * len(train_loader) / 60
                print(f"\n[HARDWARE LIMITATION DETECTED]")
                print(f"Training on CPU. Average batch time: {avg_b_time:.2f}s.")
                print(f"Projected time per epoch: {proj_time:.1f} minutes.")
                if proj_time > 30:
                    print(f"Projected training time is too slow (>30 min/epoch). Aborting full training to prevent freezing.")
                    sys.exit(3)
        
        train_loss /= len(train_loader.dataset)
        
        # Validation
        print("  Evaluating on validation set...")
        val_loss, val_acc, val_macro_f1 = evaluate_epoch(model, val_loader, criterion, device, smoke_test)
        scheduler.step(val_macro_f1)
        
        epoch_record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_loss": round(val_loss, 4),
            "val_accuracy": round(val_acc, 4),
            "val_macro_f1": round(val_macro_f1, 4),
            "lr": optimizer.param_groups[0]['lr'],
        }
        history.append(epoch_record)
        
        print(f"Epoch {epoch:02d}/{NUM_EPOCHS} | TrainLoss={train_loss:.4f} | ValLoss={val_loss:.4f} | ValAcc={val_acc:.4f} | ValF1={val_macro_f1:.4f} | LR={optimizer.param_groups[0]['lr']:.2e}")
        
        if val_macro_f1 > best_val_f1:
            best_val_f1 = val_macro_f1
            best_epoch = epoch
            patience_counter = 0
            torch.save({
                'model_state_dict': model.state_dict(),
                'architecture': arch,
                'epoch': epoch,
                'num_classes': num_classes,
                'val_macro_f1': val_macro_f1,
            }, checkpoint_path)
            print(f"  ✓ New best model saved")
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"\nEarly stopping: no improvement for {PATIENCE} epochs.")
                break
                
        if smoke_test:
            break
            
    elapsed = time.time() - start_time
    print(f"\nTraining complete in {elapsed:.0f}s")
    
    with open(ARTIFACT_DIR / "training_history.json", 'w') as f:
        json.dump(history, f, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true", help="Run a 2-batch smoke test")
    args = parser.parse_args()
    train(smoke_test=args.smoke_test)
