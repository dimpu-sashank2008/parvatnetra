# PHASE 7D: CHECKPOINT 06 — DATASET QUALITY GATE
Date: 2026-09-10T23:45:00Z

## Evidence

DATASET SPLIT QUALITY:
  real_train.csv:  pos=8  neg=8  total=16  missing_values=0
    SHA-256: 79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e
  real_val.csv:    pos=4  neg=8  total=12  missing_values=0
    SHA-256: ed732e2054f1b028cab9380a35ad31affbbb5e93a3cb207fda1582665aa0bd81
  real_test.csv:   pos=5  neg=3  total=8   missing_values=0
    SHA-256: 29f84cf974241844a16086736e1cab833484a9587519946dd24ee09ae09d28da

TOTALS: pos=17, neg=19, total=36
Class balance ratio (pos/neg): 0.895
Missing feature values: 0
Balance verdict: ACCEPTABLE (0.4 <= 0.895 <= 2.5)

HASH INTEGRITY: All three SHA-256 hashes match the baseline lock recorded in PHASE7D_BASELINE_LOCK.md.
No data corruption or modification since CP01 baseline.

QUALITY GATE CRITERIA:
  [x] No missing features
  [x] No NaN or empty values
  [x] Class balance within 0.4-2.5
  [x] SHA-256 hashes match baseline lock
  [x] Zero synthetic contamination (confirmed by check_event_leakage.py)
  [x] All 36 records have valid timestamps
  [x] All 36 records within NER bounding box (20-30.5N, 87-98E)

MINIMUM SAMPLE REQUIREMENT:
  Real labelled events: 17 < 150 minimum threshold
  Decision: MODEL_STATUS = TRAINED_LIMITED_DATA (unchanged)
  Confidence intervals cannot be guaranteed at 95% confidence.

## Checkpoint 06 Determination
STATUS: PASS (quality gate met; sample insufficiency documented)
