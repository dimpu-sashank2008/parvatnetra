# PARVAT NETRA / PAHAD AI — PHASE 12A RAINFALL THRESHOLD AUDIT
**Empirical Intensity-Duration Thresholds, Regional NER Calibration & Sensitivity Analysis**
*SIH 2026 Problem Statement: SIH 26001*

---

## 1. Executive Summary

This audit evaluates the empirical rainfall threshold formulations implemented in PARVAT NETRA. 

The platform relies on two peer-reviewed regional power-law Intensity-Duration (I-D) thresholds derived specifically for the North-Eastern Himalayan region:
1. **Mandal & Sarkar (2013 / 2021) North Sikkim Curve:**
   $$I_{\text{thresh}} = 4.045 \cdot D^{-0.25} \quad [\text{mm/hr}]$$
2. **Monga & Ganguli (2018) Regional North-East Himalaya Curve:**
   $$I_{\text{thresh}} = 5.8294 \cdot D^{-0.4141} \quad [\text{mm/hr}]$$

**CRITICAL SCIENTIFIC PRINCIPLE:** Neither relation is presented as a "universal global threshold." They are empirical boundaries calibrated on historical landslide events in Sikkim, Darjeeling, and the wider North-East Region (NER).

---

## 2. Threshold Sensitivity Table Across Event Durations

The table below contrasts both threshold equations across standard meteorological observation windows:

| Duration ($D$, hrs) | Mandal & Sarkar Intensity | M&S Cumulative Rainfall | Monga & Ganguli Intensity | M&G Cumulative Rainfall | Sensitivity Interpretation |
|---|---|---|---|---|---|
| **1h** | $4.045\text{ mm/h}$ | $4.05\text{ mm}$ | $5.829\text{ mm/h}$ | $5.83\text{ mm}$ | Flash cloudburst triggering boundary |
| **3h** | $3.074\text{ mm/h}$ | $9.22\text{ mm}$ | $3.699\text{ mm/h}$ | $11.10\text{ mm}$ | Convective squall threshold |
| **6h** | $2.585\text{ mm/h}$ | $15.51\text{ mm}$ | $2.776\text{ mm/h}$ | $16.66\text{ mm}$ | Extended monsoonal surge threshold |
| **12h** | $2.173\text{ mm/h}$ | $26.08\text{ mm}$ | $2.083\text{ mm/h}$ | $25.00\text{ mm}$ | Convergence point of both models |
| **24h** | $1.828\text{ mm/h}$ | **$43.88\text{ mm}$** | $1.563\text{ mm/h}$ | **$37.52\text{ mm}$** | Standard operational 24h hazard marker |
| **48h** | $1.537\text{ mm/h}$ | $73.80\text{ mm}$ | $1.173\text{ mm/h}$ | $56.32\text{ mm}$ | Multi-day antecedent saturation limit |
| **72h** | $1.389\text{ mm/h}$ | **$100.00\text{ mm}$** | $0.992\text{ mm/h}$ | $71.43\text{ mm}$ | 3-day deep regolith saturation marker |

---

## 3. Geographic Calibration & Valid Domains

| Parameter | Mandal & Sarkar (2013/2021) | Monga & Ganguli (2018) |
|---|---|---|
| **Calibrated Terrain** | High-energy glaciated & fluvial valleys of North Sikkim (Lachen, Lachung, Teesta Gorge). | Meso-scale basins across all 8 NER states (Meghalaya, Assam, Sikkim, Arunachal, Manipur, Mizoram, Nagaland, Tripura). |
| **Geological Setting** | Daling Group metamorphics (phyllites, schists, sheared fault zones). | Mixed Himalayan thrust belt, Barail flysch sandstones, and Shillong plateau gneiss. |
| **Monsoon Regimes** | Orographic south-west monsoon ($1500\text{--}3500\text{ mm/yr}$). | Extreme tropical monsoon ($2000\text{--}11500\text{ mm/yr}$, Cherrapunji/Mawsynram belts). |
| **Valid Duration Window** | $1\text{ h} \le D \le 72\text{ h}$ | $1\text{ h} \le D \le 120\text{ h}$ |
| **Extrapolation Caution** | Do NOT extrapolate to Peninsular India (Western Ghats) or Nilgiris without local recalibration. | Extrapolation to arid Himalayan rain-shadows (Ladakh) is invalid. |

---

## 4. Critical Scientific Finding: Monga & Ganguli ED Formula Anomaly

During the code audit of `engine/pahad_models.py:273`, an important empirical equation discrepancy was identified:

### The Implementation in Code:
```python
def calculate_ed_threshold(duration_hours: float) -> float:
    d_hours = max(0.1, float(duration_hours))
    d_days = d_hours / 24.0
    return round(1.3728 * (d_days ** 1.1083), 4)
```

### The Anomaly:
At $D = 24.0\text{ hours}$ ($D_{\text{days}} = 1.0$), this equation produces:
$$E_{\text{thresh}} = 1.3728 \cdot (1.0)^{1.1083} = 1.3728\text{ mm}$$
If evaluated via an `or` condition against active cumulative rainfall:
$$\text{ed\_exceeded} = (\text{event\_rainfall} \ge E_{\text{thresh}})$$
Any trivial drizzle of just $1.4\text{ mm}$ in 24 hours would trigger `ed_exceeded = True`!

### Operational Resolution in PARVAT NETRA:
1. **Primary Production Trigger:** In `engine/pahad_fusion.py:185`, the platform intentionally gates the hydrological trigger on:
   - Explicit `rainfall_threshold_status == "EXCEEDED"` from `services/weather_service.py` (which uses the authoritative Mandal-Sarkar I-D curve $I_{\text{thresh}} = 4.045 D^{-0.25}$); OR
   - Severe 24h accumulation: $R_{24h} \ge 100.0\text{ mm}$.
2. **False Alarm Safeguard:** This prevents the $1.37\text{ mm}$ ED curve artifact from causing premature alarm escalations.
3. **P1 Backlog Item:** The regression coefficient $\alpha=1.3728$ in `calculate_ed_threshold` was identified as having been derived from normalized daily anomaly ratios rather than raw millimeters; a scheduled refactor in Phase 12B will recalibrate the raw millimeter intercept.
