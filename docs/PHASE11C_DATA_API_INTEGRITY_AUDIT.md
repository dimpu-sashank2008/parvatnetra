# PARVAT NETRA / PAHAD AI — PHASE 11C DATA, API & PREDICTION INTEGRITY FORENSIC AUDIT
**Standard: Smart India Hackathon (SIH) 2026 Pre-Submission Hardening**  
**Classification: Comprehensive Forensic Data, API, and Prediction Audit**  
**Audit Baseline Verdict: `INTEGRITY_PASS_WITH_LIMITATIONS` (Phase 11H)**

---

## 1. Executive Summary

Phase 11C conducted a rigorous, forensic audit of the end-to-end data pipeline, API contracts, geotechnical physics, machine-learning event classification, feature alignment, and user-interface representations across the PARVAT NETRA / PAHAD AI platform.

All strict constraints were maintained:
- **Zero algorithmic changes**: FoS, CRI, and empirical rainfall threshold formulas were untouched.
- **Zero model retraining**: All model artifacts in `models/` maintain exact SHA-256 hash identity.
- **Zero test manipulation**: All 80 core regression tests and 52 satellite/corridor tests passed without alteration.
- **Fail-Closed Safety Invariants Preserved**: `ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`, `CAP_PRODUCTION_DISPATCH=0`.
- **Single Minimal Fix Applied**: Improved coordinate resolution in `/api/pahad/live-inference` and `/api/pahad/forecast` so that when `latitude`/`longitude` are omitted, coordinates are dynamically resolved from `CANONICAL_REGISTRY` using `sector_id` instead of defaulting to Sikkim coordinates.

---

## 2. Baseline Architecture & State

- **Baseline Git Commit:** `4c439af`
- **Branch:** `main`
- **Python Version:** Python 3.11.0 (Windows x64)
- **Node Runtime:** v24.19.0
- **Safety Interlocks:** `ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`, `CAP_PRODUCTION_DISPATCH=0`
- **Baseline Report:** Documented in `docs/PHASE11C_DATA_API_BASELINE.md`.

---

## 3. Data Flow Inventory

The complete data pipeline was traced and documented in `docs/PHASE11C_DATA_FLOW_MAP.md`:
1. **Raw Sensor & External Feeds:** Open-Meteo REST API, USGS GeoJSON, Copernicus GLO-30 DEM, Sentinel-1 InSAR catalog, LoRaWAN IoT telemetry packets, and citizen incident reports.
2. **Ingestion & Normalization:** Handled by `services/` connectors (`WeatherService`, `SeismicService`, `DEMService`, `EdgeGateway`) writing to in-memory/disk caches and `data/observations/pahad_observations.db`.
3. **Feature Assembly:** `_assemble_features()` in `engine/pahad_live_inference.py` constructs clean vectors with explicit missing-feature markers.
4. **Dual Model Inference:**
   - **Model A (Geotechnical Mechanics):** Computes physical Mohr-Coulomb Factor of Safety ($FoS$).
   - **Model B (Event Classification):** Computes calibrated probability of failure ($P(\text{event}) \in [0, 1]$).
5. **Multimodal Fusion:** `PahadFusionEngine` computes Composite Risk Index ($CRI = H \times V \times 100$) with false-alarm suppression.
6. **API & UI Delivery:** Dispatched through Flask REST blueprints to `templates/index.html`.

---

## 4. Data Provenance Audit

All data streams enforce strict, truthful provenance badges:
- `[LIVE]`: Authenticated real-time meteorological or seismic API query within freshness limits.
- `[CACHED]`: Local disk or memory cache with explicit `data_age_seconds`.
- `[HISTORICAL]`: Verified GSI landslide compendium or PostGIS archival observation records.
- `[MODELLED]`: Geotechnical infinite-slope calculation or canonical corridor registry baseline.
- `[SIMULATED]`: Physics-grounded simulation fallback. Explicitly badged as `[SIMULATED]` (never as `[LIVE]`).
- `[BENCH_VALIDATED]`: ESP32/LoRa hardware testrig under isolated bench conditions. Strictly segregated from field deployment.
- `[MISSING]`: Unobserved telemetry slots populated with training medians and flagged `imputed=True`.

---

## 5. API Contract Audit

Full audit detailed in `docs/PHASE11C_API_CONTRACT_AUDIT.md`:
- Public read endpoints (`/api/pahad/live-inference`, `/api/pahad/forecast`, `/api/pahad/highest-risk-corridor`, `/api/pahad/data-status`) return consistent JSON schemas and handle invalid parameters with HTTP 422.
- Actuation endpoints (`/api/siren/activate`, `/api/authority/review`) strictly enforce HMAC dual-key authority tokens and officer session authentication (HTTP 401/403 on unauthenticated attempts).
- Fail-closed defaults ensure `SIREN_DRY_RUN=1` and `ENABLE_PUBLIC_DISPATCH=0` cannot be bypassed.

---

## 6. Model Loading Forensics

- **Runtime Artifact:** `models/pahad_event_model.pkl` (SHA-256: `d2094eae9ee6906f5197af5b2fdeb671d6a571080c7f63985b92b95c82ede938`).
- **Base Algorithm:** `GradientBoostingClassifier` with Platt Sigmoid Probability Calibration (`CalibratedClassifierCV`).
- **Target Variable:** `landslide_event_probability`.
- **Model Status:** Formally tracked as `TRAINED_LIMITED_DATA` (`DATA-GROUNDED RESEARCH PROTOTYPE`).
- **Fallback:** If individual horizon models are requested, system loads `models/pahad_event_model_{H}h.pkl` or safely falls back to the calibrated 24h baseline.

---

## 7. Feature Alignment

- **Training vs Model Schema:** Exactly 34 input features in `models/pahad_event_model.pkl` align with `data/features/real_train.csv`.
- **Feature Ordering:** Model loads ordered column list from artifact (`feature_columns`) ensuring deterministic matrix ordering.
- **Missing Value Handling:** Missing features are populated with central tendencies of the $N=16$ historical baseline, marked with `imputed=True` and provenance `MISSING`.

---

## 8. Missing-Data Audit

Evaluated 5 missing data scenarios:
1. Missing rainfall: Triggers `data_quality_level = "DEGRADED DATA"` ($DQ=0.289$), `LOW_CONFIDENCE`.
2. Missing seismic: Gracefully defaults to zero ground shaking proxy; status intact.
3. Missing terrain: Resolves surveyed GSI Swastik baseline from canonical registry.
4. Missing IoT: Piezometer/tiltmeter marked `MISSING`; uses conservative training medians.
5. All sensor data missing: System continues execution without crashing, marks all inputs as imputed, degrades confidence to `LOW_CONFIDENCE`, and suppresses autonomous alert triggers.

---

## 9. Temporal Integrity & Partitioning

- **Partitions:**
  - Training: 16 samples ($\le 2023\text{-}10\text{-}04$)
  - Validation: 12 samples ($2024\text{-}02\text{-}14$ to $2024\text{-}06\text{-}25$)
  - Test: 8 samples ($2024\text{-}07\text{-}02$ to $2024\text{-}10\text{-}04$)
- **Leakage Status:** **ZERO LEAKAGE**. Partitions are strictly non-overlapping in time:
  $$\max(T_{\text{train}}) < \min(T_{\text{val}}) < \max(T_{\text{val}}) < \min(T_{\text{test}})$$
- **Quarantine:** 25 synthetic records isolated in `demo_train.csv` (active only under `PAHAD_DEMO_MODE=1`).

---

## 10. Event Model Reproduction

Evaluated existing calibrated event model on held-out test partition ($N=8$):
- **Sample 0 (`MN-TAMENG-01`):** True=1, $P=0.8331$, Pred=1
- **Sample 1 (`ML-SHILLONG-01`):** True=1, $P=0.8331$, Pred=1
- **Sample 2 (`CTRL-AS-HEAVY-01`):** True=0, $P=0.4021$, Pred=0
- **Sample 3 (`CTRL-ML-HEAVY-01`):** True=0, $P=0.4233$, Pred=0
- **Sample 4 (`CTRL-AR-HEAVY-01`):** True=0, $P=0.4233$, Pred=0
- **Sample 5 (`TR-JAMPUI-01`):** True=1, $P=0.8331$, Pred=1
- **Sample 6 (`NL-KOHIMA-01`):** True=1, $P=0.8331$, Pred=1
- **Sample 7 (`SK-NH10-KM48`):** True=1, $P=0.8331$, Pred=1

**Empirical Metrics:**
- ROC-AUC: **1.000**
- Brier Score: **0.0824** (exact match to `models/pahad_event_metrics.json`)
- Confusion Matrix: $TP=5, TN=3, FP=0, FN=0$
- Precision: 1.0, Recall/POD: 1.0, FAR: 0.0, CSI: 1.0
- **Reproduction Result: 100% BIT-FOR-BIT PERFECT MATCH**.

---

## 11. FoS Data Flow

Evaluated on 5 representative corridors:
- `SK-NH10-KM48`: Engine FoS = 0.9710, API FoS = 0.9710 (CRITICAL)
- `ML-SONAPUR-01`: Engine FoS = 0.9260, API FoS = 0.9260 (CRITICAL)
- `AS-GUWAHATI-01`: Engine FoS = 1.1250, API FoS = 1.1250 (MARGINAL)
- `AR-BHALUK-01`: Engine FoS = 0.9400, API FoS = 0.9400 (CRITICAL)
- `NL-DZUDZA-01`: Engine FoS = 1.0280, API FoS = 1.0280 (MARGINAL)
- **Status:** **VERIFIED**. Direct Mohr-Coulomb limit equilibrium matches REST API output bit-for-bit. Zero hard-coding or clamping.

---

## 12. CRI Data Flow

Authoritative formulation verified across `backend/risk_engine.py` and `engine/pahad_fusion.py`:
$$H = 0.40 \cdot S + 0.35 \cdot P + 0.25 \cdot A$$
$$\text{CRI} = H \times V \times 100$$
Constitutional 2-of-3 signal confirmation rule auto-downgrades raw CRI $\ge 80.0$ to $79.9$ (`VERY_HIGH`) if fewer than 2 independent signals (FoS $\le 1.0$, Regional I-D Exceeded, ML $P > 0.80$) confirm instability.

---

## 13. Risk Bands Consistency

- **0.0–20.0:** LOW
- **20.0–40.0:** MODERATE
- **40.0–60.0:** HIGH
- **60.0–80.0:** VERY_HIGH
- **80.0–100.0:** EXTREME
- **Transitions:** Exact boundary behavior at 20.0, 40.0, 60.0, and 80.0 verified. API and frontend UI colors match.

---

## 14. Highest-Risk Corridor Forensics

- **API Endpoint:** `/api/pahad/highest-risk-corridor`
- **Dynamic Scope:** Evaluates all 26 canonical corridors across 8 NER states.
- **Tie-Breaker Rule:** `highest_cri_desc, then lowest_fos_asc, then alphabetical_id`
- **Current Top Corridor:** `SK-NH10-KM48 - NH-10 Km 48 (29th Mile Sector)` (CRI: 47.90, Band: HIGH, FoS: 0.971).
- **Hardcoding Check:** Completely dynamic; changes based on live weather and geotechnical inputs.

---

## 15. Corridor Isolation

- Severe storm injected into `SK-NH10-KM48` (`rainfall_24h=180mm`, `pore_pressure=42kPa`).
- Result: `SK-NH10-KM48` CRI rose from 47.90 to 58.70, while `AS-GUWAHATI-01` remained exactly at baseline CRI 17.00, FoS 1.125.
- **Status:** **PASS**. Zero cross-corridor state leakage.

---

## 16. Weather Fallback Forensics

- IMD API unconfigured $\to$ Falls back to Open-Meteo REST API (`[LIVE]`).
- If Open-Meteo unreachable $\to$ Falls back to PostGIS observations (`[HISTORICAL]`).
- If database unreachable $\to$ Falls back to Eastern Himalayan Climate Simulator (`[SIMULATED]`).
- Stale cache carries `data_age_seconds` and `CACHED` badge.

---

## 17. Seismic Fallback Forensics

- NCS unconfigured $\to$ Falls back to USGS Earthquake Hazards feed (`[LIVE]`).
- Bounding box filter strictly restricted to NER ($20^\circ\text{N}\text{--}30^\circ\text{N}, 88^\circ\text{E}\text{--}98^\circ\text{E}$).
- Synthetic events carry `SIM-` prefix and are strictly tagged as `[SIMULATED]`.

---

## 18. Satellite / DEM Forensics

- DEM: Copernicus GLO-30 30m raster and surveyed GSI Swastik baseline verified.
- InSAR: Sentinel-1 LOS deformation velocity functions as spatial hazard conditioning prior. Does not claim sub-hourly radar processing.

---

## 19. IoT Data Forensics

- ESP32 / LoRaWAN firmware tested in bench harness categorized as `BENCH_SIMULATOR` / `BENCH_VALIDATED`.
- Never misrepresented as physical highway deployments.

---

## 20. API / UI Value Consistency

- Frontend (`templates/index.html`) directly binds `cri`, `risk_band`, `fos_physical`, `event_probability`, and `top_drivers` from API responses.
- No client-side recalculation or cosmetic divergence.

---

## 21. Unit Consistency

- Cohesion ($c'$): kPa
- Unit weight ($\gamma$): $\text{kN/m}^3$
- Slip depth ($z$): m
- Slope ($\beta$): degrees $\to$ radians
- Pore pressure ($u$): kPa
- Rainfall: mm, intensity mm/h
- FoS: Dimensionless ratio ($\text{kPa}/\text{kPa}$)
- **Status:** Verified.

---

## 22. Geographic Consistency

- All 26 canonical corridors verified within NER bounding box ($20.0^\circ\text{N}\text{--}30.0^\circ\text{N}, 88.0^\circ\text{E}\text{--}98.0^\circ\text{E}$).
- Coordinates verified in standard (lat, lon) order.

---

## 23. Time Consistency

- All internal timestamps, observations, and inference outputs formatted in UTC ISO 8601.
- EOC localized display converts to IST (+05:30) without distorting prediction intervals.

---

## 24. Confidence & Data Quality

- Dynamic formulation verified:
  $$\text{Confidence} = 0.50 \cdot \text{Provenance} + 0.30 \cdot \text{Completeness} + 0.20 \cdot \text{Boundary Margin} - \text{OOD Penalty}$$
- Decreases mathematically under missing or simulated inputs.

---

## 25. Safety Boundaries

- Fail-closed defaults confirmed: `ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`, `CAP_PRODUCTION_DISPATCH=0`.
- Dual-key cryptographic authorization required for siren firing.
- Voice assistant command actuation strictly blocked.

---

## 26. Minimal Fix Applied

- **BEFORE:** In `/api/pahad/live-inference` and `/api/pahad/forecast`, if `latitude` and `longitude` were omitted from query parameters, coordinates defaulted to `(27.33, 88.61)` (Sikkim), even if `sector_id` was `ML-SONAPUR-01` or `AS-GUWAHATI-01`.
- **ROOT CAUSE:** Hardcoded fallback values before querying `CANONICAL_REGISTRY`.
- **CHANGE:** Resolved `sector_id` against `CANONICAL_REGISTRY` first when coordinates are omitted, dynamically assigning the corridor's true latitude and longitude.
- **AFTER:** Queries for registered sectors without explicit lat/lon correctly evaluate their actual geographic location and local weather.
- **TEST:** Tested with auto-resolution, explicit coordinates, and invalid coordinates (422 preserved).

---

## 27. Regression Testing Summary

1. Core regression test suite (9 test suites): **80/80 passed (100% in 64.50s)**.
2. Live inference test suite (`test_live_inference.py`): **40/40 passed (100% in 3.45s)**.
3. UI theme and corridor test suite (`test_ui_theme_and_corridor.py`): **12/12 passed (100% in 5.43s)**.
- **TOTAL PASSED:** 132 / 132 tests. Zero failures, zero errors, zero skips.

---

## 28. Remaining Risks

1. Limited documented landslide training records ($N=16$ train, $N=12$ val, $N=8$ test; `TRAINED_LIMITED_DATA`).
2. Physical field deployment of in-situ borehole instruments pending institutional capital works; prototype uses physics-grounded telemetry simulation alongside live Open-Meteo and USGS data.
3. InSAR surface deformation is archival baseline; near-real-time SAR processing requires dedicated ground station downlink.

---

## 29. Final Verdict

**`DATA_API_INTEGRITY_PASS_WITH_LIMITATIONS`**
