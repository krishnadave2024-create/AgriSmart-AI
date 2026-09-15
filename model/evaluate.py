import os, sys, json
from pathlib import Path
import pandas as pd
import numpy as np
import torch
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, confusion_matrix

from dataset import get_dataloader
from train import build_model, BATCH_SIZE

# ─── CONFIG ──────────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).parent.parent
TEST_MANIFEST  = PROJECT_ROOT / "data" / "manifests" / "test.csv"
REGISTRY_PATH  = PROJECT_ROOT / "data" / "class_registry.json"
ARTIFACT_DIR   = PROJECT_ROOT / "model" / "artifacts" / "plant_disease_multiclass"
CHECKPOINT_PATH = ARTIFACT_DIR / "best_model.pth"
# ─────────────────────────────────────────────────────────────────────────────

def evaluate():
    print("=" * 60)
    print("Evaluating Model on Held-out Test Set")
    print("=" * 60)
    
    checkpoint_path_env = os.environ.get('TEST_CHECKPOINT')
    ckpt_path = Path(checkpoint_path_env) if checkpoint_path_env else CHECKPOINT_PATH
    
    if not ckpt_path.exists():
        print(f"ERROR: Checkpoint not found at {ckpt_path}")
        sys.exit(1)
        
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    num_classes = len(registry)
    
    # In python 3.7+ dicts maintain insertion order, but we should sort to be safe
    class_labels = [registry[str(i)]['class_label'] for i in range(num_classes)]
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"Loading checkpoint...")
    checkpoint = torch.load(ckpt_path, map_location=device)
    model, arch = build_model(num_classes, device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"Loading test dataset...")
    test_loader = get_dataloader(str(TEST_MANIFEST), batch_size=BATCH_SIZE, is_train=False)
    
    all_preds, all_labels = [], []
    
    print(f"Running inference on {len(test_loader.dataset)} test images...")
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    # Metrics
    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    weighted_f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    precisions = precision_score(all_labels, all_preds, average=None, zero_division=0)
    recalls = recall_score(all_labels, all_preds, average=None, zero_division=0)
    f1s = f1_score(all_labels, all_preds, average=None, zero_division=0)
    
    cm = confusion_matrix(all_labels, all_preds)
    
    print("\n--- Test Results ---")
    print(f"Accuracy:    {acc:.4f}")
    print(f"Macro F1:    {macro_f1:.4f}")
    print(f"Weighted F1: {weighted_f1:.4f}")
    
    # Save Metrics
    metrics_json = {
        "architecture": arch,
        "test_images": len(all_labels),
        "classes": num_classes,
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4)
    }
    with open(ARTIFACT_DIR / "metrics.json", 'w') as f:
        json.dump(metrics_json, f, indent=4)
        
    # Save Per-class metrics
    per_class_df = pd.DataFrame({
        'class_label': class_labels,
        'precision': np.round(precisions, 4),
        'recall': np.round(recalls, 4),
        'f1_score': np.round(f1s, 4)
    })
    per_class_df.to_csv(ARTIFACT_DIR / "per_class_metrics.csv", index=False)
    
    # Save Confusion Matrix
    cm_df = pd.DataFrame(cm, index=class_labels, columns=class_labels)
    cm_df.to_csv(ARTIFACT_DIR / "confusion_matrix.csv")
    
    print(f"\nArtifacts saved to {ARTIFACT_DIR}")

if __name__ == "__main__":
    evaluate()
