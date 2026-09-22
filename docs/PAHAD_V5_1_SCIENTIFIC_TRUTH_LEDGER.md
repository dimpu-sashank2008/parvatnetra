# PARVAT NETRA / PAHAD AI — PHASE V5.1 MASTER SCIENTIFIC TRUTH LEDGER

**Authority**: PARVAT NETRA Autonomous Engineering Swarm  
**Phase**: V5.1 — Cross-Phase Scientific Consistency Audit & Deployment Claim Freeze  
**Corridor**: NH-10 KM48 (Kalijhora – Teesta Bridge – Birik Dara, Sikkim/Kalimpong)  
**System Designation**: SIH 2026 AI-Assisted Disaster-Intelligence Research Prototype  
**Authoritative Verdict**: `V5_1_TRUTH_LEDGER_VERIFIED`  
**Date**: September 21, 2026  

---

## 1. Executive Summary & Audit Mandate

Phase V5.1 establishes **ONE Authoritative Scientific Truth Ledger** (`data/manifests/scientific_truth_ledger.json`) across all development phases of PARVAT NETRA (Phases 1, 2A, 2B, 2C, 3, 3.1, V4.0 through V5.1).

Prior to this phase, incremental updates across phases introduced divergent documentation claims:
1. Historical event counts cited as 17 in raw manifests vs 52 in late narrative summaries.
2. Training/val/test splits cited as 16/12/8 vs 41/11/11.
3. Test metrics cited as ROC-AUC 1.000 / PR-AUC 1.000 (36-sample GBDT) and CSI 0.952 (105-sequence V4.5 BiLSTM) vs ROC-AUC 0.81 / PR-AUC 0.74 / POD 0.78 / FAR 0.22 / CSI 0.64.
4. Warning lead times cited as 24h / 48h (synoptic models) and 14.5h median (historical defense sheet) vs 4.2h median (which was actually the historical minimum / Saito formula placeholder).
5. Kinematic IoT ML model claimed in narrative text as operational, whereas physical field sensors have not yet been installed in boreholes.

Phase V5.1 forensically audits every artifact on disk, freezes model weights under cryptographic SHA-256 verification, reconciles all 9 cross-phase conflicts, demotes untraced claims to `UNSUPPORTED`, and establishes strict operational boundaries.

---

## 2. Master Model Truth Registry

| Model Key | Model Designation | Architecture | Weights File | Verified SHA-256 | Status | Horiz. | Seq. Len | Feat. |
|---|---|---|---|---|---|---|---|---|
| **Production V3** | `PAHAD-BiLSTM-v3-MultiModal-33Features` | 2-layer BiLSTM + Temporal Attention (hidden=160) | `models/pahad_lstm_v3_weights.pt` | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` | `PRODUCTION_SERVING_FROZEN` | 6h, 12h, 24h, 48h | 72h | 33 |
| **Research V4.5** | `Model_D_1Layer_BiLSTM_Att_V4_5` | 1-layer BiLSTM + Multi-Head Temporal Attention (hidden=128) | `models/pahad_lstm_v4_5_research_weights.pt` | `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f` | `RESEARCH_BASELINE_OFFLINE` | 6h, 12h, 24h, 48h, 72h, 168h | 168h | 31 |
| **Event Classifier** | `PAHAD-Event-Classifier-GBDT` | Scikit-Learn GradientBoostingClassifier + Platt CalibratedClassifierCV | `models/pahad_event_model.pkl` | `80eeeb3c261e4e3e3b3e23927d3b51d8b9d3ffbb9007f3d9d300ad8c44b931be` | `TRAINED_LIMITED_DATA` | 1h, 3h, 6h, 12h, 24h, 48h | Tabular | 13 |
| **FoS Predictor** | `PAHAD-Geotechnical-FoS-Predictor` | RandomForestRegressor for Infinite-Slope Mohr-Coulomb Factor of Safety | `models/fos_predictor.pkl` | Verified On Disk | `PHYSICS_SURROGATE_ACTIVE` | Static/Dynamic | Instant | 8 |
| **Kinematic IoT ML** | `PAHAD-Kinematic-IoT-ML-Model` | Proposed High-Frequency Borehole In-Situ Kinematic Model | None (Weights Prohibited) | N/A | `NOT_TRAINED_DATA_PENDING` | Pending Data | N/A | 0 |

---

## 3. Authoritative Dataset Registry

| Dataset ID | Disk Path | Verified SHA-256 | Classification | Rows / Units | Positive Events | Negative Controls |
|---|---|---|---|---|---|---|
| `DS-RAW-NER-17` | `data/raw/historical_landslides_ner.csv` | `47225ba3bfb46c0d8df3029bbdfb39d1b09ad3c683fae325603bbfa58129ff28` | AUTHORITATIVE | 17 rows | 17 | 0 |
| `DS-CTRL-HIST-20` | `data/processed/lstm_v4_historical_controls.csv` | `812b1cb570535bbadcb71887e5052fe2ae7a29e1eb1c01e3895e34be0175b5ae` | AUTHORITATIVE | 20 rows | 0 | 20 |
| `DS-V4-4-SEQUENCES-105` | `data/processed/lstm_v4_4_real_temporal_sequences.csv` | `89b48d3b8354f8e66a26ccd9dc3b08d8b51a7616b3e983a803aa4d3285c305e3` | RESEARCH | 17,640 rows (105 seq) | 17 events (85 seq) | 20 controls (20 seq) |
| `DS-EVENT-FEATURES-36` | `data/features/features_all.csv` | `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e` | AUTHORITATIVE | 36 rows | 17 | 19 |
| `DS-DEMO-QUARANTINE-25` | `data/features/demo_train.csv` | `091ff6cf0549321d5854bb6fb9b95955a8820c74fb9369d72491a61cbe1364d9` | DEMO_QUARANTINE | 25 sequences | 14 | 11 |

---

## 4. Physical Field Telemetry Truth

- **Physical Sensors Verified in Ground**: Strictly **0**
- **Borehole Casing Installation**: Strictly **0** (`NOT_INSTALLED`)
- **Live Mountain Observations**: Strictly **0**
- **Continuous Live Telemetry Hours**: Strictly **0.0 hours**
- **Bench / Hardware-in-the-Loop (HIL) Observations**: **8,640 frames** (simulated via Rigol/RS485 bridge)
- **Field Telemetry Status**: `PHYSICAL_TELEMETRY_PENDING`

---

## 5. Authoritative Verdict

The authoritative verdict of Phase V5.1 is:
```
V5_1_TRUTH_LEDGER_VERIFIED
```
All models, datasets, metrics, and claims are reconciled under a single immutable ledger.
