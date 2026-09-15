# Phase 3: Dataset Cleaning and Splits Report

## 1. High-Level Summary
- **Raw Image Count**: 54305
- **Cleaned Image Count**: 54284
- **Exact Duplicates Excluded**: 21
- **Invalid Images Excluded**: 0
- **Total Classes**: 38
- **Total Crops**: 14 (derived from class list)

## 2. Split Strategy
- **Random Seed**: `42` (Fixed)
- **Method**: Stratified Split (Deterministic by Relative Path)
- **Target Ratios**: 70% Train / 15% Validation / 15% Test

### Split Results
- **Train**: 37982 images (70.0%)
- **Validation**: 8126 images (15.0%)
- **Test**: 8176 images (15.1%)

## 3. Leakage Validation
The following absolute safeguards guarantee no data leakage:
1. **Duplicate Exclusion**: All exact duplicate images were completely removed from the clean manifest before splitting. Each image belongs to a unique hash group of size 1.
2. **Hash Validation**: A strict set-intersection validation checked MD5 hashes across `train.csv`, `val.csv`, and `test.csv`.
3. **Result**: ALL LEAKAGE CHECKS PASSED. No overlapping hashes exist across any splits.

## 4. SIH Held-out Test Status
> [!IMPORTANT]
> **CONFIRMATION**: The official SIH held-out test dataset was NOT used in any capacity during cleaning, splitting, tuning, or training. Only the public PlantVillage dataset was processed.

## 5. Per-Class Split Distribution
| Class Name | Cleaned Total | Train | Validation | Test |
|---|---|---|---|---|
| `Apple___Apple_scab` | 630 | 441 | 94 | 95 |
| `Apple___Black_rot` | 621 | 434 | 93 | 94 |
| `Apple___Cedar_apple_rust` | 275 | 192 | 41 | 42 |
| `Apple___healthy` | 1638 | 1146 | 245 | 247 |
| `Blueberry___healthy` | 1502 | 1051 | 225 | 226 |
| `Cherry_(including_sour)___Powdery_mildew` | 1052 | 736 | 157 | 159 |
| `Cherry_(including_sour)___healthy` | 854 | 597 | 128 | 129 |
| `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | 513 | 359 | 76 | 78 |
| `Corn_(maize)___Common_rust_` | 1192 | 834 | 178 | 180 |
| `Corn_(maize)___Northern_Leaf_Blight` | 985 | 689 | 147 | 149 |
| `Corn_(maize)___healthy` | 1162 | 813 | 174 | 175 |
| `Grape___Black_rot` | 1180 | 826 | 177 | 177 |
| `Grape___Esca_(Black_Measles)` | 1383 | 968 | 207 | 208 |
| `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | 1076 | 753 | 161 | 162 |
| `Grape___healthy` | 423 | 296 | 63 | 64 |
| `Orange___Haunglongbing_(Citrus_greening)` | 5507 | 3854 | 826 | 827 |
| `Peach___Bacterial_spot` | 2297 | 1607 | 344 | 346 |
| `Peach___healthy` | 360 | 251 | 54 | 55 |
| `Pepper,_bell___Bacterial_spot` | 997 | 697 | 149 | 151 |
| `Pepper,_bell___healthy` | 1478 | 1034 | 221 | 223 |
| `Potato___Early_blight` | 1000 | 700 | 150 | 150 |
| `Potato___Late_blight` | 1000 | 700 | 150 | 150 |
| `Potato___healthy` | 152 | 106 | 22 | 24 |
| `Raspberry___healthy` | 371 | 259 | 55 | 57 |
| `Soybean___healthy` | 5090 | 3563 | 763 | 764 |
| `Squash___Powdery_mildew` | 1835 | 1284 | 275 | 276 |
| `Strawberry___Leaf_scorch` | 1109 | 776 | 166 | 167 |
| `Strawberry___healthy` | 456 | 319 | 68 | 69 |
| `Tomato___Bacterial_spot` | 2127 | 1488 | 319 | 320 |
| `Tomato___Early_blight` | 1000 | 700 | 150 | 150 |
| `Tomato___Late_blight` | 1901 | 1330 | 285 | 286 |
| `Tomato___Leaf_Mold` | 952 | 666 | 142 | 144 |
| `Tomato___Septoria_leaf_spot` | 1771 | 1239 | 265 | 267 |
| `Tomato___Spider_mites Two-spotted_spider_mite` | 1676 | 1173 | 251 | 252 |
| `Tomato___Target_Spot` | 1404 | 982 | 210 | 212 |
| `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | 5357 | 3749 | 803 | 805 |
| `Tomato___Tomato_mosaic_virus` | 373 | 261 | 55 | 57 |
| `Tomato___healthy` | 1585 | 1109 | 237 | 239 |