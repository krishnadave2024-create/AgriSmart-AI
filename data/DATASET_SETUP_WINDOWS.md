# Dataset Setup Guide for Windows

If the automated dataset download script (`data/download_full_plantvillage.py`) fails due to network timeouts or other issues, follow these instructions to download and extract the dataset manually.

## 1. Download the Dataset
1. Open your web browser.
2. Navigate to the official Hugging Face repository for PlantVillage:
   [https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip](https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip)
3. The download will start automatically. The file size is approximately **2.03 GB**.

## 2. Place the Archive
1. Once downloaded, move `data.zip` into the following directory within this project:
   `AgriSmart-AI/data/external/`
2. If the `external` folder does not exist, create it.

## 3. Extract the Dataset
1. Right-click on `data.zip` and select **Extract All...**
2. Extract it directly into `AgriSmart-AI/data/external/plantvillage_raw/`.
3. Open the extracted folder and locate the `color/` directory (it may be nested inside a few folders).
4. Move the `color/` directory directly into `AgriSmart-AI/data/external/` and rename it to `plantvillage`.
5. The final structure MUST look exactly like this:
   ```text
   AgriSmart-AI/
   ├── data/
   │   ├── external/
   │   │   ├── plantvillage/
   │   │   │   ├── Tomato___healthy/
   │   │   │   ├── Tomato___Bacterial_spot/
   │   │   │   └── ... (other crop-disease folders)
   ```

## 4. Verify and Clean Up
1. Verify that the `plantvillage` folder contains 38 subdirectories (one for each crop/disease combination).
2. Delete the downloaded `data.zip` file and the `plantvillage_raw` folder to free up space.

## 5. Continue the Pipeline
Once extracted, you can safely continue the pipeline by running the preparation scripts.
