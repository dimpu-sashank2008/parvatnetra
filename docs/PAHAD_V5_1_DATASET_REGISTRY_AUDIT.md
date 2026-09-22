# PARVAT NETRA / PAHAD AI — PHASE V5.1 DATASET REGISTRY AUDIT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: Canonical Datasets, Negative Controls, Sequences, and Demo Quarantines  

---

## 1. Executive Summary

A critical finding resolved in Phase V5.1 is the reconciliation between:
- **Canonical Documented Real Landslide Events**: Exactly **17** records.
- **Divergent Narrative Summary Claim**: Untraced mention of "52 real historical events".

This audit traces every single CSV dataset on disk, performs row counts, verifies cryptographic hashes, inspects provenance columns, and documents negative control selection criteria.

---

## 2. Canonical Datasets on Disk

### 2.1 Raw Historical Landslide Events (`DS-RAW-NER-17`)
- **File Path**: `data/raw/historical_landslides_ner.csv`
- **SHA-256**: `47225ba3bfb46c0d8df3029bbdfb39d1b09ad3c683fae325603bbfa58129ff28`
- **Total Records**: **17** documented events (`EV-01` through `EV-17`).
- **Date Range**: May 16, 2022 to October 4, 2024.
- **Geographic Scope**: North-Eastern Region (NER) mountain highways:
  - NH-10 (Kalijhora, Birik Dara, 29th Mile, Teesta Bazar) — West Bengal / Sikkim
  - NH-29 (Kohima – Dimapur) — Nagaland
  - NH-06 (Jowai – Ratacherra) — Meghalaya
  - NH-102 (Imphal – Moreh) — Manipur
  - NH-13 (Nirjuli – Banderdewa) — Arunachal Pradesh
  - NH-108 (Damcherra – Dharmanagar) — Tripura
  - NH-54 (Kolasib – Sairang) — Mizoram
  - NH-27 (Haflong – Silchar) — Assam
- **Provenance**: Geological Survey of India (GSI) Bulletins, Border Roads Organisation (BRO) Road Closure Registers, NDMA Disaster Bulletins, IMD AWS historical archives.
- **Data Quality**: 100% verified coordinates, verified timestamps, zero synthetic rows.

### 2.2 Historical Negative Control Windows (`DS-CTRL-HIST-20`)
- **File Path**: `data/processed/lstm_v4_historical_controls.csv`
- **SHA-256**: `812b1cb570535bbadcb71887e5052fe2ae7a29e1eb1c01e3895e34be0175b5ae`
- **Total Records**: **20** verified non-failure windows (`CTRL-01` through `CTRL-20`).
- **Selection Algorithm**:
  1. Geographically matched to high-hazard corridors (NH-10, NH-29, NH-06, etc.).
  2. Temporal holdout periods of 168 hours under moderate-to-heavy rainfall (> 40mm/24h) where no movement or slope failure was recorded by BRO, SDMA, or local road stations.
  3. Buffer exclusion: windows maintain a minimum 14-day temporal separation and 5km spatial separation from known landslide events.

### 2.3 Empirical Multi-Horizon Sequences (`DS-V4-4-SEQUENCES-105`)
- **File Path**: `data/processed/lstm_v4_4_real_temporal_sequences.csv`
- **SHA-256**: `89b48d3b8354f8e66a26ccd9dc3b08d8b51a7616b3e983a803aa4d3285c305e3`
- **Total Rows**: **17,640** hourly rows.
- **Sequences**: **105 continuous 168-hour empirical sequences**.
- **Composition**:
  - 85 event sequences (5 temporal lead windows $\times$ 17 canonical events).
  - 20 negative control sequences (1 non-failure window $\times$ 20 control sites).
- **Channels**: 37 empirical environmental and reanalysis channels (rainfall intensity, antecedent precipitation, ERA5-Land volumetric soil water, InSAR cumulative velocity, thermal gradients, etc.).
- **Synthetic Content**: **0.0%** (zero manufactured time-series).

### 2.4 Event Classifier Feature Matrix (`DS-EVENT-FEATURES-36`)
- **File Path**: `data/features/features_all.csv`
- **SHA-256**: `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`
- **Total Samples**: **36** real observation feature rows.
- **Partitions**:
  - **Train Set**: 16 rows (`data/features/real_train.csv`: 8 positive events, 8 negative controls).
  - **Val Set**: 12 rows (`data/features/real_val.csv`: 4 positive events, 8 negative controls).
  - **Test Set**: 8 rows (`data/features/real_test.csv`: 5 positive events, 3 negative controls).
- **Target**: `event_label \in {0, 1}`.

### 2.5 Quarantined Synthetic Demonstration Set (`DS-DEMO-QUARANTINE-25`)
- **File Path**: `data/features/demo_train.csv`
- **SHA-256**: `091ff6cf0549321d5854bb6fb9b95955a8820c74fb9369d72491a61cbe1364d9`
- **Total Rows**: **25** synthetic sequences.
- **Quarantine Invariant**: Accessible ONLY when `PAHAD_DEMO_MODE=1`. Strictly excluded from operational training, model validation, and benchmark metrics.

---

## 3. Resolution of the "52 Events" Claim

Forensic examination of disk artifacts confirmed:
1. No CSV, JSON, or SQLite database in the repository contains 52 real historical events.
2. The number 52 appeared only in late text summaries as an unverified placeholder.
3. The true, documented, corroborated ground-truth event count is strictly **17**.
4. The 52-event claim is formally classified as **`UNSUPPORTED`** and removed from all authoritative documentation.
