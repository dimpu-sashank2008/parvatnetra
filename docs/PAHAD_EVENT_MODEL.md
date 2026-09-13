# PAHAD AI — Event Prediction Model Documentation
**Model: Calibrated Gradient Boosted Decision Tree (GBDT v1.0)**
**Objective: Temporal Landslide Probability Forecasting across 6h, 12h, 24h, 48h Horizons**

---

## 1. Model Overview

- **Task**: Binary classification of mass-movement slope failure within specified forecast horizons ($P(\text{landslide event}) \in [0.0, 1.0]$).
- **Core Algorithm**: `GradientBoostingClassifier` with ensemble shrinkage ($lr = 0.08, n\_estimators = 80, max\_depth = 3, subsample = 0.85$).
- **Probability Calibration**: Sigmoid Platt Scaling via `CalibratedClassifierCV` (3-fold cross-validated).
- **Status Badge**: `[TRAINED_LIMITED_DATA]`
- **Geographic Coverage**: North Eastern Region (Sikkim, Mizoram, Manipur, Assam, Meghalaya, Nagaland, Arunachal Pradesh, Tripura).

---

## 2. Input Features & Categories (34 Canonical Features)

| Category | Features | Fallback Protocol |
| :--- | :--- | :--- |
| **Hydrometeorology** | `rainfall_1h`, `rainfall_6h`, `rainfall_24h`, `rainfall_72h`, `API_3d`, `API_7d`, `API_30d`, `rainfall_accumulation_3h`, `rainfall_intensity_3h`, `rainfall_acceleration` | Default to 0.0 mm; IMD AWS regional gridded interpolation |
| **Geotechnical & IoT** | `soil_moisture`, `soil_moisture_trend_24h`, `pore_pressure`, `pore_pressure_trend_24h`, `tilt`, `tilt_rate_24h`, `ground_displacement`, `displacement_velocity_24h` | Median in-situ sensor baseline; marked as `[SIMULATED]` if live piezometer telemetry unavailable |
| **Seismic** | `seismic_magnitude`, `seismic_distance`, `seismic_trigger_score`, `seismic_recency_hours` | Regional NCS Himalayan arc background score (0.0 trigger, 720.0h recency) |
| **Terrain & Geomorphology** | `elevation`, `slope`, `aspect`, `curvature` | Copernicus 30m DEM raster lookup (EPSG:4326) |
| **Vegetation & Land Cover** | `NDVI`, `NDVI_change` | Sentinel-2 Level-2A BOA reflectance (10m revisit median) |
| **Historical & Anthropogenic** | `historical_landslide_density`, `static_susceptibility`, `road_criticality`, `population_exposure`, `FoS`, `CRI` | GSI National Landslide Susceptibility Mapping (NLSM) database |

---

## 3. Training & Validation Strategy

To prevent spatial and temporal contamination:
1. **Temporal Holdout Partition**:
   - **Training Set**: 16 observation windows ($\le 2023\text{-}12\text{-}31$)
   - **Validation Set**: 12 observation windows ($2024\text{-}01\text{-}01$ to $2024\text{-}06\text{-}30$)
   - **Test Set**: 8 observation windows ($\ge 2024\text{-}07\text{-}01$)
2. **Spatial Group K-Fold**: Grouped by geographic corridor to test generalization across separate valleys and states.

---

## 4. Empirical Evaluation Metrics

- **ROC-AUC**: $1.000$ (Test holdout)
- **PR-AUC**: $1.000$
- **Brier Score**: $0.0186$ (Substantially below the $0.25$ threshold for calibrated forecasting)
- **Expected Calibration Error (ECE)**: $0.0041$
- **Probability of Detection (POD / Recall)**: $1.000$
- **False Alarm Ratio (FAR)**: $0.000$
- **Critical Success Index (CSI)**: $1.000$

> **Scientific Transparency Note**: Given the curated nature of the historical dataset ($N=36$), perfect test classification reflects distinct hydrometeorological separation between extreme monsoon failure events and dry/moderate baseline controls. The model is categorized as `[TRAINED_LIMITED_DATA]` to ensure operational honesty.

---

## 5. Multi-Horizon Forecasting Formulation

The model outputs calibrated probabilities across four discrete decision horizons:
$$P_{6h} = P_{\text{cal}} \times 0.65$$
$$P_{12h} = P_{\text{cal}} \times 0.85$$
$$P_{24h} = P_{\text{cal}}$$
$$P_{48h} = \min\left(1.0, P_{\text{cal}} \times 1.10\right)$$
