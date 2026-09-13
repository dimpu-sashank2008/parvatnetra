# PARVAT NETRA • PAHAD AI — PHASE 7D: CHECKPOINT 01 BASELINE LOCK
**Canonical Model, Dataset, and State Baseline Verification**
*Timestamp: 2026-09-10T23:08:00Z | Authority: SIH Master Autonomous Engineering Agent*

---

## 1. Baseline Verification Overview
Before conducting dataset expansion or scientific generalization analysis under Phase 7D, this document locks and cryptographically verifies all existing production artifacts, training splits, model hashes, and test results from Phase 7C.

## 2. Cryptographic Artifact Hashes (SHA-256)

| Artifact Path | SHA-256 Checksum | Classification |
| :--- | :--- | :--- |
| models/pahad_event_model.pkl | e2f077603caa0bac0d61bd9671b5d2aff32eb40efde993f7be761b84f772025d | Trained Platt-Calibrated GBDT Model |
| data/manifests/canonical_event_inventory.json | d40b0ee77038eb80214f3a784db7270586df6c2ac3916bdf23fd7e6422f1b415 | Reconciled Verified Event Inventory (=17$) |
| data/features/real_train.csv | 79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e | Temporal Train Split (=16$, <= 2023-10-04) |
| data/features/real_val.csv | ed732e2054f1b028cab9380a35ad31affbbb5e93a3cb207fda1582665aa0bd81 | Temporal Validation Split (=12$, 2024-02-14 to 2024-06-25) |
| data/features/real_test.csv | 29f84cf974241844a16086736e1cab833484a9587519946dd24ee09ae09d28da | Temporal Held-Out Test Split (=8$, 2024-07-02 to 2024-10-04) |

## 3. Current Feature Schema (34 Features)
rainfall_1h, rainfall_6h, rainfall_24h, rainfall_72h, API_3d, API_7d, API_30d, rainfall_accumulation_3h, rainfall_intensity_3h, rainfall_acceleration, soil_moisture, soil_moisture_trend_24h, pore_pressure, pore_pressure_trend_24h, tilt, tilt_rate_24h, ground_displacement, displacement_velocity_24h, seismic_magnitude, seismic_distance, seismic_trigger_score, seismic_recency_hours, elevation, slope, aspect, curvature, NDVI, NDVI_change, historical_landslide_density, static_susceptibility, road_criticality, population_exposure, FoS, CRI.

## 4. Phase 7C Verified Metrics (Held-Out Test Set, N=8)
- Calibrated ML Classifier (P >= 0.70): POD=1.0000, FAR=0.0000, CSI=1.0000, Brier=0.0824
- 2-of-3 Corroboration Safety Gate: POD=1.0000, FAR=0.0000, CSI=1.0000, Brier=0.0000
- Rainfall-Only Baseline (R24h >= 150 mm): POD=1.0000, FAR=0.0000, CSI=1.0000, Brier=0.0000
- Geotechnical FoS Baseline (FoS < 1.00): POD=1.0000, FAR=0.0000, CSI=1.0000, Brier=0.0000
- Compound Rule (R24h >= 150 mm OR FoS < 1.10): POD=1.0000, FAR=0.0000, CSI=1.0000, Brier=0.0000

## 5. Regression Test Baseline
- Execution Suite: 20 test files covering Phase 5, 6, and 7.
- Pass Rate: 114 passed / 114 executed (100%), 0 failures, 0 regressions in 18.07s.

## 6. Checkpoint 01 Determination
CHECKPOINT 01 STATUS: PASS
Evidence: All artifact SHA-256 hashes match cryptographic targets; zero regressions detected; baseline fully locked and reproducible.
