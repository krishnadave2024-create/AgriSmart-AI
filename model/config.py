import os

class Config:
    DATASET_NAME = "PlantVillage-Tiny-Sample"
    DATASET_TYPE = "DEVELOPMENT DATASET \u2014 NOT OFFICIAL SIH DATA"
    DATASET_SOURCE = "Wikimedia Commons / Pil Fallback"
    DATASET_LICENSE = "Public Domain / Creative Commons"
    OFFICIAL_TEST_AVAILABLE = False
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATASET_ROOT = os.path.join(BASE_DIR, "data", "external", "development_dataset")
    
    TRAIN_MANIFEST = os.path.join(BASE_DIR, "data", "manifests", "development_train.csv")
    VAL_MANIFEST = os.path.join(BASE_DIR, "data", "manifests", "development_validation.csv")
    
    CLASSES = ["Tomato___Bacterial_spot", "Tomato___healthy"]
    NUM_CLASSES = 2
    
    RANDOM_SEED = 42
    IMAGE_SIZE = (256, 256)
    SPLIT_RATIO = 0.8
    SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png"]
