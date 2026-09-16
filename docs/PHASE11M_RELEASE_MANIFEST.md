# PARVAT NETRA / PAHAD AI — PHASE 11M
## OFFICIAL RELEASE MANIFEST & FILE INVENTORY
**SIH 2026 — TOP-500 → TOP-5 SUBMISSION READINESS**

---

### Release Identification
- **Project Name:** PARVAT NETRA / PAHAD AI
- **Release Candidate:** Phase 11M Submission Candidate
- **Base Commit:** `dbde2f70f9f72f3ae55dcbad1a25e8c4ced836fb` (Base: `4c439af`)
- **Active Branch:** `main`
- **Classification Schema:**
  - `REQUIRED`: Mission-critical core application code, verified models, canonical schemas, or production tests.
  - `OPTIONAL`: Ancillary tools, development utility scripts, auxiliary visualization aids, or alternative connectors.
  - `DEMO ONLY`: Synthetic simulation harnesses, demo walkthrough scripts, or simulated sensor feed drivers (strictly isolated from operational inference).
  - `NOT FOR RELEASE`: Scratchpad scripts, temporary test traces, private environment files, or staging notes.

---

### 1. SOURCE CODE (`src/`, `engine/`, `services/`, `templates/`, `static/`)

| File / Component Path | Category | Release Classification | Description / Purpose |
| :--- | :--- | :--- | :--- |
| `app.py` | Core Application Entrypoint | `REQUIRED` | Flask / ASGI application hosting runtime endpoints, API routes, and UI templates |
| `engine/pahad_engine.py` | Geotechnical & Event Engine | `REQUIRED` | Deterministic Infinite Slope FoS, CRI multi-factor fusion, and ML classifier pipeline |
| `engine/pahad_lstm.py` | Temporal Predictor | `REQUIRED` | Explicit mathematical surrogate for temporal sequence risk decay (`NOT_TRAINED / SURROGATE`) |
| `services/weather_service.py` | Weather Telemetry Client | `REQUIRED` | Open-Meteo live API integration, IMD fallback adapter, caching layer |
| `services/seismic_service.py` | Seismological Client | `REQUIRED` | USGS real-time GeoJSON client, NCS fallback handler, regional bounding box query |
| `services/alert_service.py` | Alert & Verification Hub | `REQUIRED` | 2-of-3 corroboration engine, authority role validation, fail-closed dispatch safeguards |
| `services/pahad_voice_assistant.py` | Voice Telemetry Assistant | `REQUIRED` | Multilingual situational reporting and interactive Q&A assistant |
| `services/terrain_service.py` | Terrain & Topography | `REQUIRED` | Digital Elevation Model (DEM) slope, aspect, and curvature calculation service |
| `templates/index.html` | UI Dashboard View | `REQUIRED` | Command dashboard displaying corridor telemetry, FoS, CRI, and provenance badges |
| `templates/terrain_3d.html` | UI 3D Terrain View | `REQUIRED` | 3D topographical slope and elevation profile visualization |
| `templates/climate_map.html` | UI Climate Map View | `REQUIRED` | Rainfall, antecedent precipitation, and moisture contour mapping |
| `templates/seismic.html` | UI Seismic View | `REQUIRED` | Live USGS seismic event map and regional historical hypocenters |
| `public/static/` / `static/` | UI Static Assets | `REQUIRED` | CSS styling, vendor JavaScript libraries (Leaflet, Three.js, Chart.js), font assets |

---

### 2. TRAINED MODELS & RUNTIME ARTIFACTS (`models/`)

| Artifact Path | Artifact Type | Classification | Provenance & Validation |
| :--- | :--- | :--- | :--- |
| `models/pahad_event_model.pkl` | Binary Event Classifier | `REQUIRED` | GradientBoostingClassifier (16 train rows, 12 val, 8 test). Status: `TRAINED_LIMITED_DATA` |
| `models/pahad_event_model.metadata.json`| Model Metadata | `REQUIRED` | Training parameters, features, validation strategy, dataset SHA-256 hash |
| `models/pahad_event_metrics.json` | Model Validation Metrics | `REQUIRED` | Documented test metrics, confusion matrix, POD, FAR, CSI |
| `models/pahad_fos_surrogate.pkl` | Geotechnical Surrogate | `REQUIRED` | Fast polynomial surrogate for infinite slope Factor of Safety approximation |
| `models/pahad_fos_metadata.json` | FoS Model Metadata | `REQUIRED` | Parameter bounds, training features, physics error bounds ($R^2 > 0.99$) |
| `models/calibrator_isotonic.pkl` | Probability Calibrator | `REQUIRED` | Non-parametric isotonic probability calibrator |
| `models/calibrator_platt.pkl` | Probability Calibrator | `REQUIRED` | Parametric logistic Platt scaling calibrator |
| `models/calibration_metadata.json` | Calibration Metadata | `REQUIRED` | Brier score, Expected Calibration Error (ECE) metrics |
| `models/scaler.pkl` | Feature Preprocessing | `REQUIRED` | Standard feature normalizer fitted exclusively on training split |
| `models/feature_metadata.json` | Feature Schema | `REQUIRED` | 13-feature canonical input schema, data types, and default imputation policies |

---

### 3. DATASETS, MANIFESTS & GROUND TRUTH (`data/`)

| Dataset / Manifest Path | Format | Classification | Provenance & Description |
| :--- | :--- | :--- | :--- |
| `data/features/real_train.csv` | CSV Feature Table | `REQUIRED` | 16 temporal observation windows (8 event, 8 control) from 2020–2022 historical records |
| `data/features/real_val.csv` | CSV Feature Table | `REQUIRED` | 12 temporal observation windows (6 event, 6 control) from 2023 historical records |
| `data/features/real_test.csv` | CSV Feature Table | `REQUIRED` | 8 temporal observation windows (3 event, 5 control) from 2024 historical records |
| `data/manifests/canonical_event_inventory.json` | JSON Manifest | `REQUIRED` | 17 verified historical landslide events with GSI/NDMA incident coordinates & dates |
| `data/manifests/phase11k_demo_scenarios.json` | JSON Manifest | `REQUIRED` | 3 canonical live corridor scenarios (NH-10 Km 48, Dzüdza, Piphema) |
| `data/cache/weather/` | JSON Cache Files | `REQUIRED` | Cached weather API telemetry for offline resiliency and deterministic testing |
| `data/cache/seismic/` | JSON Cache Files | `REQUIRED` | Cached seismic USGS telemetry for offline resiliency and deterministic testing |
| `data/features/demo_train.csv` | CSV Feature Table | `DEMO ONLY` | Synthetic expansion samples quarantined for UI demonstration only (`PAHAD_DEMO_MODE=1`) |
| `data/raw/` | Raw Archival Records | `OPTIONAL` | Unprocessed source reports from geological and meteorological portals |

---

### 4. TEST SUITES & VERIFICATION HARNESSES (`tests/`)

| Test File Path | Scope | Classification | Verification Purpose |
| :--- | :--- | :--- | :--- |
| `tests/test_pahad_engine.py` | Geotechnical & Fusion | `REQUIRED` | Verifies infinite slope FoS math, CRI bounds [0, 100], and weight conservation |
| `tests/test_pahad_phase2.py` | Phase 2 Multi-corridor | `REQUIRED` | Verifies all 26 corridor geometries, regional boundaries, and baseline telemetry |
| `tests/test_pahad_phase3.py` | Phase 3 Core Engine | `REQUIRED` | Verifies event probability bounds [0, 1], feature normalization, and pipeline integrity |
| `tests/test_pahad_data_fusion.py` | Evidence Fusion Engine | `REQUIRED` | Verifies 2-of-3 multi-modal corroboration, CRI formulation, and edge cases |
| `tests/test_weather_service.py` | Weather API Client | `REQUIRED` | Verifies Open-Meteo schema handling, cache hit/miss, and rate-limit fallbacks |
| `tests/test_seismic_service.py` | Seismic API Client | `REQUIRED` | Verifies USGS GeoJSON parsing, magnitude threshold filtering, and caching |
| `tests/test_terrain_api.py` | Topography Engine | `REQUIRED` | Verifies DEM slope matrix extraction, aspect calculation, and elevation profiles |
| `tests/test_i18n_localization.py` | Multilingual UI/Voice | `REQUIRED` | Verifies English, Hindi, Nepali, and regional localization string mappings |
| `tests/test_model_regression.py` | Model Stability | `REQUIRED` | Verifies inference repeatability, bit-exact outputs, and absence of NaN/Inf |
| `tests/test_phase11j_smoke.py` | Production Deployment | `REQUIRED` | Verifies asset availability, fail-closed safety flags, and endpoint contracts |
| `tests/test_phase7g_rbac.py` | Security & RBAC | `REQUIRED` | Verifies role permissions, unauthorized request rejection, and authority controls |
| `tests/test_phase10d_voice_hardening.py` | Voice Assistant | `REQUIRED` | Verifies rate limits, input sanitization, and fallback synthesized reports |
| `tests/test_event_leakage.py` | Scientific Integrity | `REQUIRED` | Verifies zero feature leakage across temporal holdout partitions |

---

### 5. CONFIGURATION & DEPLOYMENT SPECS

| Configuration File Path | Classification | Role in Release |
| :--- | :--- | :--- |
| `requirements.txt` | `REQUIRED` | Pinned Python dependency manifest for runtime reproducibility |
| `runtime.txt` | `REQUIRED` | Pinned Python runtime specification (`python-3.11.0`) |
| `.env.example` | `REQUIRED` | Template configuration declaring all required environment variables and safety locks |
| `render.yaml` | `REQUIRED` | Infrastructure-as-code deployment blueprint for containerized web hosting |
| `vercel.json` | `REQUIRED` | Serverless build and routing configuration for Vercel deployment |
| `.gitignore` | `REQUIRED` | Repository exclusion policy ensuring zero secrets or scratch files are tracked |
| `.env` (Local Instance) | `NOT FOR RELEASE` | Local runtime secrets and environment variables (Must remain gitignored) |

---

### 6. DEMONSTRATION & EVALUATION HARNESSES (`scripts/`)

| Script / Harness Path | Classification | Operational Role |
| :--- | :--- | :--- |
| `scripts/simulate_sensor_stream.py` | `DEMO ONLY` | Standalone IoT sensor telemetry simulator (Dry-run only, strictly isolated from production DB) |
| `scripts/verify_phase11m_model_hashes.py`| `OPTIONAL` | Utility script to verify SHA-256 integrity of release model weights |
| `scripts/verify_phase11m_data_hashes.py` | `OPTIONAL` | Utility script to verify SHA-256 integrity of training and validation datasets |
| `scripts/generate_phase11m_snapshot.py` | `OPTIONAL` | Utility script to enumerate all 26 corridors and generate runtime snapshot |
| `scripts/check_event_leakage.py` | `REQUIRED` | Automated validation gate checking temporal partitions for data leakage |

---

### 7. AUDIT & FORENSIC REPORTS (`docs/`, `reports/`)

| Document / Report Path | Classification | Authority & Significance |
| :--- | :--- | :--- |
| `docs/PHASE11M_FINAL_SUBMISSION_FREEZE.md` | `REQUIRED` | Master Phase 11M submission freeze and release candidate audit report |
| `docs/PHASE11M_FINAL_EVIDENCE_INDEX.md` | `REQUIRED` | Master claim-to-evidence matrix mapping 20 core evaluation assertions |
| `docs/PHASE11M_FINAL_FREEZE_BASELINE.md` | `REQUIRED` | Git repository commit and worktree baseline record |
| `reports/PHASE11M_RELEASE_CANDIDATE.json` | `REQUIRED` | Machine-readable release candidate metadata and integrity digests |
| `reports/PHASE11M_FINAL_RUNTIME_SNAPSHOT.json` | `REQUIRED` | Canonical runtime telemetry snapshot across all 26 evaluated corridors |
| `reports/PHASE11M_FINAL_MODEL_HASHES.json` | `REQUIRED` | SHA-256 verification log for all 10 trained model binaries |
| `reports/PHASE11M_FINAL_DATA_HASHES.json` | `REQUIRED` | SHA-256 verification log for all release-critical datasets |
| `docs/PHASE11L_SIH_JUDGE_DEFENSE.md` | `REQUIRED` | 37-section technical defense handbook for hostile SIH judge questioning |
| `docs/PHASE11K_JUDGE_DEMO_SCRIPT.md` | `REQUIRED` | Turn-by-turn 6m 15s evaluation demonstration script |
| `docs/PAHAD_MODEL_CARD.md` | `REQUIRED` | Authoritative AI model card detailing intended use, limitations, and provenance |
