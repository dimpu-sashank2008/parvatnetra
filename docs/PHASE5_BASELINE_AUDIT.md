# PAHAD AI — Phase 5 Baseline Audit
## Real Data State Before Phase 5 Begins

**Document**: `PHASE5_BASELINE_AUDIT.md`  
**Audit Date**: 2026-09-09  
**Phase**: Phase 5 — Real Data Expansion & Live Predictive Inference  
**Status**: BASELINE ESTABLISHED  

---

## 1. Verified Historical Event Catalog

**File**: `data/raw/historical_landslides_ner.csv`  
**Events**: 17 documented catastrophic failures  
**Provenance**: ALL `[HISTORICAL]`

| # | Event ID | Date | State | District | Source | Source Confidence |
|---|----------|------|-------|----------|--------|------------------|
| 1 | EV-01 | 2024-10-04 | Sikkim | Pakyong | GSI Pakyong Field Inspection | HIGH |
| 2 | EV-02 | 2024-06-12 | Sikkim | Mangan | ISRO DMSG / Sikkim SDMA | HIGH |
| 3 | EV-03 | 2023-10-04 | Sikkim | Gangtok | South Lhonak GLOF / GSI Assessment | HIGH |
| 4 | EV-04 | 2022-06-29 | Manipur | Noney | GSI Disaster Report GSI-NER-MN-2022-004 | VERY_HIGH |
| 5 | EV-05 | 2024-07-02 | Manipur | Tamenglong | Manipur SDMA Monsoon Bulletin | MEDIUM |
| 6 | EV-06 | 2024-05-28 | Mizoram | Aizawl | Cyclone Remal GSI Report GSI-NER-MZ-2024-019 | VERY_HIGH |
| 7 | EV-07 | 2023-08-22 | Mizoram | Lunglei | Mizoram PWD / DDMA | MEDIUM |
| 8 | EV-08 | 2022-05-16 | Assam | Dima Hasao | New Haflong Railway Station Breaches GSI Report | VERY_HIGH |
| 9 | EV-09 | 2024-06-18 | Assam | Cachar | Assam SDMA (ASDMA) | HIGH |
| 10 | EV-10 | 2022-06-17 | Meghalaya | East Khasi Hills | GSI Shillong Plateau Escarpment Survey | VERY_HIGH |
| 11 | EV-11 | 2024-07-10 | Meghalaya | East Khasi Hills | Meghalaya SDMA Flood & Landslide Log | HIGH |
| 12 | EV-12 | 2024-09-03 | Nagaland | Kohima | Nagaland NSDMA Monsoon Assessment | HIGH |
| 13 | EV-13 | 2023-07-28 | Nagaland | Phek | GSI NLSM Archive | MEDIUM |
| 14 | EV-14 | 2024-06-25 | Arunachal Pradesh | Tawang | BRO Project Vartak / Arunachal SDMA | HIGH |
| 15 | EV-15 | 2023-06-20 | Arunachal Pradesh | Papum Pare | GSI Itanagar Road Survey | HIGH |
| 16 | EV-16 | 2024-08-20 | Tripura | North Tripura | Tripura SDMA Monsoon Deluge Log | HIGH |
| 17 | EV-17 | 2023-07-14 | Tripura | North Tripura | GSI NLSM Archive | MEDIUM |

**Geographic Coverage**: All 8 NER states represented  
**Date Range**: May 2022 – October 2024  
**States**: Sikkim, Manipur, Mizoram, Assam, Meghalaya, Nagaland, Arunachal Pradesh, Tripura  

---

## 2. Training Dataset Summary

**Chronological Temporal Holdout Partitions**:

| Partition | File | Rows | Positive (Events) | Negative (Controls) | Date Range |
|-----------|------|------|-------------------|---------------------|------------|
| Train | `data/features/real_train.csv` | 16 | 8 | 8 | Up to Oct 2023 |
| Validation | `data/features/real_val.csv` | 12 | 4 | 8 | Feb–Jun 2024 |
| Test (held-out) | `data/features/real_test.csv` | 8 | 5 | 3 | Jul–Oct 2024 |
| **Total** | — | **36** | **17** | **19** | **May 2022–Oct 2024** |

**Dataset SHA-256**: `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`

---

## 3. Label Quality Assessment

### Positive Event Labeling
- All 17 events sourced from authorized institutions (GSI, ISRO, SDMA, BRO, IMD, CWC)
- All events within NER bounding box (lat 21.5–29.5, lon 88.0–97.5)
- All events have timestamps with <24h uncertainty
- Source confidence mapping:
  - VERY_HIGH: 3 events (EV-04, EV-06, EV-08, EV-10) — **4 events**
  - HIGH: 8 events
  - MEDIUM: 3 events (EV-05, EV-07, EV-13, EV-17) — **4 events** (note MEDIUM below threshold 0.70)

> [!WARNING]
> **Critical Finding**: Events EV-05, EV-07, EV-13, EV-17 have `source_confidence = MEDIUM`. The `event_labeling.py` engine requires numeric confidence ≥ 0.70. MEDIUM is stored as a string and not directly mapped to a numeric value. The `EventLabeler.validate_positive_event()` attempts `float(event.get("source_confidence", ...))` which will raise `ValueError` on string inputs. These 4 records must be reviewed and assigned explicit numeric confidence scores.

### FoS Used in Control Definition (Potential Selection Bias)
The `event_labeling.py` `validate_negative_control()` method requires `FoS >= 1.10` for a negative control to be accepted. This means controls were **selected** based on the FoS signal being high.

> [!CAUTION]
> **Selection Bias Risk**: Using FoS ≥ 1.10 as a criterion to select negative controls creates an artificial correlation: the model will see (FoS high → label=0) in training, but this is a definitional truth, not an empirical discovery. This inflates the apparent discriminative power of FoS in the event classifier. Recommendation: FoS should be a feature, not a selection filter for controls. Controls should be selected purely based on temporal/spatial non-overlap with documented events. Mark this as a limitation in model card.

---

## 4. Feature Inventory

From `data/raw/historical_landslides_ner.csv` column headers:

| Feature | Type | Source | Availability |
|---------|------|--------|-------------|
| `rainfall_trigger_mm` | Continuous | IMD AWS / reconstructed | Historical: estimated from synoptic records |
| `soil_moisture` | Continuous [0-1] | SAT proxy / reconstructed | Historical: satellite-derived estimate |
| `pore_pressure_kpa` | Continuous | Piezometer / FoS-reconstructed | Historical: FoS limit-equilibrium back-calc |
| `tilt_deg` | Continuous | Inclinometer / estimated | Historical: pre-failure slope estimation |
| `ground_displacement_mm` | Continuous | InSAR/field measurement | Historical: post-failure field survey |
| `fos` | Continuous | Infinite slope formula | Historical: computed from known soil params |
| `cri` | Continuous [0-100] | PAHAD fusion output | Derived — NOT real-time observation |
| `slope_deg` | Continuous | DEM (GLO-30) | LIVE — available from DEM for any location |
| `elevation_m` | Continuous | DEM (GLO-30) | LIVE — available from DEM for any location |
| `geographic_group` | Categorical | Manual assignment | Available |

> [!NOTE]
> **CRI as Feature**: The `cri` field in training data represents the PAHAD fusion output computed on historical feature windows. This should NOT be used as an input feature to the event model (it's an output of another model). It is not included in the actual training feature matrix.

> [!IMPORTANT]
> **Historical Reconstruction Caveat**: Several features (`pore_pressure_kpa`, `tilt_deg`, `ground_displacement_mm`) for pre-2024 events were reconstructed using limit-equilibrium physics and InSAR estimates, not from real-time sensor telemetry at the time of the event. This is documented in `docs/PHASE4_LIMITATIONS.md`.

---

## 5. Phase 4 Model Performance (Actual Results)

**Model Selected**: Gradient Boosting Classifier (Platt-calibrated)  
**Test Set**: N=8 (5 events, 3 controls)

| Metric | Value | Caveat |
|--------|-------|--------|
| ROC-AUC | 1.0000 | ±wide CI on N=8 |
| PR-AUC | 1.0000 | ±wide CI on N=8 |
| POD | 1.0000 | 5/5 events detected |
| FAR | 0.0000 | 0 false alarms |
| CSI | 1.0000 | Perfect on N=8 |
| Brier Score | 0.0824 | Calibrated |
| ECE | 0.2604 | Moderate calibration error |
| Lead Time | 24.0h | Based on feature window horizon |

**Status**: `DATA-GROUNDED RESEARCH PROTOTYPE` — NOT production-certified

---

## 6. What Phase 5 Must Accomplish

### Priority 1 — Data Quality
- [ ] Fix string source_confidence values (MEDIUM, HIGH, VERY_HIGH → numeric)
- [ ] Document FoS-based control selection bias in model card
- [ ] Build temporal dataset with proper hourly/daily windows
- [ ] Add more raw event sources (GSI NLSM, NRSC LSLBI, state SDMAs)

### Priority 2 — Live Inference Pipeline
- [ ] Build `engine/pahad_live_inference.py` — production inference pipeline
- [ ] Connect to weather, seismic, DEM, IoT services
- [ ] Add `GET /api/pahad/live-inference` endpoint
- [ ] Add `GET /api/pahad/forecast` (6h/12h/24h/48h) endpoint
- [ ] Add `GET /api/pahad/data-status` endpoint

### Priority 3 — Model Improvements
- [ ] Temporal validation with correct multi-horizon labels
- [ ] Calibration audit (Platt vs isotonic vs uncalibrated)
- [ ] Feature importance (SHAP if available, else native)
- [ ] Retrain on clean dataset after provenance fixes

### Priority 4 — Documentation
- [ ] `docs/PHASE5_LIVE_INFERENCE.md`
- [ ] `docs/PHASE5_DATA_STATUS.md`
- [ ] `docs/PHASE5_MODEL_ARCHITECTURE.md`
- [ ] Updated `docs/PAHAD_MODEL_CARD.md`

---

## 7. External Data Sources Available for Phase 5

| Source | Data Type | Access Method | Status |
|--------|-----------|---------------|--------|
| Open-Meteo | Precipitation, temperature | Free REST API | **AVAILABLE** |
| USGS Earthquake | Seismic events | Free REST API | **AVAILABLE** |
| GLO-30 DEM | Terrain (slope, elevation) | Static files / API | **AVAILABLE** |
| IMD (India Met Dept) | Rainfall, AWS | API key required | REQUIRES_KEY |
| NCS (seismic) | Seismic events | Web scraping / API | REQUIRES_KEY |
| GSI NLSM | Landslide catalog | Static dataset | DOWNLOAD_NEEDED |
| ISRO NRSC LSLBI | Landslide inventory | Static dataset | DOWNLOAD_NEEDED |
| Copernicus Sentinel-1 | InSAR deformation | ESA Copernicus API | REQUIRES_KEY |
| BHUVAN (ISRO) | Satellite imagery | API key required | REQUIRES_KEY |

---

## 8. Honest Limitations Statement

1. **17 events** covering 2022–2024 is scientifically insufficient for a robust NER-wide operational classifier. Statistically defensible models typically require hundreds of events across multiple seasons.

2. **Feature reconstruction** for historical events means pre-2024 pore pressure and tilt values are physics-based estimates, not measurements.

3. **FoS selection bias** in negative controls inflates apparent model performance. This must be documented in model card v2.

4. **No real-time IoT data** has been collected at scale. Current IoT integration is at pilot stage (1-2 corridors).

5. **Model status**: `DATA-GROUNDED RESEARCH PROTOTYPE` — validated on N=8 test samples with wide confidence intervals.

---

## 9. Phase 5 Dataset Target

| Target | Current | Phase 5 Goal |
|--------|---------|--------------|
| Documented events | 17 | 25–50 (add GSI/NRSC archives) |
| Controls | 19 | 40–100 (defensible temporal windows) |
| Training samples | 16 | 40–80 |
| Validation samples | 12 | 15–30 |
| Test samples | 8 | 10–20 |
| Features per window | 10 | 15–20 (add NDVI, seismic, InSAR proxy) |
| Forecast horizons | 1 (24h) | 4 (6h, 12h, 24h, 48h) if data permits |
