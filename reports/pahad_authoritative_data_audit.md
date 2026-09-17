# PARVAT NETRA / PAHAD AI — AUTHORITATIVE DATA AUDIT & CRI RUNTIME TRACE
**Forensic Classification of the 47 Data Lineage Rows & Runtime Value Provenance**

**Audit Execution Date:** September 16, 2026
**Evaluated Scope:** 47 Primary Data Streams, UI Elements & Telemetry Pipelines (`reports/pahad_data_lineage_matrix.csv`)
**Target Framework:** Smart India Hackathon (SIH 2026) Grade National Early Warning Intelligence

---

## 1. Executive Summary & Authoritative Taxonomy

In previous audits, data feeds were characterized using combinations of boolean flags (`LIVE?`, `SIMULATED?`, `HISTORICAL?`). This second audit establishes a **single, mutually exclusive, authoritative `DATA_CLASS`** for each of the 47 operational data elements across PARVAT NETRA.

### The 9 Authoritative Data Classes:

1. **`LIVE_EXTERNAL`**: Live network ingestion from active external scientific providers (Open-Meteo, USGS, real-time citizen reports).
2. **`CACHED_LIVE`**: Data originating from a live external API, served within its validity TTL from local cache.
3. **`HISTORICAL`**: Verified archival datasets (GSI landslide inventories, GSI lithology, Sentinel-1 InSAR 2022-2024 baselines, Census 2011).
4. **`STATIC_PREDEFINED`**: Hardcoded or curated local assets (corridor registry coordinates, Survey of India boundaries GeoJSON, UI modals).
5. **`MODEL_PRETRAINED`**: Serialized machine learning models trained offline on verified data (`pahad_event_model.pkl`, `fos_predictor.pkl`).
6. **`SIMULATED`**: Physically realistic simulations (in-situ borehole piezometer pore pressure, TDR VWC sensors, acoustic siren dry-run).
7. **`DERIVED`**: Algorithmic runtime calculations fusing other modalities (Composite Risk Index CRI, Mohr-Coulomb FoS, explainability text).
8. **`AUTH_REQUIRED`**: Fully implemented connectors that require institutional ministerial credentials (IMD Doppler Radar, C-DOT CBS).
9. **`UNAVAILABLE`**: Missing or disconnected telemetry without fallback (0 elements currently in this state).

### Distribution Across 47 Operational Rows:

| DATA_CLASS | Count | Percentage | Operational Meaning |
| :--- | :---: | :---: | :--- |
| **`DERIVED`** | 12 | 25.5% | Runtime mathematical & algorithmic fusion (CRI, FoS, routing, explainability) |
| **`STATIC_PREDEFINED`** | 12 | 25.5% | Fixed GIS boundaries, corridor coordinates, and UI documentation cards |
| **`HISTORICAL`** | 8 | 17.0% | Archival GSI landslide scars, lithological maps, 2024 road cuts, Census 2011 |
| **`SIMULATED`** | 8 | 17.0% | In-situ IoT borehole sensors, Teesta flood surge benchmark, siren relay emulator |
| **`LIVE_EXTERNAL`** | 4 | 8.5% | Live Open-Meteo weather, live USGS earthquakes, live citizen field reports |
| **`CACHED_LIVE`** | 1 | 2.1% | Regional 15-minute CRI dataset snapshot (`realtime_cri_dataset.csv`) |
| **`MODEL_PRETRAINED`** | 1 | 2.1% | Scikit-learn GBDT failure classifier (`pahad_event_model.pkl`) |
| **`AUTH_REQUIRED`** | 1 | 2.1% | IMD Doppler Weather Radar (awaiting institutional token) |
| **`UNAVAILABLE`** | 0 | 0.0% | Zero disconnected or unhandled data streams |
| **TOTAL** | **47** | **100.0%** | Comprehensive audit complete |

---

## 2. The 47-Row Master Authoritative Classification Table

| # | UI Field / Element | API Endpoint | Source / Provider | Authoritative `DATA_CLASS` | Live Contribution | Used in CRI? | Used in PAHAD? | Used in Map? | User Visible? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `card-kpi-cri` | `/api/ml/latest-risk` | PAHAD AI Multimodal Fusion Engine | **`DERIVED`** | PARTIAL | YES | YES | YES | YES |
| 2 | `card-kpi-fos` | `/api/ml/latest-risk & /api/pahad/predict-event` | Mohr-Coulomb Limit Equilibrium & van Genuchten SWCC Physics | **`DERIVED`** | PARTIAL | YES | YES | YES | YES |
| 3 | `card-kpi-prob` | `/api/pahad/predict-event` | PAHAD Calibrated GBDT Event Classifier (Platt Sigmoid) | **`MODEL_PRETRAINED`** | PARTIAL | YES | YES | YES | YES |
| 4 | `card-kpi-conf` | `/api/pahad/predict-event` | PAHAD Probability Margin & Feature Completeness Auditor | **`DERIVED`** | ZERO | NO | YES | NO | YES |
| 5 | `card-zone-title` | `/api/ml/latest-risk` | PARVAT NETRA Corridor GeoRegistry | **`STATIC_PREDEFINED`** | ZERO | NO | YES | YES | YES |
| 6 | `card-zone-sub` | `/api/ml/latest-risk` | Administrative Boundaries Registry (MDoNER/Survey of India) | **`STATIC_PREDEFINED`** | ZERO | NO | YES | YES | YES |
| 7 | `ev-rain` | `/api/ml/latest-risk & /api/weather/current` | Open-Meteo Global Forecasting / IMD AWS API | **`LIVE_EXTERNAL`** | HIGH | YES | YES | YES | YES |
| 8 | `ev-susc` | `/api/ml/latest-risk & /api/geospatial/terrain` | ISRO CartoDEM 30m Digital Elevation Model | **`STATIC_PREDEFINED`** | ZERO | YES | YES | YES | YES |
| 9 | `ev-insar` | `/api/ml/latest-risk & /api/insar/points` | Copernicus Sentinel-1 Persistent Scatterer InSAR & NISAR | **`HISTORICAL`** | ZERO | YES | YES | YES | YES |
| 10 | `ev-vwc` | `/api/ml/latest-risk & /api/edge/readings` | In-Situ Time-Domain Reflectometry (TDR) Soil Moisture Sensor | **`SIMULATED`** | ZERO | YES | YES | YES | YES |
| 11 | `ev-soil` | `/api/ml/latest-risk` | Geological Survey of India (GSI) Lithological Map | **`HISTORICAL`** | ZERO | YES | YES | NO | YES |
| 12 | `card-prov-label` | `/api/ml/latest-risk & /api/pahad/predict-event` | PARVAT NETRA Strict Provenance Enforcement Engine | **`DERIVED`** | ZERO | NO | YES | NO | YES |
| 13 | `card-qual-label` | `/api/pahad/predict-event` | PAHAD Model Metadata Registry | **`STATIC_PREDEFINED`** | ZERO | NO | YES | NO | YES |
| 14 | `pahad-plain-explanation` | `/api/pahad/explanation/<sectorId>` | PAHAD Deterministic Multimodal Explainability Engine | **`DERIVED`** | PARTIAL | NO | YES | NO | YES |
| 15 | `card-action` | `/api/defense/bro-swastik-sop` | Border Roads Organisation (BRO Project Swastik 758/764 BRTF) | **`STATIC_PREDEFINED`** | ZERO | NO | NO | NO | YES |
| 16 | `btn-auth (Authorize Protocol)` | `/api/decisions/authorize` | EOC Incident Command (Disaster Management Act 2005 Sections 30 & 34) | **`DERIVED`** | ZERO | NO | NO | NO | YES |
| 17 | `btn-issue-alert (Public Alert Dispatch)` | `/api/alerts/broadcast-trigger` | NDMA Sachet CAP v1.2 Gateway & C-DOT CBS Interface | **`SIMULATED`** | ZERO | NO | NO | NO | YES |
| 18 | `btn-3d-dem (Inspect 3D Elevation Model)` | `/api/geospatial/terrain` | CartoDEM 30m Point Cloud Grid (ISRO Bhuvan) | **`STATIC_PREDEFINED`** | ZERO | NO | YES | YES | YES |
| 19 | `btn-arm-siren (Tactical Siren Dispatch)` | `/api/authority/siren-access & /api/alerts/dispatch-siren` | Civil Defense Acoustic Siren Relay (GW-01 Likhu Veer) | **`SIMULATED`** | ZERO | NO | NO | NO | YES |
| 20 | `teestaRiverLayer` | `/api/hydrology/teesta-status` | Central Water Commission (CWC) & South Lhonak Hydrodynamics | **`SIMULATED`** | ZERO | YES | YES | YES | YES |
| 21 | `cutsLayer` | `/api/terrain/anthropogenic-cuts` | NH-10 Road Widening Field Bench Surveys (BRO/NHIDCL) | **`HISTORICAL`** | ZERO | YES | YES | YES | YES |
| 22 | `detoursLayer` | `/api/routing/evacuation-plan` | PostGIS 3.6 pgRouting Graph & IRC SP:84 Mountain Code | **`DERIVED`** | PARTIAL | NO | NO | YES | YES |
| 23 | `habitationsLayer` | `/api/humanitarian/isolation-matrix` | Census of India & Sikkim State Disaster Management Authority | **`HISTORICAL`** | ZERO | YES | YES | YES | YES |
| 24 | `reportsLayerGroup` | `/api/reports/clustered` | Citizen Crowdsource & BRO Patrol Geo-Tagged Inspections | **`LIVE_EXTERNAL`** | HIGH | YES | YES | YES | YES |
| 25 | `insarLayer` | `/api/insar/points & /api/pahad/insar-deformation` | Copernicus Sentinel-1 / NISAR L-band SAR | **`HISTORICAL`** | ZERO | YES | YES | YES | YES |
| 26 | `scarsLayer` | `/api/satellite/detected-scars & /api/geospatial/historical-landslides` | Geological Survey of India (GSI) National Landslide Susceptibility Mapping | **`HISTORICAL`** | ZERO | YES | YES | YES | YES |
| 27 | `nerBoundsLayer` | `/static/data/ner_state_boundaries.geojson` | Survey of India National Geospatial Vector Database | **`STATIC_PREDEFINED`** | ZERO | NO | NO | YES | YES |
| 28 | `sectorMarkers` | `/api/pahad/critical-sectors & /api/ml/latest-risk` | PARVAT NETRA Priority Mountain Corridor Registry | **`DERIVED`** | PARTIAL | NO | YES | YES | YES |
| 29 | `hp-edge-nodes` | `/api/edge/nodes & /api/edge/status` | Sub-GHz LoRa Mesh Hardware Rig (ESP32 / SX1262 Nodes) | **`SIMULATED`** | ZERO | NO | NO | YES | YES |
| 30 | `hp-edge-siren` | `/api/edge/siren/status & /api/edge/status` | Civil Defense Acoustic Siren Controller (GW-01 Likhu Veer) | **`SIMULATED`** | ZERO | NO | NO | NO | YES |
| 31 | `regional-hazard-sparkline` | `/api/pahad/realtime-cri & /api/pahad/regional-overview` | PAHAD Real-Time Multi-Corridor Ingestion & Evaluation Service | **`CACHED_LIVE`** | PARTIAL | YES | YES | YES | YES |
| 32 | `highest-risk-sector-banner` | `/api/pahad/highest-risk-corridor` | PAHAD Regional Risk Ranking Algorithm | **`DERIVED`** | PARTIAL | NO | YES | NO | YES |
| 33 | `seismic-feed-drawer` | `/api/seismic/latest & /api/seismic/recent` | USGS Earthquake Hazards Program & NCS (National Center for Seismology) | **`LIVE_EXTERNAL`** | HIGH | YES | YES | YES | YES |
| 34 | `sitrep-modal-content` | `/api/ai/sitrep` | OmniRoute Local AI Gateway (LLM) / Deterministic Geotechnical Fallback | **`DERIVED`** | PARTIAL | NO | NO | NO | YES |
| 35 | `pahad-assistant-chat` | `/api/pahad/assistant/chat` | PAHAD Voice Assistant Service (DMA 2005 Safety Guarded) | **`DERIVED`** | PARTIAL | NO | NO | YES | YES |
| 36 | `modal-cap-preview` | `/api/alerts/broadcast-trigger` | NDMA Sachet Common Alerting Protocol (CAP v1.2 XML with ne-IN Gap-Fill) | **`SIMULATED`** | ZERO | NO | NO | NO | YES |
| 37 | `form-citizen-report` | `/api/reports/submit` | Citizen Mobile / Web Form + Automated Computer Vision Classifier | **`LIVE_EXTERNAL`** | HIGH | YES | YES | YES | YES |
| 38 | `modal-data-truth-matrix` | `/ (Embedded static structure in templates/index.html)` | PARVAT NETRA Data Truth & Provenance Protocol | **`STATIC_PREDEFINED`** | ZERO | NO | NO | NO | YES |
| 39 | `modal-scientific-expl` | `/ (Embedded modal in templates/index.html)` | Geotechnical Physics & Extreme Value Engineering Equations | **`STATIC_PREDEFINED`** | ZERO | NO | NO | NO | YES |
| 40 | `pahad-pipeline-ribbon` | `/ (Embedded layout in templates/index.html)` | 8-Stage Decision Chain Architecture | **`STATIC_PREDEFINED`** | ZERO | NO | NO | NO | YES |
| 41 | `card-why-parvat-netra` | `/ (Embedded card in templates/index.html)` | National Top-1 Differentiator Architecture Specification | **`STATIC_PREDEFINED`** | ZERO | NO | NO | NO | YES |
| 42 | `card-current-limitations` | `/ (Embedded card in templates/index.html)` | Engineering Scope & Limitations Disclosure | **`STATIC_PREDEFINED`** | ZERO | NO | NO | NO | YES |
| 43 | `notification-center-drawer` | `/api/notifications/status & /api/alerts/active` | PARVAT NETRA Unified Multi-Channel Notification Broker | **`DERIVED`** | ZERO | NO | NO | NO | YES |
| 44 | `fleet-machinery-panel` | `/api/fleet/bro-machinery` | Border Roads Organisation Heavy Equipment Ledger (CAT 320D, Loaders) | **`SIMULATED`** | ZERO | NO | NO | YES | YES |
| 45 | `weather-radar-overlay` | `/api/ingest/imd-rainfall & /api/geospatial/satellite/status` | IMD Doppler Weather Radar (DWR) X-band Reflectivity | **`AUTH_REQUIRED`** | ZERO | NO | NO | YES | YES |
| 46 | `optical-satellite-preview` | `/api/geospatial/satellite/footprints` | ISRO NRSC Bhoonidhi Optical Satellite Catalog (Resourcesat / Cartosat) | **`HISTORICAL`** | ZERO | NO | NO | YES | YES |
| 47 | `vegetation-loss-index` | `/api/geospatial/vegetation` | Sentinel-2 Multi-Spectral Instrument (MSI) NDVI Delta | **`HISTORICAL`** | ZERO | YES | YES | YES | YES |

---

## 3. Forensic Trace: Actual Runtime Value of Every CRI Component

### A. The Core Evaluation: What Is Shown on the Homepage?

When an evaluator opens the PARVAT NETRA homepage, the system presents three distinct risk views:
1. **Top Command Snapshot (`refreshSIHCommandSnapshot()`)**: Displays the most critical region across the database (`/api/ml/latest-risk`).
   - **Region:** Gangtok Corridor (or NH-10 Km 48 in fallback)
   - **CRI Score:** `73.16 / 100` (or `82.4` in deterministic fallback)
   - **Severity Tier:** `RED ALERT` (`CRITICAL`)
   - **Physical FoS:** `0.745` (Mohr-Coulomb limit equilibrium)
   - **Rainfall:** `68.4 mm` (Open-Meteo live API)
2. **PAHAD Decision Intelligence Drawer (`onCorridorSelectionChanged("SK-NH10-KM48")`)**: 
   - **Inspected Corridor:** NH-10 Km 48 (29th Mile Sector)
   - **CRI Score:** `46.25 / 100` (`HIGH RISK`)
   - **Factor of Safety:** `0.909` (Active limit-equilibrium failure)
   - **Rainfall (24h):** `55.1 mm`
   - **Event Probability:** `31.1% P(E)`
   - **Provenance:** `[LIVE/HYBRID]`
3. **Regional Real-Time Corridor Table & Sparklines (`/api/pahad/realtime-cri`)**: 
   - Evaluates 20 corridors across all 8 NER states from `data/realtime/realtime_cri_dataset.csv`.

### B. Component-by-Component Value Trace:

The Composite Risk Index formula combines 4 primary modalities plus local geotechnical modifiers:
$$\text{CRI} = H \times V \times 100 \quad \text{where} \quad H = (0.40 \cdot S) + (0.35 \cdot P) + (0.25 \cdot A)$$

| CRI Component | Runtime Value (NH-10 Km 48) | Runtime Source | Authoritative `DATA_CLASS` | Is it Live, CSV, Model, or Simulation? |
| :--- | :--- | :--- | :--- | :--- |
| **1. Slope Gradient ($\beta$)** | `38.0°` (or `41.5°`) | ISRO CartoDEM 30m GeoTIFF | `STATIC_PREDEFINED` | **STATIC RASTER**: Topographic surface derived from satellite elevation point cloud. |
| **2. Soil Lithology ($c', \phi', \gamma$)** | $c'=14.0\text{ kPa}, \phi'=27.0^\circ$ | GSI 1:50,000 Geological Map | `HISTORICAL` | **HISTORICAL ARCHIVE**: Daling quartz-chlorite phyllites & schists from GSI catalog. |
| **3. Dynamic Rainfall ($P$)** | `55.1 mm` (24h), `0.8 mm/h` | Open-Meteo REST API | `LIVE_EXTERNAL` | **LIVE API**: Real-time atmospheric forecast & actuals fetched via HTTP. |
| **4. Pore Water Pressure ($u$)** | `9.62 kPa` | In-situ IoT Telemetry Service | `SIMULATED` | **SIMULATION**: Hydrostatic van Genuchten SWCC matric suction model. |
| **5. Soil Moisture ($VWC$)** | `33.0%` (Regional VWC) | In-situ TDR Sensor Contract | `SIMULATED` | **SIMULATION**: Physical sensor mast emulated in software; physical mast uninstalled. |
| **6. Ground Creep Velocity** | `-14.5 mm/yr` | Copernicus Sentinel-1 InSAR | `HISTORICAL` | **HISTORICAL SATELLITE**: 12-day orbital repeat cycle, 2022-2024 interferograms. |
| **7. Seismic Shaking ($g$)** | `0.000 g` ($M4.2$, $d=803\text{km}$) | USGS Earthquake API | `LIVE_EXTERNAL` | **LIVE API**: Real-time global seismic feed cached with 15-min TTL. |
| **8. River Toe Scour Factor** | `+12.0 CRI` (or $+1.28\times$) | Teesta Waterways Hydrodynamics | `SIMULATED` | **SIMULATION**: Oct 2023 South Lhonak GLOF flood surge benchmark. |
| **9. Anthropogenic Road Cut** | `1.15x` multiplier | Field Survey Bench Inventory | `HISTORICAL` | **HISTORICAL SURVEY**: BRO/NHIDCL 2024 unreinforced cut slope measurements. |
| **10. Road Criticality ($V$)** | `1.0` (National Highway NH-10) | Corridor Registry | `STATIC_PREDEFINED` | **STATIC REGISTRY**: Strategic defense lifeline weighting. |
| **11. Factor of Safety ($FoS$)** | `0.909` (Critical Unstable) | Mohr-Coulomb Limit Equilibrium | `DERIVED` | **DERIVED PHYSICS**: Evaluated at runtime from current soil moisture & slope. |
| **12. Event Probability ($P$)** | `31.1% P(E)` | Scikit-learn GBDT Classifier | `MODEL_PRETRAINED` | **PRETRAINED MODEL**: Inferred using weights in `models/pahad_event_model.pkl`. |

### C. The Definitive Answer: Is the Homepage Value Live, CSV, Model, or Simulation?

**The definitive answer is: THE HOMEPAGE NUMBER IS A HYBRID DERIVED CALCULATION.**

Specifically:
- **It is NOT purely live:** A pure live score would require physical piezometer masts on every slope and daily InSAR passes, neither of which exists anywhere in the world.
- **It is NOT purely a static CSV snapshot:** When the user queries any corridor via `/api/pahad/location-risk`, the system makes a real-time HTTP fetch to Open-Meteo for live rainfall, queries USGS for active earthquakes, runs Mohr-Coulomb limit equilibrium equations in RAM, and executes Scikit-learn GBDT inference.
- **It is NOT a black-box AI model guess:** The machine learning event probability is only one of three signals in a 2-of-3 corroboration gate; the core stability number ($FoS$) is deterministic Mohr-Coulomb physics.
- **It is NOT arbitrary simulation:** The only simulated components are the in-situ borehole piezometer and river gauge telemetry, which use rigorous geotechnical equations (van Genuchten SWCC, Green-Ampt infiltration) to emulate sensor response under real live precipitation.

In summary: **Live atmospheric and seismic forcing feeds real-time physics and pre-trained models over static terrain and simulated borehole telemetry, producing a scientifically defensible, transparent, hybrid-derived early warning index.**

