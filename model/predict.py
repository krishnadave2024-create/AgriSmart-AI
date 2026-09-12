import os
import argparse
import torch
import torch.nn as nn
from torchvision.models import resnet18
from PIL import Image
from dataset import get_transforms

def predict(image_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chkpt_path = os.path.join(project_root, "model", "checkpoints", "baseline_resnet18.pth")
    
    if not os.path.exists(chkpt_path):
        raise FileNotFoundError(f"Model checkpoint missing at {chkpt_path}. Run training first.")
        
    checkpoint = torch.load(chkpt_path, weights_only=False, map_location=torch.device('cpu'))
    classes = checkpoint['classes']
    num_classes = len(classes)
    
    model = resnet18()
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    transform = get_transforms(is_train=False)
    
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        raise ValueError(f"Failed to open image at {image_path}: {e}")
        
    img_tensor = transform(img).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(img_tensor)
        _, preds = torch.max(outputs, 1)
        
    return classes[preds.item()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict crop disease from image")
    parser.add_argument("--image", type=str, required=True, help="Path to the image file")
    args = parser.parse_args()
    
    try:
        label = predict(args.image)
        print(f"Prediction for {args.image}: {label}")
        print("Note: This is a baseline development model, not production-ready.")
    except Exception as e:
        print(f"Error: {e}")
