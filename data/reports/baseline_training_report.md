# Baseline Training Report

**Important: This is preliminary development data only. Not for final SIH evaluation.**

## Pre-checks
- **Train samples**: 70
- **Validation samples**: 15
- **Classes**: 2 ('diseased', 'healthy')
- **Model**: ResNet18 (Pretrained)
- **Total parameters**: 11,177,538

## Training Logs
- **Epoch 1/2**: Train Loss: 1.0926 | Val Loss: 28.8621 | Val Acc: 0.4667
- **Epoch 2/2**: Train Loss: 0.3960 | Val Loss: 0.1947 | Val Acc: 0.9333

Model successfully saved to `model/checkpoints/baseline_resnet18.pth`.
