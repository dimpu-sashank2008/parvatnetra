# PAHAD AI — TEMPORAL LEARNING AUDIT & FUTURE DATA INFRASTRUCTURE ROADMAP
**Platform**: PARVAT NETRA / PAHAD AI  
**Phase**: 12A — Scientific Integrity & Temporal Sequence Audit  
**Status**: `LSTM/GRU TRAINING BLOCKED — DATA INSUFFICIENT`  
**Operational Status**: `PAHAD LSTM = PHYSICS-INFORMED TEMPORAL SURROGATE / NOT TRAINED`  
**Date**: September 2026  

---

## 1. Executive Summary & Critical Audit Findings
An exhaustive audit of every temporal, time-series, telemetry, and event dataset across the PARVAT NETRA repository was conducted prior to Phase 12A modeling. The audit established the following empirical facts:

| Audit Parameter | Ground Truth Value | Scientific Implication |
|---|---|---|
| **TEMPORAL_ROWS** | **105** | Total historical antecedent snapshot rows in `phase5b_temporal_full.csv`. |
| **UNIQUE_TIMESTAMPS** | **105** | Episodic disaster timestamps and engineered antecedent snapshots (May 2022 – Oct 2024). |
| **UNIQUE_CORRIDORS** | **17** | 17 monitored strategic sectors across all 8 Northeastern states. |
| **CONTINUOUS_SEQUENCES** | **0** | Zero uninterrupted high-frequency sensor streams ($\Delta t \le 1	ext{h}$) exist in the repository. |
| **EVENT_ALIGNED_SEQUENCES** | **17** | Exactly 17 documented disaster episodes, each with 5 engineered antecedent snapshots ($T=5$). |
| **REAL_SENSOR_ROWS** | **0** | Historical in-situ sensor values (2022–2024) are physically reconstructed from geotechnical limit equilibrium and IMD hydrology because IoT edge hardware was deployed in 2026. |
| **SIMULATED_ROWS** | **20** | 20 non-event control rows tagged `[MODELLED]` in Phase 5B. (An additional 25 synthetic rows exist in `demo_train.csv` strictly isolated under `PAHAD_DEMO_MODE=1`). |
| **MISSINGNESS** | **0.0%** | Zero nulls in the 26 canonical features (values derived from physical formulas and spatial interpolation). |
| **TEMPORAL_COVERAGE** | **May 2022 – Oct 2024** | 29 months of episodic disaster records, not continuous sensor monitoring. |
| **RECOMMENDED_STATUS** | **`KEEP_SURROGATE`** | **DO NOT TRAIN LSTM/GRU**. Preserved as a documented deterministic physics surrogate. |

---

## 2. Binding Decision for Phase 12A
In strict accordance with the Project Constitution (Section 12: "Temporal Deep Learning" & Section 32: "No Synthetic Performance Claims"):

1. **NO LSTM / GRU TRAINING SHALL OCCUR IN PHASE 12A**:
   - A recurrent neural network (such as a 2-layer Bidirectional LSTM with 26 input features and 32 hidden units) contains **$pprox 25,000$ trainable parameters**.
   - The available training partition contains only **8 positive disaster episodes ($N_{train} = 48$ total rows)**.
   - Attempting to optimize 25,000 weights on 8 training events results in severe mathematical over-parameterization, sample memorization, and scientifically fraudulent early-warning claims.
2. **NO DATA FABRICATION**:
   - No interpolation or upsampling of 5-step discrete snapshots shall be passed off as "continuous sensor streams".
   - Modelled historical sensor estimates shall **never** be labeled as "real physical sensor telemetry".
3. **PRESERVATION OF SCIENTIFIC STATUS**:
   - `PAHAD LSTM` in `engine/pahad_lstm.py` remains explicitly classified as:
     `Model Status: NOT_TRAINED (MATHEMATICAL SURROGATE)`
     `Data Provenance: [SIMULATED] NE Himalaya calibration constants`
   - Operational temporal inference for multi-horizon forecast (6h, 12h, 24h, 48h) continues to be powered by the regularized, Platt-calibrated Gradient Boosting classifier (`PAHAD Event Model v1.1` in `models/pahad_event_model.pkl`), which is statistically sound for small-sample Himalayan regimes ($N=36$ real samples).

---

## 3. Full Scientific Core Verification (56/56 Tests Passed)
The existing scientific core was completely verified across 10 specialized test modules with **100% pass rate (56/56 tests passing)**:

1. **Geotechnical Physics Core (`tests/test_pahad_engine.py` - 11/11 PASSED)**:
   - Infinite slope Mohr-Coulomb Factor of Safety ($FoS$) correctly identifies stable ($FoS > 1.5$), watch ($1.0 \le FoS \le 1.2$), and critical failure ($FoS < 1.0$) regimes.
   - Mandal & Sarkar (2021) empirical rainfall threshold curves ($I = 14.82 \cdot D^{-0.39}$) accurately evaluate regional precipitation triggers.
   - CRI risk banding ($0	ext{--}100$) and 2-of-3 corroboration safety interlocks verified.
2. **Multimodal Data Fusion Core (`tests/test_pahad_data_fusion.py` - 7/7 PASSED)**:
   - Evaluates fused risk across piezometer pore pressure, inclinometer tilt, satellite InSAR, and rainfall API.
   - Confirms false alarm suppression: single sensor outliers are prevented from dispatching red evacuation alerts without corroborating evidence.
3. **Calibrated Event Model & Calibration Bounds (`tests/test_event_model.py` & `test_event_calibration.py` - 9/9 PASSED)**:
   - Probability outputs strictly bounded in $[0.0, 1.0]$.
   - Platt scaling calibrator verified on temporal holdout; monotonic response to increasing antecedent rainfall confirmed.
4. **Data Quality, Provenance & Partition Validation (`tests/test_event_data_quality.py` & `test_event_validation.py` - 7/7 PASSED)**:
   - Confirms complete separation of `real_train.csv` (N=16), `real_val.csv` (N=12), `real_test.csv` (N=8) from `demo_train.csv` (N=25).
   - Zero lookahead leakage, zero temporal overlap across partitions.
5. **Environmental & Earth Observation Services (`tests/test_weather_service.py`, `test_dem_service.py`, `test_seismic_service.py`, `test_satellite_service.py` - 22/22 PASSED)**:
   - Copernicus DEM 30m terrain products (slope, elevation, curvature, hillshade).
   - IMD weather parsing, 24h/72h API calculations, offline cache failover.
   - NCS seismic distance and peak ground acceleration (PGA) amplification.
   - Sentinel-1 InSAR line-of-sight velocity parsing with provenance badges.

---

## 4. Exact Requirements for Future Real Temporal Neural Network Training

To transition from the current **Calibrated GBDT + Mathematical LSTM Surrogate** architecture to a **Genuinely Trained Deep Recurrent / Transformer Neural Network (LSTM / GRU / TCN / PatchTST)**, the following five structural requirements must be met:

### 4.1 Sample Volume Requirements
- **Minimum Event Sequences**: A minimum of **$N \ge 500$ independent continuous failure sequences** ($T \ge 48$ hours at 1-hour or 15-minute resolution leading directly to documented mass-wasting events).
- **Control Negative Sequences**: A minimum of **$N \ge 2,000$ continuous non-event sequences** collected during heavy monsoon precipitation events that did *not* result in failure (critical to teach the recurrent network how to distinguish high rainfall without failure from true slope destabilization).
- **Total Sequence Timestamps**: Minimum $120,000+$ contiguous telemetry observations.

### 4.2 In-Situ Telemetry Hardware Cadence
- **Sensors Required per Monitored Slope**:
  1. Vibrating-wire piezometer array (measuring pore-water pressure at 3m, 6m, and slip-surface depth; sampling rate $\le 15	ext{ min}$).
  2. In-place biaxial inclinometer strings (measuring cumulative lateral displacement and shear strain rate; sampling rate $\le 15	ext{ min}$).
  3. High-precision MEMS tiltmeters installed at tension crack crowns (sampling rate $\le 5	ext{ min}$).
  4. Automatic tipping-bucket rain gauge with optical drop counter ($\pm 0.1	ext{mm}$ resolution, continuous 1-hour accumulation).
- **Communication Invariant**: Edge gateways logging cryptographically signed packets with UTC hardware RTC timestamps via LoRaWAN / NB-IoT / SATCOM.

### 4.3 Longitudinal Data Collection Duration
- **Minimum Duration**: At least **2 to 3 complete monsoon cycles (24 to 36 months)** of uninterrupted sensor logging across primary test corridors (e.g. NH-10 Sikkim, NH-29 Nagaland, NH-717A Bengal-Sikkim bypass).
- **Missingness & Outage Protocol**: Edge micro-SD storage buffers must cache and backhaul data across cellular/satellite blackouts to guarantee sequence continuity ($< 2\%$ missingness).

### 4.4 Data Storage & Engineering Infrastructure
- **Time-Series Database**: Migration from flat CSV / JSON caches to an optimized high-throughput time-series database (e.g. **TimescaleDB** hypertables or **InfluxDB**) partitioned by `(sector_id, timestamp)`.
- **Automated Anomaly Filtering**: Real-time automated physical range checks, spike filtering, and sensor drift compensation prior to feature ingestion.
- **Micro-Climate Rainfall Interpolation**: Incorporation of high-resolution X-band Doppler Weather Radar (DWR) quantitative precipitation estimates (QPE) to resolve steep valley orographic rain gradients.

### 4.5 Ground Truth Verification Protocol
- **Failure Time Accuracy**: Landslide occurrence timestamps must be verified to within $\pm 15	ext{ minutes}$ using highway patrol incident logs, CCTV telemetry, or seismic rumble detection.
- **Geotechnical Failure Dimensioning**: Post-failure terrestrial laser scanning (TLS) or drone photogrammetry to record exact failure volume ($	ext{m}^3$), scarp geometry, and runout distance.

---

## 5. Architectural Comparison Matrix

| Component | Current Phase 12A Standard | Future Production Phase Standard |
|---|---|---|
| **Multi-Horizon Landslide Prediction** | Calibrated GBDT (`GradientBoostingClassifier` + Platt scaling) | Deep Temporal Sequence Model (BiLSTM / TCN / Temporal Transformer) |
| **Physics Validation** | Infinite Slope Mohr-Coulomb Limit Equilibrium ($FoS$) | 3D Limit Equilibrium coupled with Transient Unsaturated Seepage ($FoS(t)$) |
| **LSTM Subsystem** | Physics-informed analytical surrogate (`engine/pahad_lstm.py`) | Fully trained deep PyTorch recurrent sequence model |
| **Status Tag** | `TRAINED_LIMITED_DATA` / `SURROGATE` | `PRODUCTION-CANDIDATE` |
| **Telemetry Basis** | Reconstructed historical snapshots + Live 2026 Edge Gateways | Multi-year archived continuous 15-min sensor time-series database |
| **Corroboration Requirement** | 2-of-3 Multimodal Agreement Mandatory | 2-of-3 Multimodal Agreement Mandatory |
