# PARVAT NETRA • PAHAD AI — Phase 12B Temporal Data Architecture

**Standard**: SIH 26001 / National Disaster-Intelligence Platform  
**System**: PARVAT NETRA — Northeast Region Sentinel  
**Subsystem**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Document Version**: 12.0.0-phase12b  
**Status**: ARCHITECTURE SPECIFICATION & DATA INTEGRITY STANDARD  

---

## 1. Executive Summary

Phase 12B establishes the canonical temporal data architecture, telemetry schemas, and sequence validation standards required for future temporal deep-learning models (LSTM, GRU, Temporal Convolutional Networks) within PARVAT NETRA / PAHAD AI.

Following the empirical findings of the Phase 12A pre-check:
- Total historical temporal snapshot rows: **105**
- Unique corridors: **17**
- Continuous real sensor telemetry sequences: **0**
- Real-time sensor rows: **0** (pre-2026 sensor readings are physically derived limit-equilibrium/hydrological reconstructions)

This architecture codifies the data contracts, normalization pipelines, and quality scoring systems necessary to ingest continuous, high-cadence in-situ IoT telemetry while strictly preventing synthetic fabrication, target leakage, and ungrounded model training.

---

## 2. Canonical 26-Feature Time-Series Schema

Every temporal observation packet conforms to a strictly typed 26-dimensional physical and environmental feature space. This schema eliminates redundant indices and provides standardized physical units for recurrent sequence ingestion.

### 2.1 Hydrology & Precipitation Modality (11 Features)
| Feature Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `rain_1h` | Float64 | mm | 1-hour cumulative precipitation |
| `rain_3h` | Float64 | mm | 3-hour cumulative precipitation |
| `rain_6h` | Float64 | mm | 6-hour cumulative precipitation |
| `rain_12h` | Float64 | mm | 12-hour cumulative precipitation |
| `rain_24h` | Float64 | mm | 24-hour cumulative precipitation |
| `rain_48h` | Float64 | mm | 48-hour cumulative precipitation |
| `rain_72h` | Float64 | mm | 72-hour cumulative precipitation |
| `antecedent_rain_3d` | Float64 | mm | 3-day antecedent precipitation index |
| `antecedent_rain_7d` | Float64 | mm | 7-day antecedent precipitation index |
| `rain_intensity` | Float64 | mm/h | Instantaneous rainfall rate |
| `rainfall_threshold_exceedance` | Float64 | Ratio | Ratio of current cumulative rain to Caine (1980) empirical threshold |

### 2.2 Topography & Geotechnical Physics Modality (5 Features)
| Feature Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `fos` | Float64 | Dimensionless | Infinite-slope Factor of Safety (Mohr-Coulomb limit equilibrium) |
| `slope` | Float64 | Degrees | Slope gradient derived from CartoDEM / Copernicus 30m DEM |
| `aspect` | Float64 | Degrees | Slope azimuth / facing angle (0–360°) |
| `elevation` | Float64 | Meters | Topographic elevation above mean sea level |
| `curvature` | Float64 | 1/m | Planform and profile surface curvature |

### 2.3 In-Situ Sensor Telemetry Modality (4 Features)
| Feature Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `soil_moisture` | Float64 | % VWC | Volumetric water content from soil moisture sensors |
| `pore_pressure` | Float64 | kPa | Pore-water pressure from vibrating-wire piezometers |
| `tilt` | Float64 | Degrees | Surface tilt angle deviation from dual-axis MEMS inclinometer |
| `ground_displacement` | Float64 | mm | Cumulative subsurface shear displacement from borehole extensometer |

### 2.4 Earth Observation & Seismic Modality (6 Features)
| Feature Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `ndvi` | Float64 | Dimensionless | Normalized Difference Vegetation Index (Sentinel-2 MSI) |
| `ndvi_anomaly` | Float64 | Dimensionless | Departure from historical seasonal baseline NDVI |
| `seismic_count_24h` | Int64 | Count | Number of seismic events recorded within 100km in the last 24h |
| `max_magnitude_24h` | Float64 | Richter (M) | Maximum earthquake magnitude recorded within 100km in the last 24h |
| `nearest_seismic_distance` | Float64 | km | Epicentral distance to the closest seismic event |
| `historical_susceptibility`| Float64 | [0.0, 1.0] | Geological Survey of India (GSI) 1:50k macro-susceptibility score |

---

## 3. Metadata & Spatiotemporal Identification Schema

All observation records include a standardized 9-field identification envelope:

```json
{
  "sample_id": "SN-MANG-01-20231003-T00",
  "event_id": "EVT-202310-MANGAN",
  "sector_id": "SK-MANGAN-01",
  "state": "Sikkim",
  "district": "Mangan",
  "timestamp": "2023-10-03T19:30:00+00:00",
  "latitude": 27.5024,
  "longitude": 88.5292,
  "provenance": "[HISTORICAL]"
}
```

---

## 4. Target Exclusion & Leakage Prevention Invariant

To guarantee absolute scientific integrity, target variables are strictly quarantined from the input feature matrix:
1. `composite_risk_index_cri`: The operational composite risk score is a downstream fusion synthesis, NEVER an input feature.
2. `event_label`: The binary failure indicator ($y \in \{0, 1\}$) is stored exclusively in label vectors.
3. `target_6h`, `target_12h`, `target_24h`, `target_48h`: Multi-horizon forecast targets are isolated in target matrices.

The `TemporalLeakageDetector` in `engine/pahad_temporal_engine.py` asserts that no column containing `cri`, `risk`, or `target` appears in the feature columns during model training.

---

## 5. Five-Tier Data Provenance Ontology

Never treat simulated or reconstructed numbers as authenticated physical sensor telemetry. Every record must be tagged with its exact evidentiary provenance:

1. `REAL`: Authenticated in-situ live hardware telemetry stream (LoRaWAN/4G telemetry from deployed edge field nodes).
2. `HISTORICAL`: Archival ground truth events documented by official authorities (GSI, IMD, SDMA, BRO).
3. `MODELLED`: Physical parameters reconstructed via limit-equilibrium equations, hydrological recession models, or DEM back-analysis.
4. `SIMULATED`: Statistically realistic physics simulations generated for emergency drills and evacuation rehearsals.
5. `BENCH_VALIDATED`: Edge hardware bench-test packets transmitted during hardware-in-the-loop laboratory calibration.

---

## 6. Timestamp Normalization & Continuity Pipeline

### 6.1 Strict UTC ISO-8601 Parsing
All timestamps are parsed using `normalize_timestamp_utc()`. Unqualified local strings (e.g. `2023-10-03 19:30`) are converted to strict UTC (`2023-10-03T19:30:00+00:00`) based on Indian Standard Time (IST, UTC+5:30) offset conversion.

### 6.2 Gap Classification Taxonomy
Given nominal telemetry cadence $\Delta t_{	ext{nominal}}$:
- `NO_GAP`: $\Delta t \le 1.10 	imes \Delta t_{	ext{nominal}}$
- `MINOR_GAP`: $\Delta t_{	ext{nominal}} < \Delta t \le 2.0	ext{ hours}$ (Imputable via linear/spline interpolation)
- `MODERATE_GAP`: $2.0	ext{ hours} < \Delta t \le 6.0	ext{ hours}$ (Imputable via geotechnical physics decay)
- `CRITICAL_GAP`: $6.0	ext{ hours} < \Delta t \le 24.0	ext{ hours}$ (Gradients destroyed; sequence boundary warning)
- `DISCONNECTED`: $\Delta t > 24.0	ext{ hours}$ (Sequence must be severed into independent sub-sequences)

---

## 7. Composite Sequence Quality Scoring Methodology

Every candidate sequence receives an automated quality score $Q \in [0.0, 1.0]$:

$$Q = 0.35 	imes C_{	ext{comp}} + 0.25 	imes C_{	ext{cont}} + 0.20 	imes P_{	ext{pur}} + 0.20 	imes R_{	ext{cad}}$$

Where:
- $C_{	ext{comp}} = 1.0 - 	ext{Missing Feature Rate}$
- $C_{	ext{cont}} = \max\left(0, 1.0 - rac{N_{	ext{critical}} + 2 	imes N_{	ext{disconnected}}}{N_{\Delta t}}ight)$
- $P_{	ext{pur}} = rac{1.0 	imes N_{	ext{real}} + 0.90 	imes N_{	ext{hist}} + 0.50 	imes N_{	ext{modelled}} + 0.10 	imes N_{	ext{sim}}}{N_{	ext{total}}}$
- $R_{	ext{cad}} = \max\left(0, 1.0 - 0.5 	imes rac{\sigma_{\Delta t}}{\mu_{\Delta t}}ight)$ (Cadence regularity penalizing timing jitter)

A sequence is deemed eligible for deep learning ingestion only if $Q \ge 0.85$.
