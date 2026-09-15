import os
import zipfile
import requests
from tqdm import tqdm
import shutil
import sys

URL = "https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "external")
ZIP_PATH = os.path.join(TARGET_DIR, "plantvillage_full.zip")
RAW_EXTRACT_DIR = os.path.join(TARGET_DIR, "plantvillage_raw")
FINAL_DIR = os.path.join(TARGET_DIR, "plantvillage")

def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    
    print(f"Downloading {url} to {dest_path}")
    with open(dest_path, 'wb') as file, tqdm(
        desc=os.path.basename(dest_path),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024*1024):
            size = file.write(data)
            bar.update(size)

def extract_and_cleanup():
    print(f"Extracting {ZIP_PATH} to {RAW_EXTRACT_DIR}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(path=RAW_EXTRACT_DIR)
    
    print("Finding 'color' directory...")
    color_src = None
    for root, dirs, files in os.walk(RAW_EXTRACT_DIR):
        if "color" in dirs:
            color_src = os.path.join(root, "color")
            break
            
    if not color_src:
        raise Exception("Could not find 'color' directory inside the extracted zip.")
        
    print(f"Moving {color_src} to {FINAL_DIR}...")
    if os.path.exists(FINAL_DIR):
        shutil.rmtree(FINAL_DIR)
    shutil.move(color_src, FINAL_DIR)
    
    print("Cleaning up temporary files...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    if os.path.exists(RAW_EXTRACT_DIR):
        try:
            shutil.rmtree(RAW_EXTRACT_DIR)
        except:
            pass # Windows file locking might sometimes block this, ignore
        
    print(f"Dataset successfully prepared at {FINAL_DIR}")

if __name__ == "__main__":
    print("=== PlantVillage Dataset Full Download ===")
    try:
        # Check if already exists
        if os.path.exists(FINAL_DIR) and len(os.listdir(FINAL_DIR)) > 10:
            print(f"Dataset already appears to be present at {FINAL_DIR}. Skipping download.")
            sys.exit(0)
            
        if not os.path.exists(ZIP_PATH):
            download_file(URL, ZIP_PATH)
        else:
            print(f"Found existing zip at {ZIP_PATH}. Skipping download.")
            
        extract_and_cleanup()
        
    except Exception as e:
        print(f"Error during dataset setup: {e}")
        print("Please follow data/DATASET_SETUP_WINDOWS.md to download manually.")
        sys.exit(1)
