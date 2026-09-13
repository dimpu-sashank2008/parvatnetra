# PAHAD AI OBSERVATORY — Multimodal Predictive Intelligence Architecture

**Platform**: PARVAT NETRA — NER Sentinel  
**Engine**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Release**: Phase 3.6 Production Final  
**Classification**: National Early-Warning & Geotechnical Decision Observatory  

---

## 1. System Mission & Core Paradigm

The **PAHAD AI Observatory** (`/pahad-ai`) provides a specialized, scientific command and research environment dedicated to the continuous visualization, multi-signal convergence, and transparent evaluation of landslide risk across the North-Eastern Region (NER) of India.

While the primary PARVAT NETRA dashboard (`/`) serves operational dispatchers, responders, and civil defense coordinators, the **Observatory** is tailored for geotechnical engineers, scientific evaluators, and institutional authorities who require transparent insight into:
1. Physical limit-equilibrium mechanics versus statistical machine learning.
2. The exact convergence of multi-modal evidence.
3. Multi-horizon forecasting probabilities (6h, 12h, 24h, 48h).
4. Real-time sensitivity simulation under hypothetical environmental stresses.

---

## 2. 3D Hillslope Digital Twin Viewport

The center of the Observatory features an interactive **Three.js** 3D hillslope digital twin anchored to the Copernicus GLO-30 Digital Elevation Model (DEM) across the Teesta River Basin (NH-10 strategic corridor).

### Core Features
- **Semantic Shading & Surface Draping**: Renders slope gradients, curvature contours, and real-time Factor of Safety (FoS) risk overlays.
- **Topographic Realism**: Realistic mountain morphology with true elevation variance representing the Teesta gorge.
- **Camera Orientation Presets**:
  - `Teesta Valley`: Operational 45° perspective looking up the strategic river corridor.
  - `Orbit View`: Free-orbit rotational examination of slope flanks and drainage gullies.
  - `Nadir 2D`: Orthogonal downward view for spatial risk zoning and corridor alignment.
  - `Cross-Section`: Longitudinal profile revealing basal shear slip plane geometry.
- **Dynamic Lighting**: Directional solar lighting coupled with ambient fill to emphasize slope steepness and escarpments.

---

## 3. Converging Multimodal Telemetry Streams

The hillslope digital twin continuously visualizes the confluence of 6 independent data modalities:

| Stream ID | Modality | Source / Standard | Telemetry Metrics | Provenance |
| :--- | :--- | :--- | :--- | :--- |
| **Stream 1** | **Climate** | IMD Automatic Weather Stations (AWS) | Real-time downpour (mm/h), 24h/72h rainfall, API 30d | `[LIVE AWS]` |
| **Stream 2** | **Terrain** | Copernicus GLO-30 DEM (ESA) | Slope angle (β), profile curvature, aspect, drainage | `[GLO-30 DEM]` |
| **Stream 3** | **Ground In-Situ** | Borehole Piezometers & Inclinometers | Pore-water pressure ($u$), shear displacement rate | `[IOT TELEMETRY]` |
| **Stream 4** | **Satellite EO** | Sentinel-1 InSAR & Sentinel-2 Optical | LOS deformation velocity (mm/yr), NDVI vegetation loss | `[SENTINEL-1/2]` |
| **Stream 5** | **Seismic** | National Center for Seismology (NCS) | Hypocentral distance, magnitude, peak acceleration ($k_h$) | `[NCS / FAULTS]` |
| **Stream 6** | **Historical** | Geological Survey of India (GSI) / NRSC | Documented landslide polygons, recurrence frequency | `[GSI NLFC 1:10K]` |

---

## 4. Eight-Stage Operational Inference Pipeline

The Observatory visualizes the strict eight-stage end-to-end early warning lifecycle:

```
[01. INGEST] ──▶ [02. FUSE] ──▶ [03. FORECAST] ──▶ [04. VERIFY]
       │                │                │                 │
       ▼                ▼                ▼                 ▼
Telemetry        Hybrid Physics    Multi-Horizon     2-of-3 Signal
 Intake           & Spatial ML     GBDT (6-48h)       Concordance
                                                           │
[08. RESPOND] ◀── [07. ROUTE] ◀── [06. WARN] ◀── [05. EXPLAIN]
       │                │                │                 │
       ▼                ▼                ▼                 ▼
BRO & NDRF       Hazard-Aware     Authority Gate    Model Driver
Deployment        Safe Bypass      Push/SMS/CAP      Attribution
```

1. **Ingest**: Ingestion and schema validation of heterogeneous feeds with cryptographic timestamping.
2. **Fuse**: Multi-modal synthesis computing both physical equilibrium ($FoS$) and Composite Risk Index ($CRI$).
3. **Forecast**: Calibrated gradient boosting classification across 6h, 12h, 24h, and 48h temporal horizons.
4. **Verify**: Constitutional 2-of-3 signal concordance validation to eliminate single-sensor false alarms.
5. **Explain**: Deterministic model driver decomposition (Mandal-Sarkar I-D, shear ratio, pore pressure).
6. **Warn**: Multi-channel alert dispatch (Web Push, Mobile Push, SMS, CAP v1.2 XML, LoRa Mesh sirens).
7. **Route**: Dynamic Dijkstra/A* corridor re-routing penalizing severed or high-risk road sectors.
8. **Respond**: Automated tasking of Border Roads Organisation (BRO Project Swastik) plant and SDRF/NDRF teams.

---

## 5. Geotechnical & Physics Formulations

The Observatory explicitly displays the underlying physics and mathematical formulas to avoid black-box opacity:

### 1. Infinite-Slope Mohr-Coulomb Factor of Safety ($FoS$)
$$\text{FoS} = \frac{c' + (\gamma \cdot z \cdot \cos^2\beta - u)\tan\phi'}{\gamma \cdot z \cdot \sin\beta \cos\beta}$$
- $c'$: Effective soil cohesion ($\text{kPa}$)
- $\phi'$: Internal friction angle ($^\circ$)
- $\gamma$: Unit weight of saturated soil ($\text{kN/m}^3$)
- $z$: Depth to sliding plane ($\text{m}$)
- $\beta$: Hillslope inclination angle ($^\circ$)
- $u$: Pore-water pressure at slip surface ($\text{kPa}$)
- **Threshold**: $\text{FoS} < 1.0$ indicates limit-state shear failure.

### 2. Composite Risk Index ($CRI$)
$$H = \alpha \cdot S + \beta \cdot P + \gamma \cdot A$$
$$CRI = H \times V \times 100$$
- $S$: Intrinsic slope susceptibility baseline (GSI 1:10K)
- $P$: Real-time triggering precipitation intensity and antecedent saturation
- $A$: Anthropogenic toe-cutting and road disturbance factor
- $V$: Settlement and highway vulnerability exposure

### 3. Mandal-Sarkar Rainfall Threshold ($I\text{-}D$)
$$I_{\text{threshold}} = 14.82 \cdot D^{-0.39}$$
$$\text{API}_{30\text{d}} = \sum_{t=1}^{30} (0.84^t \cdot R_t)$$
- Validated empirical intensity-duration envelope specifically developed for the Sikkim-Darjeeling Himalayas (Mandal & Sarkar, 2021).

---

## 6. Interactive AI Calculation Visualizer (Simulator)

The Observatory provides a real-time simulation sandbox with 7 parameter sliders:
1. **24h Precipitation Intensity** ($0 - 300\text{ mm}$)
2. **Volumetric Soil Moisture** ($10 - 90\%$)
3. **Pore-Water Pressure ($u$)** ($0 - 100\text{ kPa}$)
4. **Slope Angle ($\beta$)** ($15 - 65^\circ$)
5. **Inclinometer Surface Tilt** ($0.0 - 5.0^\circ$)
6. **Deformation Displacement Rate** ($0.0 - 50.0\text{ mm/day}$)
7. **Seismic Shaking Proxy** ($M\text{ }0.0 - 7.5$)

### Real-Time Outputs
- **Physical $FoS$**: Recalculated dynamically with limit-state color bar.
- **24h Landslide Probability**: Calibrated GBDT response to variable saturation.
- **Composite Risk Index**: Operational risk score ($0 - 100$).
- **Signal Concordance**: Live indication whether the 2-of-3 threshold is satisfied.

---

## 7. Model Transparency & Honest Disclosures

In strict adherence to the **Data Honesty & Provenance Protocol**:
- **Geotechnical $FoS$ Model**: `TRAINED (v1.0)` — Deterministic infinite-slope limit equilibrium mechanics.
- **PAHAD Event Classifier**: `TRAINED_LIMITED_DATA` — Scikit-learn Gradient Boosting Classifier calibrated using Platt scaling on documented GSI historical events.
- **Temporal Deep Learning (LSTM)**: `NOT TRAINED (Surrogate)` — Mathematical surrogate based on decay functions; explicitly marked as not trained to prevent fabricated AI performance claims.
