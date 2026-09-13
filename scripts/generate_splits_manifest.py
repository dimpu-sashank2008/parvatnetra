# -*- coding: utf-8 -*-
"""
scripts/generate_splits_manifest.py
===================================
Generates data/splits/train.json, validation.json, and test.json
containing complete provenance, cryptographic hashes, and sample-level metadata.
"""

import os
import json
import hashlib
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_DIR = os.path.join(REPO_ROOT, "data", "features")
SPLITS_DIR = os.path.join(REPO_ROOT, "data", "splits")
os.makedirs(SPLITS_DIR, exist_ok=True)

splits = [
    ("train", "real_train.csv", "train.json"),
    ("validation", "real_val.csv", "validation.json"),
    ("test", "real_test.csv", "test.json")
]

for name, csv_name, json_name in splits:
    csv_path = os.path.join(FEATURES_DIR, csv_name)
    with open(csv_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    df = pd.read_csv(csv_path)
    timestamps = pd.to_datetime(df["timestamp"], utc=True)
    samples = []
    for idx, row in df.iterrows():
        samples.append({
            "sample_id": f"{name}_{idx+1:03d}",
            "sector_id": str(row["sector_id"]),
            "timestamp": str(row["timestamp"]),
            "event_label": int(row["event_label"]),
            "geographic_group": str(row.get("geographic_group", "unknown")),
            "FoS": round(float(row.get("FoS", 1.25)), 3),
            "CRI": round(float(row.get("CRI", 50.0)), 1)
        })
    manifest = {
        "split": name,
        "source_file": f"data/features/{csv_name}",
        "sha256_hash": sha256,
        "total_samples": len(df),
        "positive_count": int(df["event_label"].sum()),
        "negative_count": int(len(df) - df["event_label"].sum()),
        "date_range": {
            "min_timestamp": str(timestamps.min()),
            "max_timestamp": str(timestamps.max())
        },
        "validation_strategy": "TEMPORAL_HOLDOUT",
        "samples": samples
    }
    out_path = os.path.join(SPLITS_DIR, json_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote {out_path}: {len(df)} samples ({manifest['positive_count']} pos, {manifest['negative_count']} neg, SHA256: {sha256[:12]}...)")
