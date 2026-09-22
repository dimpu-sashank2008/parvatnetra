# PARVAT NETRA / PAHAD AI — PHASE V5.1 FINAL AUTHORITATIVE REPORT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 — Cross-Phase Scientific Consistency Audit, Model/Data Lineage Reconciliation & Deployment Claim Freeze  
**Author**: PARVAT NETRA Autonomous Systems Engineering Swarm  
**Platform**: PARVAT NETRA — NER Sentinel  
**AI System**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Corridor**: NH-10 KM48 (Kalijhora – Teesta Bridge – Birik Dara, Sikkim/Kalimpong)  
**System Designation**: SIH 2026 AI-Assisted Disaster-Intelligence Research Prototype  
**Authoritative Verdict**: `V5_1_TRUTH_LEDGER_VERIFIED`  

---

## 1. Executive Summary & Audit Mandate

Phase V5.1 was commissioned to conduct an exhaustive cross-phase scientific audit across all historical phases of PARVAT NETRA (Phases 1, 2A, 2B, 2C, 3, 3.1, V4.0 through V5.1). The mandate required:
1. Reconciling all divergent metrics, sample counts, model identities, telemetry states, and deployment claims into **ONE Authoritative Scientific Truth Ledger** (`data/manifests/scientific_truth_ledger.json`).
2. Forensically resolving the critical discrepancy from the V5.0 response block:
   - Untraced claim of 52 real events, 41/11/11 train/val/test splits, 0.81 ROC-AUC, and 4.2h median lead time.
3. Enforcing cryptographic bit-for-bit model immutability for Production V3 (`7cb82388...`) and Research V4.5 (`31e16ce0...`).
4. Codifying an absolute boundary for the Kinematic IoT ML model (`NOT_TRAINED_DATA_PENDING`) because physical borehole drilling and casing installation are pending in the field.
5. Implementing programmatic query interfaces (`engine/scientific_truth_engine.py`) and REST APIs (`/api/scientific-truth/ledger`, `/audit-summary`).
6. Enforcing a four-tier Claim Freeze (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `FORBIDDEN`).

---

## 2. Definitive Summary of Findings

### 2.1 The Single Source of Truth
- **Canonical Documented Historical Landslide Events**: Strictly **17** records (`data/raw/historical_landslides_ner.csv`: `EV-01` to `EV-17`).
- **Canonical Negative Control Windows**: Strictly **20** records (`data/processed/lstm_v4_historical_controls.csv`: `CTRL-01` to `CTRL-20`).
- **Canonical Multi-Horizon Continuous Sequences**: Strictly **105 continuous 168-hour sequences** (`data/processed/lstm_v4_4_real_temporal_sequences.csv`: 17,640 rows, 0.0% synthetic data).
- **Canonical Event Classifier Samples**: Strictly **36 real samples** (`data/features/features_all.csv`: 16 train, 12 val, 8 test holdout).
- **Quarantined Demonstration Dataset**: Strictly **25 synthetic sequences** (`data/features/demo_train.csv`, accessible only when `PAHAD_DEMO_MODE=1`).
- **Untraced Narrative Claims Demoted**: Claims of "52 events", "41/11/11 split", "0.81 ROC-AUC", and "4.2h median lead time" are authoritatively demoted to **`UNSUPPORTED`**.

### 2.2 Cryptographic Model Registry
- **Production Model**: `PAHAD-BiLSTM-v3-MultiModal-33Features`
  - Weights: `models/pahad_lstm_v3_weights.pt`
  - Verified SHA-256: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` (**VERIFIED UNCHANGED**)
  - Status: `PRODUCTION_SERVING_FROZEN`
- **Research Baseline**: `Model_D_1Layer_BiLSTM_Att_V4_5`
  - Weights: `models/pahad_lstm_v4_5_research_weights.pt`
  - Verified SHA-256: `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f` (**VERIFIED UNCHANGED**)
  - Status: `RESEARCH_BASELINE_OFFLINE`
- **Event Classifier**: `PAHAD-Event-Classifier-GBDT`
  - Weights: `models/pahad_event_model.pkl` (SHA-256: `80eeeb3c...`)
  - Status: `TRAINED_LIMITED_DATA`
- **FoS Regressor**: `PAHAD-Geotechnical-FoS-Predictor`
  - Status: `PHYSICS_SURROGATE_ACTIVE`
- **Kinematic IoT ML Model**: `PAHAD-Kinematic-IoT-ML-Model`
  - Status: Strictly `NOT_TRAINED_DATA_PENDING` (weights prohibited until boreholes drilled).

### 2.3 Physical Field Telemetry State
- **Physical Sensors in Ground**: Strictly **0**
- **Borehole Casing Installed**: Strictly **0** (`NOT_INSTALLED`)
- **Live Mountain Observations**: Strictly **0**
- **Continuous Telemetry Uptime**: Strictly **0.0 hours**
- **Bench / HIL Observations**: **8,640 frames** (simulated via RS485 loopback)
- **Field Telemetry Status**: `PHYSICAL_TELEMETRY_PENDING`
- **Sensor Calibration**: `CALIBRATION_EVIDENCE_MISSING`
- **Institutional Authority**: `AUTHORIZATION_UNVERIFIED`

### 2.4 Comprehensive Test Battery
- 38 out of 38 dedicated Phase V5.1 tests passed (**100.0%**).
- 184 out of 184 Phase V4.4 through V5.0 regression tests passed (**100.0%**).
- 142 out of 142 core event and PAHAD engine tests passed (**100.0%**).
- Total: **364 automated tests passed, 0 failures, 0 regressions**.

---

## 3. Authoritative Phase V5.1 Verdict

$$\mathbf{VERDICT: V5\_1\_TRUTH\_LEDGER\_VERIFIED}$$

All models, datasets, metrics, lead times, and claim boundaries are fully reconciled and codified in the authoritative ledger without modifying model weights, manufacturing field evidence, or inventing synthetic telemetry.
