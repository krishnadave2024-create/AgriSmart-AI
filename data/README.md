# Dataset Information

This directory handles downloading, cleaning, and preparing the agricultural dataset.

- **Source**: PlantVillage Dataset (Color)
- **Important**: This is the public training dataset. The official SIH dataset remains held-out and is NOT to be used here.
- **Images**: Extracted to `data/external/plantvillage`. The raw images are excluded from version control to save space.

## Reproducing the Cleaning & Split Generation (Windows)

Ensure you have downloaded and extracted the PlantVillage dataset using the Phase 1 & 2 instructions (`data/DATASET_SETUP_WINDOWS.md`).

To reproduce the exact dataset cleaning, deduplication, and leakage-free stratified splits, run these exact Windows commands:

### 1. Cleaning and Manifest Generation
Run the cleaning script to perform hash-based exact deduplication and corrupt image exclusion.
```powershell
python data\clean_dataset.py
```
This produces the authoritative clean manifest containing only unique and valid images at:
`data\manifests\plantvillage_clean_manifest.csv`

### 2. Generate Leakage-Free Stratified Splits
Run the split script to allocate 70% Train, 15% Validation, and 15% Test datasets deterministically.
```powershell
python data\create_splits.py
```
This will automatically:
- Read the unique hashes from the clean manifest.
- Create `data\manifests\train.csv`, `val.csv`, and `test.csv`.
- Run internal validation checks to ensure zero hash overlap (leakage) between splits.
- Fail loudly if leakage is detected.

### 3. Generate the Audit Report
To view the results of the phase 3 cleaning process:
```powershell
python data\reports\generate_phase3_report.py
```
The final report will be available at: `data\reports\phase3_cleaning_and_splits_report.md`

## Requirements
- Python 3.9+
- `pillow` (`pip install pillow`)
- See `requirements.txt` for the full project dependencies.