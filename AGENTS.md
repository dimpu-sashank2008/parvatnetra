# PARVATNETRA / PAHAD AI — PHASE 3.1

## REAL EVENT DATA EXPANSION, DATA QUALITY & MODEL VALIDATION

You are continuing development of the existing PARVATNETRA project.

Platform:
PARVATNETRA

AI:
PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response

Phases 2A, 2B, 2C and 3 have already been implemented.

DO NOT rebuild the application.

DO NOT redesign the UI.

DO NOT add unrelated features.

The objective of this phase is to make the PAHAD landslide-event prediction model scientifically more defensible by improving data quality, event labeling, validation methodology and model reporting.

==================================================

1. CRITICAL MODEL DISTINCTION
   ==================================================

There are currently two different model families.

MODEL A:
PAHAD Geotechnical FoS Model

Target:
Factor of Safety

MODEL B:
PAHAD Landslide Event Model

Target:
Probability of a landslide event within a forecast horizon.

Do NOT merge them conceptually.

Do NOT rename the FoS model into a landslide-event model.

The event model must remain a separate classifier.

==================================================
2. AUDIT THE CURRENT EVENT DATA
===============================

Inspect exactly:

data/raw/
data/processed/
data/labels/
data/features/

Inspect:

historical_landslides_ner.csv
pahad_event_observations.csv
event_labels.csv
features_all.csv
train_set.csv
val_set.csv
test_set.csv

Report:

* number of real event records
* number of synthetic/derived records
* date range
* state coverage
* district coverage
* sector coverage
* duplicated events
* missing coordinates
* missing timestamps
* missing features
* label confidence
* source provenance

Do not assume anything is real simply because it is stored in CSV.

==================================================
3. DATA PROVENANCE AUDIT
========================

For every record determine:

REAL
DERIVED
SYNTHETIC
DEMO
HISTORICAL
UNKNOWN

Every training sample must have provenance.

Create:

data/README.md

and:

reports/pahad_data_quality_report.md
reports/pahad_data_quality_report.json

The report must clearly distinguish:

DOCUMENTED EVENT

from:

ENGINEERED FEATURE

from:

SYNTHETIC DEMO SAMPLE

==================================================
4. REMOVE SYNTHETIC SAMPLES FROM OPERATIONAL TRAINING
=====================================================

This is mandatory.

If a sample is synthetic or generated solely to expand the dataset:

DO NOT silently include it in the operational event-model training set.

Instead create separate datasets:

data/features/real_train.csv
data/features/real_val.csv
data/features/real_test.csv

and:

data/features/demo_train.csv

The demo dataset may only be used when:

PAHAD_DEMO_MODE=1

The final model metadata must state exactly what training data was used.

==================================================
5. HISTORICAL EVENT LABELING
============================

Inspect all documented landslide events.

For each event create:

event_id
timestamp
latitude
longitude
state
district
sector_id
source
source_confidence

Target:

event_label = 1

Then construct non-event/control windows.

IMPORTANT:

A non-event sample is not automatically "ground truth stable".

Only create a negative label if there is a defensible observation window with no documented failure.

Otherwise use:

unknown

and exclude it from supervised binary training.

==================================================
6. TEMPORAL WINDOW GENERATION
=============================

For each documented event, create feature windows before the event:

1h
3h
6h
12h
24h
48h
72h

Include when available:

rainfall
antecedent rainfall
soil moisture
pore pressure
FoS
slope
elevation
curvature
NDVI
historical susceptibility
seismic indicators
deformation
IoT anomalies
road disturbance

Do not invent observations to fill missing historical time periods.

If a feature did not exist historically:

mark it missing.

==================================================
7. NEGATIVE CONTROL STRATEGY
============================

Create geographically and temporally appropriate control windows.

Controls should be selected from periods and locations where:

* no documented landslide occurred
* data coverage is sufficient
* the time window does not overlap known event windows

Avoid selecting easy negatives that are obviously unlike every positive event.

Calculate:

class balance
event density
control density

Document the control selection algorithm.

==================================================
8. LEAKAGE AUDIT
================

Build an explicit leakage checker.

Check for:

* duplicate event IDs
* duplicate timestamps
* repeated feature windows
* overlapping windows
* future rainfall appearing in past features
* post-event measurements appearing before event time
* the same event appearing in train and test
* same geographic event sequence crossing partitions

Create:

scripts/check_event_leakage.py

The script must fail loudly if leakage is detected.

==================================================
9. VALIDATION STRATEGY
======================

Do NOT use ordinary random train_test_split as the primary validation.

Use:

TEMPORAL HOLDOUT

Example:

TRAIN:
oldest period

VALIDATION:
later period

TEST:
most recent period

Where sample volume permits, also conduct:

GROUPED SPATIAL VALIDATION

using:

state
district
basin
or sector

depending on available data.

Create:

reports/pahad_validation_strategy.md

==================================================
10. MINIMUM SAMPLE REQUIREMENT
==============================

Before training, calculate whether the dataset is large enough.

If the real labelled event dataset remains extremely small:

DO NOT manufacture a large dataset.

Instead set:

MODEL_STATUS = TRAINED_LIMITED_DATA

or:

MODEL_STATUS = INSUFFICIENT_DATA

The system must prefer an honest limitation over fake performance.

==================================================
11. EVENT MODEL TRAINING
========================

Use the existing:

scripts/train_event_model.py

Refactor if required.

Preferred baseline:

GradientBoostingClassifier

Also support if installed:

RandomForestClassifier
XGBoost

Train separately for:

6h
12h
24h
48h

If data volume is insufficient for independent horizon models:

create a clearly documented shared model or baseline and explain the limitation.

Do not create unnecessary model complexity.

==================================================
12. TEMPORAL DEEP LEARNING
==========================

DO NOT claim an LSTM or GRU is trained unless the repository contains:

* actual sequence data
* real temporal labels
* a real PyTorch/TensorFlow implementation
* actual training
* actual validation

If these conditions are not satisfied:

status:

NOT_TRAINED

Do not fabricate results.

The existing mathematical surrogate in:

engine/pahad_lstm.py

must remain explicitly identified as a surrogate.

==================================================
13. PROBABILITY CALIBRATION
===========================

Keep calibrated probabilities.

Evaluate:

raw probability

versus:

calibrated probability

Use:

Platt scaling

or:

isotonic regression

depending on data volume.

Do not claim calibration quality if the validation set is too small.

==================================================
14. PERFORMANCE METRICS
=======================

Calculate where statistically meaningful:

ROC-AUC
PR-AUC
Precision
Recall
F1
Brier score
Calibration error
Confusion matrix

Also calculate operational metrics:

POD
FAR
CSI

Definitions:

POD = hits / (hits + misses)

FAR = false alarms / (hits + false alarms)

CSI = hits / (hits + misses + false alarms)

Do not report meaningless metrics from tiny test partitions without clearly stating sample size.

==================================================
15. EARLY-WARNING METRIC
========================

Add an important metric:

WARNING LEAD TIME

For each correctly detected event:

time of first qualifying prediction
→
event occurrence time

Calculate:

median lead time
minimum lead time
maximum lead time

When data allows.

This is much more meaningful for an early-warning system than accuracy alone.

==================================================
16. THRESHOLD ANALYSIS
======================

Evaluate event probability thresholds:

0.50
0.60
0.70
0.80
0.90

For each:

precision
recall
FAR
POD
CSI

Create:

reports/pahad_threshold_analysis.csv

The operational threshold must be configurable.

Do not automatically choose 0.80 merely because the research document mentions it.

==================================================
17. MODEL CALIBRATION REPORT
============================

Create:

reports/pahad_calibration_report.md

Include:

* dataset size
* positive count
* negative count
* validation size
* calibration method
* reliability information
* Brier score
* ECE
* limitations

==================================================
18. FEATURE IMPORTANCE
======================

Produce model-driver information.

Preferred:

SHAP

Fallback:

native model feature importance

For every driver provide:

feature
importance
direction
data source
availability

Never describe feature importance as causal proof.

Use:

"model driver"

or:

"contributing signal"

==================================================
19. MODEL CARD
==============

Update:

docs/PAHAD_MODEL_CARD.md

Clearly state:

MODEL:
PAHAD Event Classifier

TARGET:
landslide event probability

GEOGRAPHIC SCOPE:
NER

FORECAST:
6h / 12h / 24h / 48h

TRAINING DATA:
exact source and number

VALIDATION:
exact methodology

STATUS:
PRODUCTION-CANDIDATE
TRAINED_LIMITED_DATA
INSUFFICIENT_DATA
or DEMO_ONLY

depending on actual results.

==================================================
20. MODEL VERSIONING
====================

Create a versioned model registry:

models/pahad_event_model.pkl
models/pahad_event_model.metadata.json
models/pahad_event_metrics.json

Metadata must include:

model_version
created_at
dataset_hash
feature_schema_version
training_rows
positive_rows
negative_rows
validation_strategy
metrics
calibration
status

==================================================
21. DATASET HASH
================

Calculate a SHA-256 hash of the exact training dataset.

Store it in model metadata.

This allows us to prove which data produced which model.

==================================================
22. REPRODUCIBILITY
===================

Training must be reproducible.

Support:

--seed

and document:

Python version
scikit-learn version
feature schema
dataset hash
model parameters

==================================================
23. RETRAINING COMMAND
======================

Ensure:

python scripts/train_event_model.py

can reproducibly rebuild the model.

Support:

--dataset
--output
--algorithm
--seed
--forecast-window
--model-version

==================================================
24. PREDICTION API
==================

Preserve:

POST /api/pahad/predict-event

Return:

event_probability
calibrated_probability
forecast_horizon
confidence
model_status
model_version
top_drivers
data_quality
data_provenance

Do not return fabricated confidence.

==================================================
25. PAHAD FUSION
================

Preserve:

FoS
rainfall threshold
event probability
seismic signal
ground anomaly
satellite/InSAR
terrain
historical context

Keep event probability and CRI separate.

Example:

EVENT PROBABILITY:
72%

CRI:
68 / 100

FoS:
1.04

These are different measurements.

==================================================
26. ALERT SAFETY
================

Do not automatically create a public RED alert from the event classifier alone.

Maintain:

prediction
→ verification
→ alert recommendation
→ authorization
→ public dispatch

Keep the existing 2-of-3 independent confirmation rule.

==================================================
27. DATA SUFFICIENCY UI
=======================

Do not redesign the dashboard.

Only add a small model-data status area:

PAHAD AI EVENT MODEL

Training samples:
XX real

Historical events:
XX

Data span:
YYYY–YYYY

Validation:
Temporal holdout

Status:
TRAINED_LIMITED_DATA

This must use actual values.

==================================================
28. MODEL STATUS API
====================

Add:

GET /api/pahad/event-model/status

Return:

model_status
model_version
training_rows
real_event_rows
validation_rows
forecast_horizons
training_date
dataset_hash
metrics_summary

==================================================
29. DATA QUALITY API
====================

Add:

GET /api/pahad/event-model/data-quality

Return:

event_count
control_count
date_range
states
districts
feature_completeness
missing_features
provenance_summary

==================================================
30. TESTS

Create or update:

tests/test_event_data_quality.py
tests/test_event_labeling.py
tests/test_event_leakage.py
tests/test_event_training.py
tests/test_event_validation.py
tests/test_event_calibration.py
tests/test_event_api.py
tests/test_model_registry.py

Test:

* provenance
* label integrity
* temporal split
* leakage detection
* model loading
* model version
* dataset hash
* probability bounds
* calibration
* API contract
* missing features
* model status
* alert safety

==================================================
31. REGRESSION TESTS

Run all existing tests.

Especially:

tests/test_pahad_engine.py
tests/test_pahad_phase2.py
tests/test_pahad_phase3.py
tests/test_pahad_data_fusion.py
tests/test_weather_service.py
tests/test_seismic_service.py
tests/test_terrain_api.py
tests/test_i18n_localization.py
tests/test_model_regression.py

Do not modify existing tests simply to make failures disappear.

If a regression occurs, fix the implementation.

==================================================
32. NO SYNTHETIC PERFORMANCE CLAIMS
===================================

This is mandatory.

A synthetic/demo dataset may be useful to test that the code executes.

It must NEVER be used to claim:

* production accuracy
* real-world recall
* real-world precision
* real-world AUC
* real-world early-warning lead time

Clearly label demo results:

[DEMO]

==================================================
33. FINAL REPORT

Create:

docs/PAHAD_PHASE3_1_REPORT.md

Include:

1. Real event count
2. Control count
3. Geographic coverage
4. Time coverage
5. Feature count
6. Missingness
7. Model type
8. Model version
9. Validation method
10. Calibration method
11. Actual metrics
12. Warning lead time
13. Model limitations
14. Dataset limitations
15. Remaining external data requirements

==================================================
34. CRITICAL ACCEPTANCE CRITERIA

Phase 3.1 is successful only if:

[ ] real and synthetic samples are separated

[ ] event labels are traceable

[ ] leakage checker exists

[ ] temporal validation exists

[ ] dataset provenance is explicit

[ ] event probability is separate from FoS

[ ] calibrated probability exists when statistically justified

[ ] model version is tracked

[ ] dataset hash is tracked

[ ] operational metrics are calculated

[ ] limitations are visible

[ ] existing regression tests still pass

==================================================
35. DO NOT DO THESE THINGS

Do NOT:

* invent landslide events
* fabricate historical weather
* call synthetic samples "real"
* call a GBDT an LSTM
* call FoS prediction event prediction
* claim 100% accuracy as proof of deployment readiness
* fabricate satellite observations
* fabricate sensor observations
* silently fill historical missing data
* remove tests
* rewrite the entire application

==================================================
36. FINAL STATUS

At the end report exactly:

FOs MODEL:
EXISTING / UPDATED

EVENT MODEL:
TRAINED / LIMITED / INSUFFICIENT / DEMO

LSTM:
TRAINED / NOT TRAINED

REAL HISTORICAL EVENTS:
N

REAL TRAINING SAMPLES:
N

VALIDATION SAMPLES:
N

TEST SAMPLES:
N

BEST ACTUAL METRICS:
...

MEDIAN WARNING LEAD TIME:
...

MODEL STATUS:
...

DO NOT call the event model "production-ready" unless the evidence supports that conclusion.

IMPLEMENT PHASE 3.1 NOW.
# PARVAT NETRA — Core Project Constitution & Agent Rules

This document establishes the binding architectural and engineering rules for all autonomous AI agents working within the **PARVAT NETRA** repository.

---

## 1. Project Mission & Identity
- **Project**: PARVAT NETRA — NER Sentinel
- **Tagline**: “See the risk. Act before the disaster.”
- **Standard**: Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform.
- **Paradigm**: **Predict → Detect → Explain → Warn → Prioritise → Respond → Recover**

---

## 2. The Core Technical Invariant: Multimodal Evidence Fusion
PARVAT NETRA never relies on single-threshold heuristics or unexplainable black-box AI. All risk scores must correlate:
1. **Physical Mechanics**: Infinite Slope Factor of Safety (FoS) based on Mohr-Coulomb shear strength.
2. **In-Situ Geotechnical Telemetry**: Piezometer pore-water pressure, borehole inclinometer displacement, tilt, and vibration.
3. **Precipitation**: Real-time rainfall intensity + 24h/72h Antecedent Precipitation Index (API).
4. **Earth Observation**: InSAR satellite deformation velocities and vegetation loss.
5. **Computer Vision**: CCTV/drone tension crack and mudflow detection.
6. **Community Intelligence**: Geo-tagged verified citizen reports.

Every warning MUST be accompanied by an **Explainability Breakdown ("Why")** showing exact modality contribution percentages.

---

## 3. Strict Visual & Design Guidelines
- **Atmosphere**: Calm, scientific, operational, national emergency authority grade.
- **Theme**: Deep obsidian slate (`#070B10` to `#0F172A`) with crisp, high-contrast typography (`Inter` + `JetBrains Mono` for telemetry).
- **PROHIBITED TROPES**:
  - NO cyberpunk neon glows or grid scans.
  - NO video-game target reticles or decorative HUDs.
  - NO heavy glassmorphism blurring critical sensor curves.
  - NO decorative, meaningless AI animation widgets.

---

## 4. Data Honesty & Provenance Protocol
Never fabricate live connectivity. Every metric, map layer, and incident feed must display an explicit provenance badge:
- `[LIVE]`: Authenticated real-time sensor/API feed.
- `[SIMULATED]`: Statistically realistic physics simulation based on historical rainfall.
- `[HISTORICAL]`: Archival ground truth from GSI/IMD records.
- `[DEMO]`: Synthetic walkthrough sequence for evaluator inspection.

---

## 5. Safe Routes Engine Invariants
1. Provides **FASTEST**, **SHORTEST**, and **SAFEST** (hazard-aware cost optimization).
2. Selecting a route updates the vector layer dynamically; **never reload the whole page or remount the map**.
3. If external routing APIs (Mapbox/Google) are unavailable, fall back deterministically to the local PostGIS geometric road network graph. **Never render straight-line routes.**

---

## 6. Security & Credential Isolation
- All secrets, tokens, and database passwords belong in `.env`.
- Never hardcode credentials into source code, test files, or MCP configs.
- Run `python mcp/scripts/validate_config.py` to confirm zero leaks before committing.

---

## 7. OmniRoute Local AI Gateway Protocol
- OmniRoute runs locally on `http://localhost:20128` (OpenAI-compatible inference base: `http://localhost:20128/v1`).
- Used for natural language SitRep synthesis, multilingual safety broadcasts (Nepali, Lepcha, Bhutia, Hindi, English), and tactical decision intelligence.
- **Fail-Safe Invariant**: Never block or halt platform telemetry if OmniRoute is offline. Services must gracefully fall back to deterministic geotechnical formulas with transparent provenance badges (`[LIVE / DETERMINISTIC]`).

---

## 8. Specialized AI Agent Swarm
The repository deploys five specialized engineering and operational agents in `.agents/agents/`:
1. **`geotechnical_physics_agent`**: Mohr-Coulomb shear strength, Factor of Safety ($FoS$), pore-water pressure, and slope mechanics.
2. **`gis_hydrology_sentinel_agent`**: PostGIS spatial queries, Sentinel-1 InSAR LOS ground deformation, and CWC Teesta river hydrometry.
3. **`tactical_evacuation_routing_agent`**: BRO mountain highway corridors (NH-10, NH-717A bypasses), Dijkstra/A* multi-modal hazard penalty graphs, and relief convoy staging.
4. **`multi_source_triage_coordinator`**: Citizen field evidence clustering, drone/CCTV vision crack apertures, automated SDRF/NDRF dispatch, and OASIS CAP v1.2 alerts.
5. **`omniroute_agent_bridge`**: OmniRoute LLM gateway orchestration, multilingual translations, structured output validation, and local resilience.

