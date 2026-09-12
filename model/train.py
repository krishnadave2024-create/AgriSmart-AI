import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.models import resnet18, ResNet18_Weights
from dataset import get_dataloader

def train():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_manifest = os.path.join(project_root, "data", "manifests", "development_train.csv")
    val_manifest = os.path.join(project_root, "data", "manifests", "development_validation.csv")
    
    if not os.path.exists(train_manifest):
        print(f"Error: Manifest {train_manifest} not found.")
        return
        
    train_loader = get_dataloader(train_manifest, batch_size=4, is_train=True)
    val_loader = get_dataloader(val_manifest, batch_size=4, is_train=False)
    
    dataset = train_loader.dataset
    num_classes = len(dataset.all_classes)
    
    print("--- Training Safety Pre-checks ---")
    print(f"Train samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")
    print(f"Classes ({num_classes}): {dataset.all_classes}")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    try:
        model = resnet18(weights=ResNet18_Weights.DEFAULT)
    except Exception as e:
        print(f"Error downloading pretrained weights: {e}")
        return
        
    # Modify last layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model = model.to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    print("----------------------------------\n")
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 2
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * inputs.size(0)
            
        train_loss = train_loss / len(train_loader.dataset)
        
        model.eval()
        val_loss = 0.0
        correct = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                correct += torch.sum(preds == labels.data)
                
        val_loss = val_loss / len(val_loader.dataset)
        val_acc = correct.double() / len(val_loader.dataset)
        
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
    chkpt_dir = os.path.join(project_root, "model", "checkpoints")
    os.makedirs(chkpt_dir, exist_ok=True)
    
    # Save the model
    torch.save({
        'model_state_dict': model.state_dict(),
        'classes': dataset.all_classes
    }, os.path.join(chkpt_dir, "baseline_resnet18.pth"))
    
    print(f"Training completed. Model saved to {chkpt_dir}/baseline_resnet18.pth")

if __name__ == "__main__":
    train()
