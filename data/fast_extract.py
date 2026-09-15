import os
import zipfile
import shutil

TARGET_DIR = os.path.join(os.path.dirname(__file__), "external")
ZIP_PATH = os.path.join(TARGET_DIR, "plantvillage_full.zip")
RAW_EXTRACT_DIR = os.path.join(TARGET_DIR, "plantvillage_raw")
FINAL_DIR = os.path.join(TARGET_DIR, "plantvillage")

def extract_only_color():
    if not os.path.exists(ZIP_PATH):
        print(f"Error: {ZIP_PATH} not found.")
        return

    print("Cleaning up previous partial extraction...")
    if os.path.exists(RAW_EXTRACT_DIR):
        try:
            shutil.rmtree(RAW_EXTRACT_DIR)
        except Exception as e:
            print(f"Warning: could not delete {RAW_EXTRACT_DIR}: {e}")
            
    if os.path.exists(FINAL_DIR):
        try:
            shutil.rmtree(FINAL_DIR)
        except Exception as e:
            print(f"Warning: could not delete {FINAL_DIR}: {e}")

    print(f"Selectively extracting 'color' folder from {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        color_members = [f for f in zip_ref.namelist() if '/color/' in f or f.endswith('/color')]
        zip_ref.extractall(path=RAW_EXTRACT_DIR, members=color_members)
    
    print("Finding the extracted color directory...")
    color_src = None
    for root, dirs, files in os.walk(RAW_EXTRACT_DIR):
        if "color" in dirs:
            color_src = os.path.join(root, "color")
            break
            
    if not color_src:
        print("Error: Could not find 'color' directory after extraction.")
        return
        
    print(f"Moving {color_src} to {FINAL_DIR}...")
    shutil.move(color_src, FINAL_DIR)
    
    print("Cleaning up raw directory...")
    try:
        shutil.rmtree(RAW_EXTRACT_DIR)
    except:
        pass
        
    print(f"Extraction successfully completed at {FINAL_DIR}")

if __name__ == "__main__":
    extract_only_color()
