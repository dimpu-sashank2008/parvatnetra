# PHASE 7D: CHECKPOINT 10 — MODEL GOVERNANCE
Date: 2026-09-10T23:51:00Z

## 1. Model Registry State

MODEL FILE: models/pahad_event_model.pkl
METADATA:   models/pahad_event_model.metadata.json
METRICS:    models/pahad_event_metrics.json

Model version:       test-v1.0
Created at:          2026-09-10T18:19:55Z
Algorithm:           GradientBoostingClassifier + Platt Sigmoid Calibration
Status:              TRAINED_LIMITED_DATA
Dataset hash:        79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e
Training rows:       16 (pos=8, neg=8)
Validation rows:     12 (pos=4, neg=8)
Test rows:           8  (pos=5, neg=3)
Total verified events: 17
Forecast horizons:   [1, 3, 6, 12, 24, 48] hours

## 2. Governance Rules Applied (from AGENTS.md / Phase 3.1)

  [x] Real and synthetic samples separated (demo_train.csv vs real_*.csv)
  [x] Operational training uses ONLY real verified events
  [x] PAHAD_DEMO_MODE=1 required to use synthetic demo data
  [x] Model status = TRAINED_LIMITED_DATA (not PRODUCTION)
  [x] Dataset hash locked and verified
  [x] Model version tracked in metadata
  [x] FoS model (Model A) distinct from Event model (Model B)
  [x] Public emergency dispatch disabled (siren: DISPATCH_DISABLED)
  [x] 2-of-3 independent confirmation required for any alert

## 3. Model Status Decision Matrix

  Condition                             | Value     | Decision
  Real verified events                  | 17        | TRAINED_LIMITED_DATA (< 150 threshold)
  Test CSI                              | 1.0       | Does NOT warrant upgrade (small N=8)
  Institutional data access             | BLOCKED   | Cannot expand dataset
  Physical sensor deployment            | PENDING   | No live telemetry
  IMD rainfall API access               | PENDING   | No real-time hydrology
  Public dispatch authorization         | DISABLED  | SHADOW_ONLY

MODEL_STATUS: TRAINED_LIMITED_DATA (NO CHANGE)

## 4. Phase 7D Governance Summary

The Phase 7D dataset expansion attempt has been completed. The canonical dataset
remains at N=17 events and N=19 controls because:

  a) All institutional data portals (GSI, NESAC, NASA COOLR, EM-DAT) are inaccessible
     programmatically without formal MoU or authenticated access.
  b) No new events were fabricated (as strictly required by AGENTS.md).
  c) The model therefore remains TRAINED_LIMITED_DATA.

The 19 negative controls have been audited and are CONDITIONALLY DEFENSIBLE.
The 8 DRY-SEASON controls are easy negatives. The 3 HEAVY-STABLE test controls
are in a near-critical FoS zone and require institutional confirmation of non-failure.

## 5. Checkpoint 10 Determination
STATUS: PASS (governance rules fully documented and enforced)
