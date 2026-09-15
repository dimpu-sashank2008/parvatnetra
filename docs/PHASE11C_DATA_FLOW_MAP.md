# PARVAT NETRA / PAHAD AI — PHASE 11C DATA FLOW MAP
**Comprehensive Data Flow, Ingestion, Normalization & Provenance Inventory**

---

## 1. End-to-End Architectural Data Pipeline

```text
+---------------------------------------------------------------------------------------------------------+
|                                          EXTERNAL DATA SOURCES                                          |
|  [Open-Meteo / IMD AWS]  [USGS / NCS Seismology]  [Copernicus / CartoDEM]  [Sentinel-1 InSAR / Sentinel-2]  |
+----------------------------+-----------------------------+------------------------------+---------------+
                             |                             |                              |
                             v                             v                              v
+---------------------------------------------------------------------------------------------------------+
|                                        INGESTION & CONNECTOR LAYER                                      |
|  services/weather_service.py  services/seismic_service.py  services/dem_service.py  services/eo_catalog.py   |
|  backend/iot_routes.py        backend/field_routes.py      services/edge_gateway.py                      |
+---------------------------------------------------------------------------------------------------------+
                                                           |
                                                           v
+---------------------------------------------------------------------------------------------------------+
|                                     NORMALIZATION & OBSERVATION STORE                                   |
|  - In-memory & SQLite cache (data/cache/weather/, data/cache/seismic/, data/observations/pahad_obs.db)   |
|  - Unit normalization: mm/24h, mm/h, kPa, degrees, mm displacement                                      |
|  - Provenance tagging: [LIVE], [CACHED], [HISTORICAL], [MODELLED], [SIMULATED], [BENCH_VALIDATED], etc.   |
+---------------------------------------------------------------------------------------------------------+
                                                           |
                                                           v
+---------------------------------------------------------------------------------------------------------+
|                                          FEATURE ASSEMBLY ENGINE                                        |
|  engine/pahad_live_inference.py: _assemble_features()                                                   |
|  engine/pahad_inputs.py: build_pahad_feature_vector()                                                   |
|  - Explicit missing feature tracking & training-median imputation (n=16 real historical baseline)       |
+---------------------------------------------------------------------------------------------------------+
                                                           |
                                 +-------------------------+-------------------------+
                                 |                                                   |
                                 v                                                   v
+---------------------------------------------------+   +---------------------------------------------------+
|                     MODEL A                       |   |                      MODEL B                      |
|         PAHAD Geotechnical FoS Engine             |   |            PAHAD Landslide Event Model            |
|  engine/pahad_models.py:                          |   |  engine/pahad_event_predictor.py                  |
|    calculate_infinite_slope_fs()                  |   |  models/pahad_event_model.pkl (GBDT + Platt)       |
|  - Mohr-Coulomb shear strength                    |   |  - Target: P(landslide event within forecast)     |
|  - Effective stress & pore-water ratio (m)        |   |  - Horizons: 6h / 12h / 24h / 48h                 |
|  - Continuous Factor of Safety (FoS: 0.4 - 3.0+)  |   |  - Calibrated probability output [0.0, 1.0]       |
+---------------------------------------------------+   +---------------------------------------------------+
                                 |                                                   |
                                 +-------------------------+-------------------------+
                                                           |
                                                           v
+---------------------------------------------------------------------------------------------------------+
|                                           PAHAD FUSION ENGINE                                           |
|  engine/pahad_fusion.py: PahadFusionEngine                                                              |
|  - Static Susceptibility (S: 0-1) [0.40 weight]                                                         |
|  - Dynamic Rainfall (P: 0-1) [0.35 weight]                                                              |
|  - Ground Anomaly (A: 0-1) [0.25 weight]                                                                |
|  - Base Hazard: H = 0.40*S + 0.35*P + 0.25*A                                                           |
|  - Vulnerability Score (V: 0.1 - 1.0)                                                                   |
|  - Composite Risk Index: CRI = H * V * 100                                                              |
|  - Constitutional 2-of-3 Signal False Alarm Suppression Gate (FoS<=1.0, Rain Exceeded, ML P>0.80)      |
+---------------------------------------------------------------------------------------------------------+
                                                           |
                                                           v
+---------------------------------------------------------------------------------------------------------+
|                                         REST API EXPOSURE LAYER                                         |
|  /api/pahad/live-inference           /api/pahad/highest-risk-corridor                                   |
|  /api/pahad/forecast                 /api/pahad/data-status                                             |
|  /api/pahad/event-model/status       /api/pahad/event-model/data-quality                                |
+---------------------------------------------------------------------------------------------------------+
                                                           |
                                                           v
+---------------------------------------------------------------------------------------------------------+
|                                         OPERATIONAL FRONTEND                                            |
|  templates/index.html (Desktop GIS, Mobile Dashboard, Multi-corridor Matrix, EOC Triage, Warning Center)|
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Complete Input Inventory Table

| Input Parameter | Primary Source | Wire/Data Format | Normalization / Transformation | Consuming Engine Component | Permitted Provenance Badge |
|---|---|---|---|---|---|
| **Rainfall (24h accumulation)** | Open-Meteo REST API / IMD AWS | JSON (`rain_24h_mm`, hourly array) | Summation of 24 hourly rainfall values (mm); mapped to $P_{\text{norm}} = \min(1.0, R_{24h}/100 + I/12)$ | `WeatherService`, `pahad_live_inference.py`, `pahad_fusion.py` | `[LIVE]`, `[CACHED]`, `[SIMULATED]` |
| **Rainfall Intensity (Current)** | Open-Meteo / IMD AWS | JSON (`current_mm_hr`) | Instantaneous hourly rate (mm/h); evaluated against regional I-D curve: $I_{\text{thresh}} = 5.8294 \cdot D^{-0.4141}$ | `pahad_models.py:is_empirical_threshold_exceeded`, `pahad_fusion.py` | `[LIVE]`, `[CACHED]`, `[SIMULATED]` |
| **Antecedent Precipitation ($API_{30d}$)** | IMD AWS / Open-Meteo archive | JSON (30-day history) | Decay-weighted cumulative index $API_t = \sum k^i R_i$ ($k=0.85$); compared to Monga-Ganguli curve | `pahad_live_inference.py`, `pahad_event_predictor.py` | `[LIVE]`, `[CACHED]`, `[HISTORICAL]` |
| **Soil Volumetric Water Content (VWC)** | In-situ capacitive probe / Open-Meteo | JSON / LoRaWAN packet (0–100%) | Inverted van Genuchten (1980) SWCC conversion: $VWC \to$ matric suction $\psi$ (kPa) | `risk_engine.py`, `pahad_live_inference.py` | `[LIVE]`, `[SIMULATED]`, `[MISSING]` |
| **Basal Pore-Water Pressure ($u$)** | Vibrating-wire piezometer / Edge Gateway | LoRaWAN binary $\to$ JSON (kPa) | Saturation ratio $m = \min(1.0, \frac{u}{\gamma_w \cdot z})$; reduces Mohr-Coulomb effective stress | `calculate_infinite_slope_fs`, `risk_engine.py` | `[LIVE]`, `[BENCH_VALIDATED]`, `[SIMULATED]`, `[MISSING]` |
| **Biaxial Hillslope Tilt ($\theta_x, \theta_y$)** | MEMS biaxial tiltmeter / Gateway | LoRaWAN binary $\to$ JSON (degrees) | Vector magnitude $\theta = \sqrt{\theta_x^2 + \theta_y^2}$; rate of angular acceleration ($^\circ/\text{hr}$) | `SensorRegistry`, `pahad_live_inference.py` | `[LIVE]`, `[BENCH_VALIDATED]`, `[SIMULATED]`, `[MISSING]` |
| **Borehole / Surface Displacement** | Inclinometer / Draw-wire extensometer | LoRaWAN / RS485 $\to$ JSON (mm) | Cumulative displacement (mm) & velocity rate ($\text{mm}/\text{day}$); ground anomaly input $A$ | `pahad_fusion.py`, `pahad_live_inference.py` | `[LIVE]`, `[SIMULATED]`, `[MISSING]` |
| **Earthquake Magnitude & Hypocenter** | USGS GeoJSON feed / NCS API | GeoJSON (`mag`, `depth`, `coordinates`) | Distance attenuation filter; peak ground acceleration proxy $g = f(M, \text{hypo\_dist})$ | `SeismicService`, `pahad_live_inference.py` | `[LIVE]`, `[CACHED]`, `[SIMULATED]` |
| **Digital Elevation & Slope Angle ($\beta$)** | Copernicus GLO-30 / ISRO CartoDEM | 30m GeoTIFF / Canonical Registry | Trigonometric slope gradient $\beta = \arctan(\sqrt{p^2 + q^2})$; elevation $z$ in meters | `DEMService`, `calculate_infinite_slope_fs`, `canonical_registry.py` | `[CACHED]`, `[MODELLED]`, `[HISTORICAL]` |
| **InSAR Surface Deformation ($v_{\text{LOS}}$)** | Sentinel-1 InSAR / Bhoonidhi | GeoJSON / CSV raster table | Line-of-sight velocity ($mm/\text{year}$); persistent scatterer temporal displacement series | `pahad_insar.py`, `pahad_fusion.py` | `[HISTORICAL]`, `[MODELLED]`, `[SIMULATED]` |
| **Multispectral Vegetation Index (NDVI)** | Sentinel-2 MSI (B4, B8) | STAC GeoTIFF / Catalog metadata | $\text{NDVI} = \frac{\text{B8} - \text{B4}}{\text{B8} + \text{B4}}$; 30-day temporal drop $\Delta \text{NDVI}$ indicates clearing/fissuring | `VegetationService`, `pahad_live_inference.py` | `[HISTORICAL]`, `[CACHED]`, `[SIMULATED]` |
| **Geotechnical Soil Parameters ($c', \phi', \gamma_{\text{sat}}, z$)** | GSI NLSM lithological compendium / BRO | Python dictionary / DB table | Mohr-Coulomb shear parameters per geologic unit (Daling, Buxa, Siwalik formations) | `calculate_infinite_slope_fs`, `risk_engine.py` | `[HISTORICAL]`, `[MODELLED]` |
| **Corridor Vulnerability Prior ($V$)** | MoRTH / BRO Traffic / Census 2011 | Static canonical dictionary | Normalized scalar $V \in [0.1, 1.0]$ based on highway class, bypass availability, population | `calculate_composite_risk_index`, `pahad_fusion.py` | `[HISTORICAL]` |
| **Field Incident Reports & Tension Cracks** | Citizen PWA & Field Scout Mobile Form | Multipart form (JSON + JPEG) | CV crack aperture detection ($\text{mm}$); crowd consensus spatial clustering | `cv_crack_classifier.py`, `field_evidence_service.py` | `[LIVE]`, `[DEMO]` |
| **Historical Landslide Event Inventory** | GSI National Landslide Repository | Tabular CSV (`historical_landslides_ner.csv`)| 17 verified ground-truth disaster events partitioned into strict temporal windows | `pahad_event_predictor.py`, `models/pahad_event_model.pkl` | `[HISTORICAL]` |
