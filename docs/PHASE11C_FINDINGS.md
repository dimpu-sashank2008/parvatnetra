# PARVAT NETRA / PAHAD AI — PHASE 11C FORENSIC FINDINGS
**Standard: Smart India Hackathon (SIH) 2026 Pre-Submission Forensic Hardening**

---

## 1. Summary of Forensic Findings

| Checkpoint | Category | Audit Result | Forensic Observation |
|---|---|:---:|---|
| **CP01** | Baseline | **RECORDED** | Git commit `4c439af`, Python 3.11.0, Node v24.19.0. |
| **CP02** | Data Pipeline Inventory | **VERIFIED** | Complete mapping created in `docs/PHASE11C_DATA_FLOW_MAP.md`. 15 distinct data streams traced from raw sensor/satellite/weather inputs to inference, CRI, and UI. |
| **CP03** | Data Provenance Audit | **VERIFIED** | Provenance tags strictly enforced (`[LIVE]`, `[CACHED]`, `[HISTORICAL]`, `[MODELLED]`, `[SIMULATED]`, `[BENCH_VALIDATED]`, `[MISSING]`). Zero simulated or demo data represented as live. |
| **CP04** | API Contract Audit | **VERIFIED** | Full audit completed in `docs/PHASE11C_API_CONTRACT_AUDIT.md`. Actuation endpoints (`/api/siren/activate`, `/api/notifications/dispatch`) enforce statutory authentication gates. |
| **CP05** | Model Loading Forensics | **VERIFIED** | Runtime loads `models/pahad_event_model.pkl` (and horizon-specific `.pkl` when available). Platt calibrator and GBDT base model verified. SHA-256 matches baseline. |
| **CP06** | Feature Alignment | **VERIFIED** | 34 features in `models/pahad_event_model.pkl` align with `data/features/real_train.csv`. Missing features are mapped to training-split medians with explicit `imputed=True` flags. |
| **CP07** | Missing-Data Audit | **VERIFIED** | Missing weather, seismic, terrain, or IoT data triggers graceful degradation: data quality drops to `DEGRADED DATA` ($DQ=0.289$), confidence drops to `LOW_CONFIDENCE`, and fail-closed alert suppression is enforced. |
| **CP08** | Temporal Data Audit | **VERIFIED** | Partitions verified: Train ($\le 2023$), Val (H1 2024), Test (H2 2024). Strict temporal holdout with zero train/test leakage (`tr['timestamp'].max() < val['timestamp'].min() < val['timestamp'].max() < te['timestamp'].min()`). |
| **CP09** | Event Model Reproduction | **VERIFIED** | Re-evaluated existing model on held-out test partition ($N=8$): ROC-AUC = 1.0, Brier Score = 0.0824, Precision = 1.0, Recall/POD = 1.0, FAR = 0.0, CSI = 1.0. 100% bit-for-bit match with `models/pahad_event_metrics.json`. |
| **CP10** | FoS Data Flow | **VERIFIED** | Evaluated on representative corridors (`SK-NH10-KM48`, `ML-SONAPUR-01`, `AS-GUWAHATI-01`, `AR-BHALUK-01`, `NL-DZUDZA-01`). Physical Infinite Slope Mohr-Coulomb equation matches REST API output bit-for-bit (e.g. Sonapur: 0.926, NH-10: 0.971). |
| **CP11** | CRI Data Flow | **VERIFIED** | Authoritative formula verified: $H = 0.40S + 0.35P + 0.25A$; $\text{CRI} = H \times V \times 100$. False-alarm suppression automatically downgrades raw CRI $\ge 80$ to $79.9$ (`VERY_HIGH`) if $<2$ independent signals trigger. |
| **CP12** | Risk Band Consistency | **VERIFIED** | Continuous bands verified: 0–20 (LOW), 20–40 (MODERATE), 40–60 (HIGH), 60–80 (VERY_HIGH), 80–100 (EXTREME). Boundary transitions at 20, 40, 60, 80 confirmed across API and frontend. |
| **CP13** | Highest-Risk Corridor | **VERIFIED** | `/api/pahad/highest-risk-corridor` dynamically evaluates all 26 canonical corridors across the 8 NER states. Top corridor currently selected: `SK-NH10-KM48` (CRI 47.90, Band HIGH, FoS 0.971). Deterministic tie-breaker verified. |
| **CP14** | Corridor Isolation | **VERIFIED** | Severe storm simulation injected into `SK-NH10-KM48` (`rainfall_24h=180mm`, `pore_pressure=42kPa`) increased NH-10 CRI from 47.90 to 58.70, while `AS-GUWAHATI-01` remained completely unaffected (CRI 17.00, FoS 1.125). Zero cross-corridor leakage. |
| **CP15** | Weather Fallback | **VERIFIED** | Provider hierarchy verified: IMD AWS $\to$ Open-Meteo $\to$ PostGIS $\to$ Calibrated Simulation. Live Open-Meteo feed properly badged as `[LIVE]`. Simulation explicitly badged as `[SIMULATED]`. |
| **CP16** | Seismic Fallback | **VERIFIED** | NCS $\to$ USGS $\to$ Calibrated Fault Simulator. USGS live feed badged as `[LIVE]`. Synthetic earthquakes carry `SIM-` prefix and are strictly badged as `[SIMULATED]`. |
| **CP17** | Terrain / DEM / Satellite | **VERIFIED** | Copernicus GLO-30 30m raster and surveyed GSI Swastik baseline verified. InSAR ground deformation velocity functions as spatial hazard conditioning prior without claiming real-time radar processing. |
| **CP18** | IoT Data Forensics | **VERIFIED** | LoRaWAN / ESP32 bench firmware categorized under `BENCH_SIMULATOR` / `BENCH_VALIDATED` and strictly segregated from physical field deployments. |
| **CP19** | API/UI Value Consistency | **VERIFIED** | Frontend JavaScript (`templates/index.html`) directly consumes API fields (`inf.cri`, `inf.risk_band`, `inf.fos_physical`, `inf.event_probability`, `inf.top_drivers`) without local mutation or fabrication. |
| **CP20** | Unit Consistency | **VERIFIED** | Dimensional analysis verified: $c$ (kPa), $\gamma$ ($\text{kN/m}^3$), $z$ (m), slope (deg $\to$ rad), pore pressure (kPa), rainfall (mm, mm/h). Resulting FoS is dimensionless ($\text{kPa}/\text{kPa}$). |
| **CP21** | Geographic Consistency | **VERIFIED** | All 26 canonical corridors verified within NER bounding box ($20.0^\circ\text{N}\text{--}30.0^\circ\text{N}, 88.0^\circ\text{E}\text{--}98.0^\circ\text{E}$). Coordinate order confirmed as (lat, lon). |
| **CP22** | Time Consistency | **VERIFIED** | All internal timestamps and cache records use UTC ISO 8601 (`datetime.now(timezone.utc).isoformat()`). EOC display converts to IST (+05:30) without shifting prediction windows. |
| **CP23** | Confidence & Data Quality | **VERIFIED** | Dynamic formula verified: $0.50 \cdot \text{provenance} + 0.30 \cdot \text{completeness} + 0.20 \cdot \text{margin} - \text{OOD penalty}$. Degrades mathematically when sensors or external APIs are offline. |
| **CP24** | Safety Boundaries | **VERIFIED** | Fail-closed defaults verified: `ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`, `CAP_PRODUCTION_DISPATCH=0`. Autonomous siren actuation strictly rejected. Human DM sign-off remains mandatory. |
| **CP25** | Minimal Fix Policy | **APPLIED & VERIFIED** | Fixed coordinate omission fallback in `/api/pahad/live-inference` and `/api/pahad/forecast`: when `latitude`/`longitude` are omitted, coordinates are now resolved from `CANONICAL_REGISTRY` using `sector_id` rather than silently defaulting to Sikkim. |
| **CP26** | Regression | **VERIFIED** | All 80 core regression test suites passed (100% pass rate). |
| **CP27** | Final Git Forensics | **VERIFIED** | Working tree inspected; only 1 file modified (`app.py`, 24 insertions, 0 deletions), zero scientific formula alterations, zero model alterations. |
