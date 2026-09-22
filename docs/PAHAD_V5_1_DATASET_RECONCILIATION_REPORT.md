# PARVAT NETRA / PAHAD AI — PHASE V5.1 DATASET RECONCILIATION REPORT

**Document ID**: `DOC-V5-1-DATASET-RECON`  
**Phase**: V5.1 — Scientific Truth Ledger & Dataset Lineage Reconciliation  
**Primary Corridor**: `CORR-NH10-SIKKIM-KM48`  
**System Designation**: Smart India Hackathon (SIH) 2026 AI-Assisted Research and Decision-Support Prototype  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering Swarm  
**Date**: September 21, 2026  

---

## 1. Executive Summary & Objective

This report provides the authoritative, line-by-line reconciliation of all dataset lineage claims across Phases V4.4 through V5.0 of PARVAT NETRA. Specifically, it resolves the discrepancy between the canonical documented count of 17 historical landslide events and the divergent narrative placeholder claiming "52 Real Historical Events" and "41 Train / 11 Val / 11 Test".

Every physical and digital dataset on disk was verified using SHA-256 cryptographic hashing, row inspection, and temporal window validation.

---

## 2. Canonical Datasets on Disk

| Dataset ID | Path | SHA-256 | Classification | Rows | Positive Events | Negative Controls |
|---|---|---|---|---|---|---|
| `DS-RAW-NER-17` | `data/raw/historical_landslides_ner.csv` | `47225ba3bfb46c0d8df3029bbdfb39d1b09ad3c683fae325603bbfa58129ff28` | AUTHORITATIVE | 17 | 17 | 0 |
| `DS-CTRL-HIST-20` | `data/processed/lstm_v4_historical_controls.csv` | `812b1cb570535bbadcb71887e5052fe2ae7a29e1eb1c01e3895e34be0175b5ae` | AUTHORITATIVE | 20 | 0 | 20 |
| `DS-V4-4-SEQUENCES-105` | `data/processed/lstm_v4_4_real_temporal_sequences.csv` | `89b48d3b8354f8e66a26ccd9dc3b08d8b51a7616b3e983a803aa4d3285c305e3` | RESEARCH | 17,640 (105 seq) | 17 events (85 seq) | 20 controls (20 seq) |
| `DS-EVENT-FEATURES-36` | `data/features/features_all.csv` | `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e` | AUTHORITATIVE | 36 | 17 | 19 |
| `DS-DEMO-QUARANTINE-25` | `data/features/demo_train.csv` | `091ff6cf0549321d5854bb6fb9b95955a8820c74fb9369d72491a61cbe1364d9` | DEMO_QUARANTINE | 25 seq | 14 | 11 |

---

## 3. Forensic Investigation: 17 vs 52 Events

### 3.1 Finding
The file `data/raw/historical_landslides_ner.csv` contains exactly 17 records (`EV-01` to `EV-17`). No file on disk contains 52 historical events. The claim of "52 Real Historical Events" originated in a summary narrative block in Phase V5.0 and was never backed by raw data records.

### 3.2 Partition Reconciliation: 16/12/8 vs 41/11/11
The tabular feature matrix `data/features/features_all.csv` contains 36 samples partitioned as:
- **Training Set** (`data/features/train_set.csv`): 16 rows (8 positive, 8 negative)
- **Validation Set** (`data/features/val_set.csv`): 12 rows (4 positive, 8 negative)
- **Test Set** (`data/features/test_set.csv`): 8 rows (5 positive, 3 negative)
- **Total**: 36 rows

The claimed partition of "41 Train / 11 Val / 11 Test" (summing to 63 samples) does not match any artifact. It has been formally demoted to `UNSUPPORTED` in `CONF-02`.

---

## 4. Negative Control Strategy

The 20 negative control windows (`CTRL-01` to `CTRL-20`) were selected based on the following criteria:
1. **Corridor Alignment**: High-hazard NER mountain corridors (NH-10, NH-29, NH-06, NH-102, NH-13, NH-108, NH-54, NH-27).
2. **Stress Window**: 168-hour windows with moderate-to-heavy rainfall (>40mm / 24h) where slope stability was maintained.
3. **Buffer Exclusion**: Minimum 14-day temporal buffer and 5km spatial buffer from any documented landslide failure.

---

## 5. Formal Conclusion

The canonical historical landslide event count for PARVAT NETRA / PAHAD AI is **strictly 17 events**. All narrative claims of 52 events or 41/11/11 sample splits are formally deprecated, invalidated, and demoted to `UNSUPPORTED`.
