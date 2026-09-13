# PAHAD AI — Data Pipeline & Ingestion Architecture
**Standard: Smart India Hackathon (SIH) 2026 Grade National Early Warning Architecture**

---

## 1. Directory Structure

```text
data/
├── raw/                 # Raw unprocessed external extracts (GSI bulletins, IMD rainfall)
├── processed/           # Filtered, harmonized event observation CSVs
├── labels/              # Ground-truth binary labels and event timestamps
├── features/            # Feature tables partitioned into train/val/test splits
└── README.md            # Comprehensive data dictionary and NER provenance guidelines
```

---

## 2. Ingestion Pipeline Scripts

1. `scripts/build_landslide_dataset.py`:
   - Curates documented historical mass-movement failure events from the Geological Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM) archives and state disaster management bulletins.
   - Synthesizes balanced, physically grounded control windows (dry season, moderate monsoon non-failure, stable heavy precipitation, and non-trigger seismic ground shaking).
   - Generates:
     - `data/processed/pahad_event_observations.csv` (36 records)
     - `data/labels/event_labels.csv`
     - `data/features/features_all.csv` (34 features)
     - `data/features/train_set.csv` ($\le 2023\text{-}12\text{-}31$)
     - `data/features/val_set.csv` ($2024\text{-}01\text{-}01$ to $2024\text{-}06\text{-}30$)
     - `data/features/test_set.csv` ($\ge 2024\text{-}07\text{-}01$)

2. `scripts/inspect_training_data.py`:
   - Programmatically audits class balance (47.2% positive, 52.8% negative).
   - Confirms 100% feature completeness with zero unexpected missing values.
   - Enforces regional representation across all 8 NER states.

3. `scripts/train_event_model.py`:
   - Trains GBDT with 5-fold spatial group cross-validation.
   - Fits Platt sigmoid calibration (`CalibratedClassifierCV`).
   - Exports serialized models to `models/` and performance metrics to `reports/`.

4. `scripts/evaluate_event_model.py`:
   - Independent verification suite executing out-of-sample evaluation on the holdout test set.

5. `scripts/export_model_metadata.py`:
   - Exports canonical MLOps metadata conforming to `models/pahad_feature_schema.json`.
