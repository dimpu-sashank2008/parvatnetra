# PAHAD AI — BiLSTM v4 Upgrade: Baseline & Immutable Backup Audit (CP01)
**Standard**: Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform  
**System**: PARVAT NETRA / PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Date**: September 20, 2026  
**Document**: `docs/PAHAD_LSTM_V4_BASELINE.md`  
**Milestone**: CP01 — Immutable Baseline State & Cryptographic Verification  

---

## 1. Executive Summary

In accordance with Checkpoint 01 (CP01), an immutable offline backup of the existing `PAHADBiLSTMv3` model artifacts, weights, feature configuration, scalers, and training pipeline has been established prior to initiating the v4 research-grade validation upgrade.

All artifacts were verified, copied to `backup/lstm_v3_baseline/`, and fingerprinted with SHA-256 cryptographic checksums.

---

## 2. Immutable Artifact Registry & SHA-256 Checksums

| Artifact Description | Source Path | Backup Location | Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- | :---: | :--- |
| **Model Weights** | `models/pahad_lstm_v3_weights.pt` | `backup/lstm_v3_baseline/pahad_lstm_v3_weights.pt` | 5,189,381 | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` |
| **Model Configuration** | `models/pahad_lstm_v3_config.json` | `backup/lstm_v3_baseline/pahad_lstm_v3_config.json` | 2,953 | `7e9d76e26fc66a383ec60d2449da25ff4cce451d9346d665d6210912aacf9f88` |
| **Performance Metrics** | `models/pahad_lstm_v3_metrics.json` | `backup/lstm_v3_baseline/pahad_lstm_v3_metrics.json` | 4,084 | `e212d6d5c64fe42a69cda887f67580d5380ce47c226ab9c73673824908d472be` |
| **Training Pipeline** | `scripts/train_lstm_v3.py` | `backup/lstm_v3_baseline/train_lstm_v3.py` | 27,813 | `2f9463f3b324e2484f40ce1d5e964e36e278bfb1ab9ef48756d92f1e83cdad26` |
| **Inference Engine** | `engine/pahad_lstm.py` | `backup/lstm_v3_baseline/pahad_lstm.py` | 27,699 | `7828f2bc7fcf1e7dcc07de6e471de0889fcea878c4851c0dad596e779d2e6f33` |

---

## 3. Baseline Architectural Specifications (`PAHADBiLSTMv3`)

* **Model Class**: `PAHADBiLSTMv3`
* **Input Sequence Dimensions**: $(B, 72, 33)$ where sequence length $T = 72\text{ hours}$ antecedent window and $D = 33\text{ multimodal features}$.
* **Input Projection**: `Linear(33 -> 160)` + `LayerNorm(160)` + `GELU` + `Dropout(0.2)`
* **Recurrent Backbone**: 2-layer Bidirectional LSTM (`hidden_size=160`, bidirectional output $D_{\text{out}}=320$, `dropout=0.3`)
* **Layer Normalization**: `LayerNorm(320)` on concatenated bidirectional outputs
* **Attention Mechanism**: `TemporalAttention` single-head linear pooling across the 72 antecedent hours
* **Prediction Heads**: 4 independent horizon linear projections (`6h`, `12h`, `24h`, `48h`) with residual skip dimensions:
  $$\text{Head}_h: \text{Linear}(320 \to 160) \to \text{GELU} \to \text{Dropout}(0.2) \to \text{Linear}(160 \to 1)$$
* **Total Trainable Weights**: **1,293,125 parameters**
* **Optimizer**: `AdamW` ($\text{lr} = 4\times 10^{-4}$, weight decay $1\times 10^{-4}$)
* **Calibration**: Post-hoc Platt temperature scaling with calibrated temperature $T = 1.0552$.

---

## 4. Baseline Feature Manifest (33 Multimodal Dimensions)

```text
========================================================================================
INDEX | FEATURE NAME                   | CATEGORY                   | UNIT / TYPE
========================================================================================
 0    | rain_1h                        | Climate & Precipitation    | mm/hr (Trajectory)
 1    | rain_3h                        | Climate & Precipitation    | mm (Cumulative)
 2    | rain_6h                        | Climate & Precipitation    | mm (Cumulative)
 3    | rain_12h                       | Climate & Precipitation    | mm (Cumulative)
 4    | rain_24h                       | Climate & Precipitation    | mm (Cumulative)
 5    | rain_48h                       | Climate & Precipitation    | mm (Cumulative)
 6    | rain_72h                       | Climate & Precipitation    | mm (Cumulative)
 7    | antecedent_rain_3d             | Climate & Precipitation    | mm (API)
 8    | antecedent_rain_7d             | Climate & Precipitation    | mm (API)
 9    | api_30d                        | Climate & Precipitation    | mm (API)
 10   | rain_intensity                 | Climate & Precipitation    | mm/hr (Instantaneous)
 11   | fos                            | Geotechnical Physics       | Mohr-Coulomb Factor of Safety
 12   | soil_moisture                  | Soil Porosity & Geotech    | VWC (Ratio 0.0 - 1.0)
 13   | soil_porosity                  | Soil Porosity & Geotech    | Porosity n (Ratio 0.0 - 1.0)
 14   | pore_pressure                  | Soil Porosity & Geotech    | Piezometer pressure u (kPa)
 15   | effective_stress               | Soil Porosity & Geotech    | Normal effective stress σ' (kPa)
 16   | hydraulic_saturation           | Soil Porosity & Geotech    | Saturation ratio θ / n
 17   | tilt                           | IoT Sensor Telemetry       | Biaxial tilt angle θ (deg)
 18   | tilt_rate_24h                  | IoT Sensor Telemetry       | Angular velocity (deg/day)
 19   | ground_displacement            | IoT Sensor Telemetry       | Extensometer shear Δx (mm)
 20   | displacement_velocity_24h      | IoT Sensor Telemetry       | Creeping velocity (mm/day)
 21   | slope                          | Geographical / Terrain     | Slope gradient β (deg)
 22   | aspect                         | Geographical / Terrain     | Hillslope compass azimuth (deg)
 23   | elevation                      | Geographical / Terrain     | Altitude from SRTM 30m (m)
 24   | curvature                      | Geographical / Terrain     | Plan/profile curvature (m^-1)
 25   | ndvi                           | Satellite Earth Obs        | Sentinel-2 NDVI ratio
 26   | ndvi_anomaly                   | Satellite Earth Obs        | Vegetation loss / scar ΔNDVI
 27   | insar_velocity                 | Satellite Earth Obs        | Sentinel-1 InSAR LOS (mm/yr)
 28   | seismic_count_24h              | Seismic Shaking            | Regional earthquake count (M>=2.0)
 29   | max_magnitude_24h              | Seismic Shaking            | Peak moment magnitude Mw
 30   | nearest_seismic_distance       | Seismic Shaking            | Epicentral distance (km)
 31   | historical_susceptibility      | Macro Vulnerability        | GSI NLSM susceptibility index
 32   | composite_risk_index_cri       | Macro Vulnerability        | CRI multi-hazard score (0-100)
========================================================================================
```

---

## 5. Baseline Holdout Evaluation Metrics

Evaluated on the held-out temporal test set ($N=24$ sequences from late 2024):

```text
========================================================================================
HORIZON | TEST ROC-AUC | TEST BRIER | POD (HITS) | FAR (FALSE ALARMS) | THREAT SCORE (CSI)
========================================================================================
6h      | 1.000        | 0.0038     | 1.000      | 0.000              | 1.000
12h     | 1.000        | 0.0042     | 1.000      | 0.000              | 1.000
24h     | 1.000        | 0.0015     | 1.000      | 0.000              | 1.000
48h     | 1.000        | 0.0039     | 1.000      | 0.000              | 1.000
========================================================================================
```

* **Early Warning Lead Time**: Median 24.0 Hours.
* **Governance Status**: `TRAINED_LIMITED_DATA` (`DATA-GROUNDED RESEARCH PROTOTYPE`).

This baseline state is completely preserved in `backup/lstm_v3_baseline/` and serves as the benchmark against which `PAHADBiLSTMv4` will be evaluated.
