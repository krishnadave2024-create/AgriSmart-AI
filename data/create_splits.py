import os
import csv
import random
from collections import defaultdict

def create_splits():
    manifest_path = os.path.join(os.path.dirname(__file__), "manifests", "plantvillage_clean_manifest.csv")
    manifest_dir = os.path.dirname(manifest_path)
    
    if not os.path.exists(manifest_path):
        print(f"Error: {manifest_path} not found.")
        return
        
    records = []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
            
    # Group by class label
    class_groups = defaultdict(list)
    for r in records:
        class_groups[r['class_label']].append(r)
        
    # Since we excluded duplicates from the manifest entirely in clean_dataset.py,
    # every record here has a unique hash. Therefore, hash leakage is impossible.
    
    train_split = []
    val_split = []
    test_split = []
    
    # Use deterministic random seed
    random.seed(42)
    
    for cls, items in class_groups.items():
        # Sort items deterministically by relative_path before shuffling
        items.sort(key=lambda x: x['relative_path'])
        random.shuffle(items)
        
        n_total = len(items)
        if n_total < 10:
            print(f"Warning: Class {cls} has only {n_total} samples. Splitting may be severely unbalanced.")
            
        n_train = int(n_total * 0.70)
        n_val = int(n_total * 0.15)
        # Remainder goes to test
        
        # Ensure at least 1 per split if possible
        if n_total >= 3 and (n_train == 0 or n_val == 0 or (n_total - n_train - n_val) == 0):
            n_train = max(1, n_train)
            n_val = max(1, n_val)
            
        train_split.extend(items[:n_train])
        val_split.extend(items[n_train:n_train+n_val])
        test_split.extend(items[n_train+n_val:])
        
    def write_split(filename, data):
        path = os.path.join(manifest_dir, filename)
        # Sort output deterministically
        data.sort(key=lambda x: x['relative_path'])
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if not data:
                return
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            for r in data:
                writer.writerow(r)
        print(f"Wrote {len(data)} records to {filename}")
        
    write_split("train.csv", train_split)
    write_split("val.csv", val_split)
    write_split("test.csv", test_split)
    
    print("Splits created successfully.")
    print("Validating splits...")
    
    # Validation
    train_hashes = set(r['file_hash'] for r in train_split)
    val_hashes = set(r['file_hash'] for r in val_split)
    test_hashes = set(r['file_hash'] for r in test_split)
    
    assert len(train_hashes.intersection(val_hashes)) == 0, "Leakage detected between Train and Val"
    assert len(train_hashes.intersection(test_hashes)) == 0, "Leakage detected between Train and Test"
    assert len(val_hashes.intersection(test_hashes)) == 0, "Leakage detected between Val and Test"
    
    assert len(train_split) + len(val_split) + len(test_split) == len(records), "Total counts do not match"
    
    print("All validation checks passed.")

if __name__ == "__main__":
    create_splits()
