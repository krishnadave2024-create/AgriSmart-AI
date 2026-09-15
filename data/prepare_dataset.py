"""
Phase 3 — Dataset Preparation Pipeline
=======================================
Validates, deduplicates, normalises labels, and generates manifests 
from downloaded PlantVillage images.

Usage:
    python data/prepare_dataset.py

Outputs:
    data/processed/<ClassName>/<image>.jpg
    data/manifests/plantvillage_full.csv
    data/reports/preparation_report.md
"""

import os, sys, json, hashlib, shutil
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "external" / "plantvillage" / "color"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"
REPORT_DIR = PROJECT_ROOT / "data" / "reports"

# ── Class Taxonomy (Phase 5) ─────────────────────────────────────────────────
# Maps PlantVillage directory name → (crop_name, disease_name, health_status, class_label)
CLASS_TAXONOMY = {
    # Tomato
    "Tomato___Bacterial_spot":              ("Tomato", "Bacterial Spot",           "diseased", "Tomato___Bacterial_spot"),
    "Tomato___Early_blight":               ("Tomato", "Early Blight",             "diseased", "Tomato___Early_blight"),
    "Tomato___Late_blight":                ("Tomato", "Late Blight",              "diseased", "Tomato___Late_blight"),
    "Tomato___Leaf_Mold":                  ("Tomato", "Leaf Mold",               "diseased", "Tomato___Leaf_Mold"),
    "Tomato___Septoria_leaf_spot":         ("Tomato", "Septoria Leaf Spot",       "diseased", "Tomato___Septoria_leaf_spot"),
    "Tomato___Spider_mites Two-spotted_spider_mite": ("Tomato", "Spider Mites",   "diseased", "Tomato___Spider_mites"),
    "Tomato___Target_Spot":                ("Tomato", "Target Spot",              "diseased", "Tomato___Target_Spot"),
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": ("Tomato", "Yellow Leaf Curl Virus","diseased", "Tomato___Tomato_Yellow_Leaf_Curl_Virus"),
    "Tomato___Tomato_mosaic_virus":        ("Tomato", "Mosaic Virus",             "diseased", "Tomato___Tomato_mosaic_virus"),
    "Tomato___healthy":                    ("Tomato", None,                       "healthy",  "Tomato___healthy"),
    # Corn/Maize
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": ("Corn", "Gray Leaf Spot", "diseased", "Corn___Gray_leaf_spot"),
    "Corn_(maize)___Common_rust_":         ("Corn", "Common Rust",               "diseased", "Corn___Common_rust"),
    "Corn_(maize)___Northern_Leaf_Blight": ("Corn", "Northern Leaf Blight",      "diseased", "Corn___Northern_Leaf_Blight"),
    "Corn_(maize)___healthy":              ("Corn", None,                         "healthy",  "Corn___healthy"),
    # Potato
    "Potato___Early_blight":              ("Potato", "Early Blight",             "diseased", "Potato___Early_blight"),
    "Potato___Late_blight":               ("Potato", "Late Blight",              "diseased", "Potato___Late_blight"),
    "Potato___healthy":                   ("Potato", None,                        "healthy",  "Potato___healthy"),
    # Pepper
    "Pepper,_bell___Bacterial_spot":      ("Pepper", "Bacterial Spot",           "diseased", "Pepper___Bacterial_spot"),
    "Pepper,_bell___healthy":             ("Pepper", None,                        "healthy",  "Pepper___healthy"),
}

SUPPORTED_CROPS = sorted(set(v[0] for v in CLASS_TAXONOMY.values()))
SUPPORTED_CLASS_LABELS = sorted(set(v[3] for v in CLASS_TAXONOMY.values()))


def md5_hash(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_image(path: Path) -> tuple:
    """Returns (is_valid, width, height, error_msg)"""
    try:
        with Image.open(path) as img:
            w, h = img.size
            if w < 32 or h < 32:
                return False, w, h, f"Too small: {w}x{h}"
            img.verify()  # checks for corruption
        return True, w, h, ""
    except Exception as e:
        return False, 0, 0, str(e)[:100]


def prepare():
    print("=" * 60)
    print("Phase 3: Dataset Preparation")
    print("=" * 60)

    if not RAW_DIR.exists():
        print(f"ERROR: Raw data directory not found: {RAW_DIR}")
        print("Please run: python data/bulk_download_plantvillage.py")
        sys.exit(1)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    hashes_seen = {}   # hash → first path (for duplicate detection)
    corrupt = []
    duplicates = []
    missing_classes = []
    class_counts = Counter()

    for pv_dir_name, (crop, disease, health_status, class_label) in CLASS_TAXONOMY.items():
        src_dir = RAW_DIR / pv_dir_name
        dst_dir = PROCESSED_DIR / class_label

        if not src_dir.exists():
            missing_classes.append(pv_dir_name)
            print(f"  MISSING: {pv_dir_name}")
            continue

        dst_dir.mkdir(parents=True, exist_ok=True)
        images = sorted([p for p in src_dir.iterdir()
                         if p.suffix.lower() in ('.jpg', '.jpeg', '.png')])

        print(f"\n  Processing {pv_dir_name} ({len(images)} images)...")

        for img_path in images:
            # Validate
            is_valid, w, h, err = validate_image(img_path)
            if not is_valid:
                corrupt.append(str(img_path))
                continue

            # Hash for duplicate detection
            img_hash = md5_hash(img_path)
            if img_hash in hashes_seen:
                duplicates.append((str(img_path), hashes_seen[img_hash]))
                continue
            hashes_seen[img_hash] = str(img_path)

            # Copy to processed
            dst_path = dst_dir / img_path.name
            if not dst_path.exists():
                shutil.copy2(img_path, dst_path)

            # Relative paths for manifest portability
            rel_path = str(dst_path.relative_to(PROJECT_ROOT)).replace('\\', '/')

            records.append({
                'image_path': rel_path,
                'crop_name': crop,
                'disease_name': disease if disease else 'healthy',
                'health_status': health_status,
                'class_label': class_label,
                'source_dataset': 'mohanty/PlantVillage',
                'source_license': 'CC-BY-SA 3.0',
                'image_hash': img_hash,
                'original_dir': pv_dir_name,
            })
            class_counts[class_label] += 1

        print(f"    → {class_counts[class_label]} valid unique images")

    if not records:
        print("\nERROR: No valid images found. Cannot proceed.")
        print("Check that the download has completed.")
        sys.exit(1)

    # Save full manifest
    df = pd.DataFrame(records)
    full_manifest = MANIFEST_DIR / "plantvillage_full.csv"
    df.to_csv(full_manifest, index=False)
    print(f"\n✓ Full manifest: {len(df)} images → {full_manifest}")

    # Report
    report_lines = [
        "# PlantVillage Dataset Preparation Report",
        "",
        "## Dataset",
        "- Source: mohanty/PlantVillage (HuggingFace)",
        "- License: CC-BY-SA 3.0",
        "- Paper: Hughes & Salathé (2016) arXiv:1511.08060",
        "",
        f"## Summary",
        f"- Total valid images: {len(df)}",
        f"- Corrupt/invalid: {len(corrupt)}",
        f"- Exact duplicates removed: {len(duplicates)}",
        f"- Classes: {df['class_label'].nunique()}",
        f"- Crops: {df['crop_name'].nunique()}",
        "",
        "## Class Distribution",
        "| Class | Crop | Health | Count |",
        "|---|---|---|---|",
    ]
    for cls in SUPPORTED_CLASS_LABELS:
        subset = df[df['class_label'] == cls]
        if len(subset) > 0:
            crop = subset['crop_name'].iloc[0]
            health = subset['health_status'].iloc[0]
            report_lines.append(f"| {cls} | {crop} | {health} | {len(subset)} |")

    if missing_classes:
        report_lines += ["", "## Missing Classes (not yet downloaded)", ""]
        for m in missing_classes:
            report_lines.append(f"- {m}")

    if corrupt:
        report_lines += ["", f"## Corrupt Images ({len(corrupt)})", ""]
        for c in corrupt[:10]:
            report_lines.append(f"- {c}")

    report_lines += [
        "",
        "## Acknowledged Limitations",
        "- Dataset contains only laboratory-condition images (controlled backgrounds).",
        "- Cotton, Rice, and Wheat are NOT present in PlantVillage — these crops are unsupported.",
        "- Field-condition accuracy will differ from lab-condition validation accuracy.",
        "- This is NOT the official SIH evaluation dataset.",
    ]

    report_path = REPORT_DIR / "preparation_report.md"
    report_path.write_text('\n'.join(report_lines))
    print(f"✓ Report saved: {report_path}")

    # Also save supported class registry
    registry = {
        "dataset": "mohanty/PlantVillage",
        "license": "CC-BY-SA 3.0",
        "supported_crops": SUPPORTED_CROPS,
        "class_taxonomy": [
            {
                "pv_dir": pv,
                "crop_name": crop,
                "disease_name": disease,
                "health_status": health,
                "class_label": label,
                "count": class_counts.get(label, 0)
            }
            for pv, (crop, disease, health, label) in CLASS_TAXONOMY.items()
        ],
        "unsupported_crops": ["Cotton", "Rice", "Wheat", "Maize (partial — only lab images)"],
        "total_images": len(df),
        "total_classes": df['class_label'].nunique() if len(df) else 0,
    }
    registry_path = PROJECT_ROOT / "data" / "supported_class_registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"✓ Class registry: {registry_path}")

    return df


if __name__ == "__main__":
    prepare()
