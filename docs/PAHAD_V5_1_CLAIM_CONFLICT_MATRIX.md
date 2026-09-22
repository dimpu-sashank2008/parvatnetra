# PARVAT NETRA / PAHAD AI — PHASE V5.1 CLAIM CONFLICT MATRIX

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: Reconciliation of 9 Identified Cross-Phase Inconsistencies  

---

## 1. Executive Summary

This document presents the complete 9-point Claim Conflict Matrix codified in `data/manifests/scientific_truth_ledger.json`. Every conflict is evaluated with its earlier claim, later claim, authoritative artifact, and formal resolution.

---

## 2. Reconciled Conflict Matrix

### CONF-01: Documented Historical Event Count
- **Earlier Claim**: 17 Canonical Historical Landslide Events (`data/raw/historical_landslides_ner.csv`).
- **Later Claim**: 52 Real Historical Events (cited in Phase V5.0 response narrative).
- **Authoritative Artifact**: `data/raw/historical_landslides_ner.csv` (17 rows, `EV-01` to `EV-17`).
- **Resolution**: 17 is the true ground-truth count. The figure 52 was an unverified text placeholder. Demoted to `UNSUPPORTED`.
- **Status**: **RESOLVED**

### CONF-02: Dataset Partition Splits
- **Earlier Claim**: 16 Train, 12 Val, 8 Test Holdout (`data/features/features_all.csv`, total 36 real samples).
- **Later Claim**: 41 Train, 11 Val, 11 Test (cited in Phase V5.0 response narrative, total 63 samples).
- **Authoritative Artifact**: `data/features/real_train.csv`, `real_val.csv`, `real_test.csv`.
- **Resolution**: 16/12/8 is the exact verified partitioning. 41/11/11 does not exist in any file. Demoted to `UNSUPPORTED`.
- **Status**: **RESOLVED**

### CONF-03: Published Evaluation Metrics
- **Earlier Claim**: Event GBDT Holdout: ROC-AUC 1.000, PR-AUC 1.000, POD 1.000, FAR 0.000, CSI 1.000, Brier 0.0824; V4.5 BiLSTM: 48h CSI 0.952, POD 1.000, FAR 0.048.
- **Later Claim**: ROC-AUC: 0.81, PR-AUC: 0.74, POD: 0.78, FAR: 0.22, CSI: 0.64.
- **Authoritative Artifact**: `models/pahad_event_metrics.json` and `reports/pahad_validation_strategy.md`.
- **Resolution**: The 0.81/0.74/0.78/0.22/0.64 metrics were untraced narrative placeholders. They are demoted to `UNSUPPORTED`.
- **Status**: **RESOLVED**

### CONF-04: Median Warning Lead Time
- **Earlier Claim**: 24h/48h horizons in ML models; 14.5 hours median lead time across 17 events in `CORE_IMPLEMENTATION_DEFENSE_SHEET.md`.
- **Later Claim**: 4.2 hours median warning lead time.
- **Authoritative Artifact**: `CORE_IMPLEMENTATION_DEFENSE_SHEET.md` and `templates/demo.html`.
- **Resolution**: 4.2 hours was the historical minimum lead time (and Saito formula demo output), not the median. Demoted to `UNSUPPORTED`.
- **Status**: **RESOLVED**

### CONF-05: Composite Risk Index (CRI) Feature Leakage
- **Earlier Claim**: CRI was included as input feature channel #33 in Phase V3 legacy model.
- **Later Claim**: CRI strictly removed as an input feature in Phase V4.4 and V4.5 to prevent circular self-referential prediction.
- **Authoritative Artifact**: `engine/pahad_feature_pipeline.py` and `scripts/evaluate_v4_5_temporal_cv.py`.
- **Resolution**: V3 legacy retains CRI for backwards compatibility under SHA-256 lock. V4.4 and V4.5 strictly eliminate CRI from feature vectors.
- **Status**: **RESOLVED**

### CONF-06: Kinematic In-Situ IoT ML Model Status
- **Earlier Claim**: Kinematic IoT ML model described in narrative prose as operational.
- **Later Claim**: Kinematic ML model is strictly `NOT_TRAINED_DATA_PENDING` (Phases V4.8–V5.0).
- **Authoritative Artifact**: `models/` directory inspection (zero kinematic weights files exist).
- **Resolution**: Physical downhole sensors and borehole casings are NOT yet installed. Kinematic ML model is strictly `NOT_TRAINED_DATA_PENDING`.
- **Status**: **RESOLVED**

### CONF-07: Physical Sensor Field Commissioning State
- **Earlier Claim**: Narrative suggestions that NH-10 KM48 instrumentation is active.
- **Later Claim**: Physical sensors verified = 0, borehole casing = `NOT_INSTALLED`, live observations = 0.
- **Authoritative Artifact**: `data/manifests/v5_0_physical_field_manifest.json`.
- **Resolution**: Zero field sensors exist in the ground. Hardware-in-the-Loop bench simulation (8,640 frames) is running, but field deployment remains pending.
- **Status**: **RESOLVED**

### CONF-08: Sensor Calibration Certification
- **Earlier Claim**: Claims of NABL / ISO-17025 accredited calibration lab certification.
- **Later Claim**: Calibration certificates and traceability sheets are `CALIBRATION_EVIDENCE_MISSING`.
- **Authoritative Artifact**: Phase V4.9 and V5.0 audit logs.
- **Resolution**: Manufacturer factory sheets exist, but third-party accredited metrology certificates do not. Classified as `CALIBRATION_EVIDENCE_MISSING`.
- **Status**: **RESOLVED**

### CONF-09: Institutional Authorization & Operational Clearance
- **Earlier Claim**: Narrative mention of official clearance code `BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026`.
- **Later Claim**: Collaboration is in pre-installation planning stage with no formal clearance.
- **Authoritative Artifact**: Administrative agency audit logs.
- **Resolution**: Clearance code was an unverified string. Official authority status is classified as `AUTHORIZATION_UNVERIFIED`.
- **Status**: **RESOLVED**
