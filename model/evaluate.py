import os
import torch
import torch.nn as nn
from torchvision.models import resnet18
from dataset import get_dataloader
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import matplotlib.pyplot as plt
import numpy as np

def evaluate():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_manifest = os.path.join(project_root, "data", "manifests", "development_test.csv")
    chkpt_path = os.path.join(project_root, "model", "checkpoints", "baseline_resnet18.pth")
    
    if not os.path.exists(test_manifest) or not os.path.exists(chkpt_path):
        print("Manifest or checkpoint not found.")
        return
        
    checkpoint = torch.load(chkpt_path, weights_only=False)
    classes = checkpoint['classes']
    num_classes = len(classes)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = resnet18()
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    test_loader = get_dataloader(test_manifest, batch_size=4, is_train=False)
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    # Calculate metrics
    acc = accuracy_score(all_labels, all_preds)
    macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    report = classification_report(all_labels, all_preds, target_names=classes, zero_division=0)
    cm = confusion_matrix(all_labels, all_preds)
    
    # Save text report
    report_dir = os.path.join(project_root, "data", "reports")
    os.makedirs(report_dir, exist_ok=True)
    
    with open(os.path.join(report_dir, "baseline_evaluation_report.md"), "w") as f:
        f.write("# Baseline Evaluation Report\n")
        f.write("**Important: This is preliminary development data only. Not for final SIH evaluation.**\n\n")
        f.write(f"- **Test Samples**: {len(test_loader.dataset)}\n")
        f.write(f"- **Accuracy**: {acc:.4f}\n")
        f.write(f"- **Macro-F1**: {macro_f1:.4f}\n\n")
        f.write("## Per-Class Metrics\n```text\n")
        f.write(report)
        f.write("\n```\n")
        f.write("## Confusion Matrix\n")
        f.write(str(cm))
        f.write("\n")
        
    print(f"Accuracy: {acc:.4f} | Macro-F1: {macro_f1:.4f}")
    
    # Save CM plot
    fig, ax = plt.subplots()
    cax = ax.matshow(cm, cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    fig.colorbar(cax)
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, str(cm[i, j]), va='center', ha='center')
            
    plt.savefig(os.path.join(report_dir, "confusion_matrix.png"))
    print(f"Evaluation complete. Reports saved to {report_dir}")

if __name__ == "__main__":
    evaluate()
