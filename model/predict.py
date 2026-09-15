import os, sys, json
from pathlib import Path
from PIL import Image
import torch
import torch.nn.functional as F

from dataset import get_transforms
from train import build_model

# ─── CONFIG ──────────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).parent.parent
REGISTRY_PATH  = PROJECT_ROOT / "data" / "class_registry.json"
ARTIFACT_DIR   = PROJECT_ROOT / "model" / "artifacts" / "plant_disease_multiclass"
CHECKPOINT_PATH = ARTIFACT_DIR / "best_model.pth"
# ─────────────────────────────────────────────────────────────────────────────

class DiseasePredictor:
    def __init__(self):
        # Support loading Colab checkpoint during evaluation/testing
        checkpoint_path_env = os.environ.get('TEST_CHECKPOINT')
        ckpt_path = Path(checkpoint_path_env) if checkpoint_path_env else CHECKPOINT_PATH
        
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Missing checkpoint: {ckpt_path}. Cannot predict.")
            
        with open(REGISTRY_PATH, 'r') as f:
            self.registry = json.load(f)
            
        self.num_classes = len(self.registry)
        if self.num_classes != 38:
            raise ValueError(f"Incompatible registry: Expected 38 classes, found {self.num_classes}")
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        checkpoint = torch.load(ckpt_path, map_location=self.device)
        
        # Guard against old binary checkpoint
        ckpt_classes = checkpoint.get('num_classes', 0)
        if ckpt_classes == 0 and 'classes' in checkpoint:
            ckpt_classes = len(checkpoint['classes'])
        
        if ckpt_classes != 38:
            raise ValueError(f"Invalid checkpoint: Checkpoint has {ckpt_classes} classes, expected exactly 38. The old 2-class prototype is strictly forbidden.")
            
        self.model, self.arch = build_model(self.num_classes, self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        self.transform = get_transforms(is_train=False)
        
    def predict(self, image_path: str):
        image = Image.open(image_path).convert('RGB')
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = F.softmax(outputs, dim=1)[0]
            
        conf, pred_idx = torch.max(probs, 0)
        conf = conf.item()
        pred_idx = str(pred_idx.item())
        
        class_info = self.registry[pred_idx]
        
        return {
            "model_version": self.arch,
            "class_label": class_info['class_label'],
            "crop": class_info['crop'],
            "disease": class_info['disease'],
            "is_healthy": class_info['is_healthy'],
            "confidence": conf
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to image for prediction")
    args = parser.parse_args()
    
    predictor = DiseasePredictor()
    result = predictor.predict(args.image)
    print(json.dumps(result, indent=2))
