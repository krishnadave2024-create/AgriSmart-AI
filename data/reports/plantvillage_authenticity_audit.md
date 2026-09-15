# PlantVillage Dataset Authenticity & Class Audit Report
**Date:** 2026-09-15 14:54:47

## 1. Dataset Provenance
- **Source Name**: PlantVillage Dataset (Color)
- **Source URL**: `https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip`
- **Local Path**: `D:\Internal_H\AgriSmart-AI\data\external\plantvillage`
- **License**: Public Domain / Open Access (as per official dataset release)

## 2. High-Level Summary
- **Total Images**: 54305
- **Total Classes**: 38
- **Total Crop Types**: 14
- **Total Disease/Healthy Types**: 21

## 3. Integrity Audit
The following integrity checks were performed on all files:
- **Corrupt Images**: 0
- **Zero-Byte Files**: 0
- **Non-Image Files**: 0
- **Exact Duplicates**: 21

**Duplicate Example**: D:\Internal_H\AgriSmart-AI\data\external\plantvillage\Apple___healthy\13298d36-4425-437d-ae8e-c7d70e200084___RS_HL 6271.JPG is identical to D:\Internal_H\AgriSmart-AI\data\external\plantvillage\Apple___healthy\11beda66-01e9-4bfd-be37-c0f8646d1478___RS_HL 6271.JPG

## 4. Class Distribution
| Class Name | Crop | Disease | Image Count |
|---|---|---|---|
| `Apple___Apple_scab` | Apple | Apple_scab | 630 |
| `Apple___Black_rot` | Apple | Black_rot | 621 |
| `Apple___Cedar_apple_rust` | Apple | Cedar_apple_rust | 275 |
| `Apple___healthy` | Apple | healthy | 1645 |
| `Blueberry___healthy` | Blueberry | healthy | 1502 |
| `Cherry_(including_sour)___Powdery_mildew` | Cherry_(including_sour) | Powdery_mildew | 1052 |
| `Cherry_(including_sour)___healthy` | Cherry_(including_sour) | healthy | 854 |
| `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | Corn_(maize) | Cercospora_leaf_spot Gray_leaf_spot | 513 |
| `Corn_(maize)___Common_rust_` | Corn_(maize) | Common_rust_ | 1192 |
| `Corn_(maize)___Northern_Leaf_Blight` | Corn_(maize) | Northern_Leaf_Blight | 985 |
| `Corn_(maize)___healthy` | Corn_(maize) | healthy | 1162 |
| `Grape___Black_rot` | Grape | Black_rot | 1180 |
| `Grape___Esca_(Black_Measles)` | Grape | Esca_(Black_Measles) | 1383 |
| `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | Grape | Leaf_blight_(Isariopsis_Leaf_Spot) | 1076 |
| `Grape___healthy` | Grape | healthy | 423 |
| `Orange___Haunglongbing_(Citrus_greening)` | Orange | Haunglongbing_(Citrus_greening) | 5507 |
| `Peach___Bacterial_spot` | Peach | Bacterial_spot | 2297 |
| `Peach___healthy` | Peach | healthy | 360 |
| `Pepper,_bell___Bacterial_spot` | Pepper,_bell | Bacterial_spot | 997 |
| `Pepper,_bell___healthy` | Pepper,_bell | healthy | 1478 |
| `Potato___Early_blight` | Potato | Early_blight | 1000 |
| `Potato___Late_blight` | Potato | Late_blight | 1000 |
| `Potato___healthy` | Potato | healthy | 152 |
| `Raspberry___healthy` | Raspberry | healthy | 371 |
| `Soybean___healthy` | Soybean | healthy | 5090 |
| `Squash___Powdery_mildew` | Squash | Powdery_mildew | 1835 |
| `Strawberry___Leaf_scorch` | Strawberry | Leaf_scorch | 1109 |
| `Strawberry___healthy` | Strawberry | healthy | 456 |
| `Tomato___Bacterial_spot` | Tomato | Bacterial_spot | 2127 |
| `Tomato___Early_blight` | Tomato | Early_blight | 1000 |
| `Tomato___Late_blight` | Tomato | Late_blight | 1909 |
| `Tomato___Leaf_Mold` | Tomato | Leaf_Mold | 952 |
| `Tomato___Septoria_leaf_spot` | Tomato | Septoria_leaf_spot | 1771 |
| `Tomato___Spider_mites Two-spotted_spider_mite` | Tomato | Spider_mites Two-spotted_spider_mite | 1676 |
| `Tomato___Target_Spot` | Tomato | Target_Spot | 1404 |
| `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | Tomato | Tomato_Yellow_Leaf_Curl_Virus | 5357 |
| `Tomato___Tomato_mosaic_virus` | Tomato | Tomato_mosaic_virus | 373 |
| `Tomato___healthy` | Tomato | healthy | 1591 |

## 5. Crop Breakdown
The dataset contains the following crops:
Apple, Blueberry, Cherry_(including_sour), Corn_(maize), Grape, Orange, Peach, Pepper,_bell, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato

## 6. Official SIH Status
> [!IMPORTANT]
> **This is NOT the official SIH held-out test dataset.** This is the public PlantVillage training dataset used to train the base model.

## Conclusion
The dataset has been completely downloaded, extracted, and audited. The dataset is **suitable for training** once any minor data cleaning (e.g., removing corrupt files if any) is performed in Phase 3.