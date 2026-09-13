# PHASE 7D: CHECKPOINT 04 — NEGATIVE CONTROL QUALITY AUDIT
Date: 2026-09-10T23:43:00Z

## 1. Objective
Verify the 19 negative controls are defensible documented non-failure windows.

## 2. Control Classification

### Category A: DRY-SEASON Controls (N=8, all in real_train.csv)
Timestamps: Jan–Mar 2023 (winter/pre-monsoon)
Geography: One control per each of the 8 NER states
FoS range: 1.70–1.90
Rainfall 24h: 0.0–2.0mm (extremely low — dry season)
Tilt: 0.06–0.11 deg (minimal deformation)

DEFENSIBILITY:
- Represents well-documented stable meteorological windows (winter dry season NER)
- No contemporaneous GSI or SDMA landslide bulletin found for these dates
- FoS >> 1.0 indicating substantial geotechnical margin
- Low precipitation consistent with January–March inter-monsoon period
CLASSIFICATION: DEFENSIBLE as negative control (winter dry season, documented stable period)
NOTE: These are easy negatives — the model correctly ignores them. They do NOT represent the most challenging negative scenario.

### Category B: SEISMIC-STRESS Controls (N=2, real_val.csv)
Timestamps: Feb–Mar 2024 (post-seismic dry season)
Geography: Sikkim, Assam
FoS range: 1.30–1.35
Rainfall 24h: 0.0–5.0mm
Tilt: 0.65–0.72 deg (elevated but no failure)

DEFENSIBILITY:
- Designed to test model under seismic excitation without co-occurring rainfall trigger
- No failure reported by SDMA Sikkim or ASDMA for these dates in USGS seismic context
- FoS > 1.0 with low rainfall; tilt elevated from seismic but no progression
CLASSIFICATION: CONDITIONALLY DEFENSIBLE — seismic stress context is plausible. Source attribution requires formal confirmation from SDMA records (not yet available).
CAVEAT: Feature values appear engineered to represent a specific scenario rather than sourced from direct observation.

### Category C: MODERATE-RAINFALL Controls (N=6, real_val.csv)
Timestamps: May–Jun 2024 (early monsoon onset)
Geography: Sikkim, Mizoram, Manipur, Assam, Meghalaya, Nagaland
FoS range: 1.28–1.41
Rainfall 24h: 38–65mm (moderate monsoon)
Tilt: 0.38–0.52 deg

DEFENSIBILITY:
- Represents challenging negative scenario: moderate monsoon rainfall on steep terrain WITHOUT failure
- FoS range 1.28–1.41 is plausible for stable slopes under moderate saturation
- Dates between documented events (no SDMA bulletin found for these specific dates)
CLASSIFICATION: PARTIALLY DEFENSIBLE — temporal placement is reasonable, but feature values require institutional confirmation that no failure occurred at these specific geographic coordinates/windows.
CAVEAT: These controls are temporally close to actual events (May/Jun 2024). The geographic groups differ from event sectors, but overlap cannot be fully excluded without sector-level SDMA records.

### Category D: HEAVY-STABLE Controls (N=3, real_test.csv)
Timestamps: Jul–Aug 2024 (peak monsoon, test partition)
Geography: Assam, Meghalaya, Arunachal Pradesh
FoS range: 1.10–1.16
Rainfall 24h: 92–115mm (heavy rainfall)
Tilt: 0.75–0.88 deg

DEFENSIBILITY:
- These are the most challenging negative controls: heavy rainfall, near-critical FoS, significant tilt
- FoS 1.10–1.16 with 115mm/24h rainfall represents NEAR-FAILURE but no failure
- No SDMA bulletin found for these exact dates/locations — absence of evidence is not evidence of absence
RISK FLAG: At FoS=1.10 and 115mm/24h rainfall, these controls are in a geotechnically marginal zone. The model's correct classification of these as negative may partly reflect overfitting to the training signal rather than genuine geotechnical distinction.
CLASSIFICATION: CONDITIONALLY DEFENSIBLE — challenging controls are scientifically appropriate but cannot be confirmed as "ground truth stable" without direct institutional records.

## 3. Overall Assessment

| Control Category | N | Defensibility | Provenance Quality | Risk Flag |
|:---|:---|:---|:---|:---|
| DRY-SEASON | 8 | HIGH | Meteorological context confirmed | Easy negatives — limited discriminatory value |
| SEISMIC-STRESS | 2 | MODERATE | Plausible, not institutionally confirmed | Feature values appear engineered |
| MODERATE-RAINFALL | 6 | MODERATE | Temporally placed, not confirmed | Close to event timestamps |
| HEAVY-STABLE | 3 | LOW-MODERATE | High-risk zone, not confirmed stable | Near-critical FoS at test partition |

## 4. Control Selection Algorithm

Controls selected per Phase 3.1 methodology:
- One geographically representative control per NER state per season
- Temporal exclusion zone: >48h from any documented event in same geographic group
- CHECK RESULT: ZERO temporal collisions verified by dedicated temporal audit

## 5. Class Balance

Train: pos=8, neg=8 (ratio 1.0)
Val:   pos=4, neg=8 (ratio 0.5)
Test:  pos=5, neg=3 (ratio 1.67)
Total: pos=17, neg=19 (ratio 0.895 - ACCEPTABLE per AGENTS.md)

## 6. Checkpoint 04 Determination

STATUS: CONDITIONAL_PASS (with documented limitations)

PASS conditions met:
- Zero temporal collisions with events
- Feature values physically plausible
- Class balance within acceptable range
- No duplicate controls detected

LIMITATIONS documented:
- 8 DRY-SEASON controls are easy negatives with limited discriminatory challenge
- SEISMIC and HEAVY-STABLE controls appear to have engineered feature values rather than directly observed measurements
- Formal GSI/SDMA institutional confirmation of non-failure for MODERATE and HEAVY controls is pending

REQUIRED ACTION: When institutional data access is obtained, replace engineered control features with directly observed measurements from confirmed non-failure windows.
