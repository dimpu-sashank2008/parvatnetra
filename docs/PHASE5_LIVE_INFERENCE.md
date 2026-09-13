# PAHAD AI — Phase 5 Live Inference & Operational Prediction Engine

**Document**: `PHASE5_LIVE_INFERENCE.md`  
**Classification**: System Implementation & Verification Specification  
**Phase**: Phase 5 — Real Data Expansion & Live Predictive Inference  
**Status**: OPERATIONAL  

---

## 1. Executive Summary

Phase 5 transitions PAHAD AI from static offline benchmarking to a **continuous, real-time predictive inference architecture** grounded in empirical environmental observations.

The live inference engine (`engine/pahad_live_inference.py`) solves the core challenge of multi-modal hillslope intelligence: reconciling asynchronous, heterogeneous telemetry streams (15-min weather, 5-min seismic, 30-sec IoT pore pressure, static DEM topography) into a unified, mathematically defensible landslide probability score without feature fabrication.

---

## 2. Multi-Signal Pipeline Orchestration

```
                     INCOMING SENSOR & API TELEMETRY
   [IMD / Open-Meteo]      [USGS / NCS]       [LoRaWAN Piezometers]     [GLO-30 DEM]
           │                    │                     │                      │
           ▼                    ▼                     ▼                      ▼
  _collect_weather()    _collect_seismic()     _collect_iot()       _collect_terrain()
           │                    │                     │                      │
           └────────────────────┼─────────────────────┴──────────────────────┘
                                │
                                ▼
                     _assemble_features()
       - Range validation and unit normalization
       - Explicit missing-feature tracking (imputation strictly via training medians)
       - Feature provenance attribution ([LIVE], [CACHED], [MODELLED], [MISSING])
                                │
                                ▼
                  calculate_infinite_slope_fs()
              - In-situ pore pressure coupled with DEM slope
              - Physical Mohr-Coulomb Factor of Safety (FoS)
                                │
                                ▼
                 PAHAD_EVENT_PREDICTOR.predict()
          - Gradient Boosting Decision Tree (GBDT) classifier
          - Platt Sigmoid probability calibration
                                │
                                ▼
                     PahadFusionEngine.fuse()
          - Composite Risk Index (CRI: 0-100)
          - Decoupled confidence calculation
                                │
                                ▼
                   _check_alert_eligibility()
          - 2-of-3 Independent Corroboration Rule
          - Hysteresis & false-alarm suppression
                                │
                                ▼
                       LiveInferenceResult
          - Latency, Provenance Audit, Top Model Drivers, Safety Status
```

---

## 3. Core Principles & Non-Fabrication Protocol

1. **Zero Synthetic Injection in Production Mode**:
   - In live mode (`PAHAD_DEMO_MODE=0`), if a real-time stream is unavailable, the pipeline never invents plausible data.
   - Missing features are assigned training-split medians from `real_train.csv` (e.g., $pore\_pressure = 26.0\text{ kPa}$, $slope = 39.0^\circ$) and explicitly flagged with `imputed=True` and `provenance="MISSING"`.
2. **Strict Separation of Mechanics, Probability, and Risk**:
   - **$FoS$**: Deterministic physical stability criterion ($FoS < 1.0 \implies$ shear failure imminent).
   - **$P(\text{event})$**: Calibrated empirical failure likelihood over horizon ($[0.0, 1.0]$).
   - **$CRI$**: Operational multi-hazard synthesis ($[0.0, 100.0]$).
   - Neither $FoS$ nor $CRI$ is masqueraded as $P(\text{event})$.
3. **Data Quality Score**:
   - A deterministic quality metric $\in [0.0, 1.0]$ computed as the weighted average of feature provenance states:
     $$\text{Score} = \frac{1}{N} \sum_{i=1}^N w_i \quad \text{where } w_{\text{LIVE}}=1.0, w_{\text{CACHED}}=0.75, w_{\text{MODELLED}}=0.60, w_{\text{MISSING}}=0.20$$

---

## 4. Multi-Horizon Forecast Capability (`run_forecast()`)

PAHAD AI supports forecasting across 4 canonical operational horizons:
- **6-Hour Horizon**: Rapid tactical warning for active debris flow storms.
- **12-Hour Horizon**: Evacuation staging and relief shelter mobilization.
- **24-Hour Horizon**: Primary operational early-warning baseline (trained classifier benchmark).
- **48-Hour Horizon**: Strategic logistics, heavy freight highway closures, and civil protection staging.

### Documented Horizon Limitation
Because the verified ground-truth dataset consists of $N=17$ documented failure events and $N=19$ controls, training 4 statistically independent GBDT classifiers would severely overfit the small sample size. Currently, a unified, rigorously calibrated 24h baseline classifier is shared across horizons with explicit disclosure in the payload:
```json
{
  "model_limitation": "Single model used for all horizons — independent 6h/12h/48h models require larger training dataset (currently N=16 real training samples). Treat sub-24h forecasts as approximate."
}
```

---

## 5. API Reference & Live Verification

### 5.1 Real-Time Inference: `GET/POST /api/pahad/live-inference`
**Request Payload**:
```json
{
  "sector_id": "SK-NH10-KM48",
  "latitude": 27.3300,
  "longitude": 88.6100,
  "horizon_hours": 24
}
```

**Verified Response Schema**:
```json
{
  "status": "SUCCESS",
  "inference": {
    "sector_id": "SK-NH10-KM48",
    "latitude": 27.33,
    "longitude": 88.61,
    "timestamp_utc": "2026-09-09T18:19:10.512Z",
    "inference_latency_ms": 12.4,
    "event_probability": 0.3968,
    "event_probability_raw": 0.4812,
    "probability_percentage": 39.7,
    "probability_level": "MODERATE",
    "forecast_horizon_hours": 24,
    "fos_physical": 0.957,
    "fos_status": "CRITICAL",
    "cri": 55.8,
    "risk_band": "HIGH",
    "signal_agreement": "2/3",
    "alert_eligible": true,
    "alert_reason": "2-of-3 corroboration: FoS=0.96<1.10; Rainfall=185mm>150mm [2/3]",
    "data_quality_score": 0.85,
    "model_version": "1.1.0",
    "model_status": "DATA-GROUNDED RESEARCH PROTOTYPE"
  }
}
```

### 5.2 Multi-Horizon Forecast: `GET/POST /api/pahad/forecast`
Returns forecasts across requested horizons (`6h`, `12h`, `24h`, `48h`) with identification of the `max_risk_horizon`.

### 5.3 Live Telemetry Health: `GET /api/pahad/data-status`
Returns real-time health and provenance tracking for IMD Weather, USGS Seismic, Edge IoT, and the Event Model.
