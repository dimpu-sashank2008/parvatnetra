# PARVAT NETRA • PAHAD AI — PHASE 12F COMPREHENSIVE LIMITATIONS DISCLOSURE
==========================================================================
**Classification**: Uncompromising Scientific Honesty & Technical Transparency  
**Standard**: Smart India Hackathon (SIH) 2026 Grand Finale — MDoNER  
**Core Invariant**: Better to State an Honest Limitation Than to Fabricate Deployment Readiness  

---

## 1. EXECUTIVE STATEMENT OF LIMITATIONS
PARVAT NETRA is an advanced research, decision-support, and emergency operational intelligence prototype. It is engineered to provide national-grade situational awareness for the Northeast Region. To preserve scientific integrity, every limitation of the current software and data architecture is formally documented below.

---

## 2. DETAILED LIMITATION BREAKDOWN

### Limitation 1: Physical In-Situ IoT Sensor Hardware Deployment Gap
* **Current Status**: **`PHYSICAL FIELD DEPLOYMENT: NOT VERIFIED`**
* **Detailed Context**: The platform architecture includes drivers and telemetry ingestion schemas for vibrating wire borehole piezometers, in-place inclinometers, and wireless tiltmeters. However, physical sensor hardware is not currently drilled into the slopes of the 300+ Northeast highway corridors.
* **Operational Handling**: In-situ telemetry in the prototype is simulated using coupled Mohr-Coulomb unsaturated soil infiltration equations. Every UI metric and API response originating from these streams displays the transparent badge **`[SIMULATED]`**.
* **Path to Resolution**: Capital hardware expenditure and physical civil engineering borehole drilling by Border Roads Organisation (BRO) and State Disaster Management Authorities (SDMAs).

---

### Limitation 2: Historical Landslide Event Catalog Sample Size
* **Current Status**: **`TRAINED_LIMITED_DATA / RESEARCH PROTOTYPE`**
* **Detailed Context**: The statistical landslide event classifier is trained on a curated inventory of 17 documented historical failure events across the Northeast Region and 19 geographically matched negative control windows (36 total labeled windows; held-out temporal test set $N=8$).
* **Operational Handling**: The model is properly calibrated using Platt scaling ($Brier = 0.082$), but its classification metrics cannot be claimed as "universal production-grade". It functions as a defensible research prototype.
* **Path to Resolution**: Systematic ingestion of historical landslide failure archives from the Geological Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM) program across all 8 NER states.

---

### Limitation 3: Recurrent Deep Learning Sequence Data Gap
* **Current Status**: **`NOT_TRAINED / PHYSICS-INFORMED TEMPORAL SURROGATE`**
* **Detailed Context**: True training of an LSTM or GRU recurrent neural network requires dense, continuous, multi-year sequence observations with second-by-second failure timestamps. The historical GSI landslide catalog exhibits timestamp uncertainties of $\pm 6\text{h}$ to $24\text{h}$ and sparse observation intervals.
* **Operational Handling**: Under `engine/pahad_temporal_gate.py`, training recurrent models is strictly blocked by the hard gate `DATA_COLLECTION_REQUIRED`. The surrogate module `engine/pahad_lstm.py` is explicitly identified as an unweighted mathematical surrogate.
* **Path to Resolution**: 12+ months of continuous, unbroken high-frequency in-situ IoT telemetry collection from instrumented pilot corridors.

---

### Limitation 4: Earth Observation & Remote Sensing Latency
* **Current Status**: **`HISTORICAL / ASYNCHRONOUS RADAR UPDATE INTERVALS`**
* **Detailed Context**: Sentinel-1 Synthetic Aperture Radar (SAR) interferometry provides millimeter-accuracy line-of-sight displacement velocities ($v_{LOS}$). However, satellite repeat passes occur every 6 to 12 days. In addition, steep Himalayan gorges frequently suffer from radar shadow and layover.
* **Operational Handling**: InSAR deformation velocities are used as an antecedent structural vulnerability indicator rather than an instantaneous real-time trigger.
* **Path to Resolution**: Deployment of ground-based interferometric radar (GB-InSAR) and optical drone photogrammetry patrols by quick-response teams.

---

### Limitation 5: Upstream Institutional API Authentication
* **Current Status**: **`AUTH_REQUIRED / PUBLIC FALLBACK ACTIVE`**
* **Detailed Context**: Official gridded rainfall products and Doppler radar from the India Meteorological Department (IMD) require institutional API tokens and dedicated network whitelist access.
* **Operational Handling**: When official IMD credentials are unconfigured, the system automatically falls back to Open-Meteo GFS/ECMWF numerical weather prediction feeds with explicit badge **`[AUTH_REQUIRED / FALLBACK_OPEN_METEO]`**.
* **Path to Resolution**: Formal institutional MoU between MDoNER/NDMA and IMD for direct institutional API token provisioning.

---

### Limitation 6: Geotechnical Infinite-Slope 1D Assumptions
* **Current Status**: **`TRANSLATIONAL SLIP EQUILIBRIUM ASSUMPTION`**
* **Detailed Context**: The physical Factor of Safety ($FoS$) engine implements the 1D infinite-slope limit equilibrium model. This assumes translational planar failure along a sliding surface parallel to the slope face.
* **Operational Handling**: Accurate for shallow translational slides typical of Himalayan weathered regolith, but does not calculate 3D circular Bishop rotational slip surfaces.
* **Path to Resolution**: Integration of 3D finite-element limit equilibrium models (e.g., GeoStudio / PLAXIS) for complex urban slope geometries.

---

## 3. SUMMARY COMPARISON: UNFOUNDED CLAIMS VS. DOCUMENTED REALITY

| Potential Overclaim (Disallowed) | Documented System Reality (Enforced) |
| :--- | :--- |
| *"We installed smart sensors across all Northeast highways."* | **Physical in-situ sensors are simulated; deployment status is NOT VERIFIED.** |
| *"Our LSTM deep learning model predicts landslides 48h in advance."* | **Recurrent model is NOT TRAINED; LSTM is an unweighted temporal surrogate.** |
| *"Our AI achieves 99.9% real-world landslide prediction accuracy."* | **Statistical model is trained on 17 events; status is TRAINED_LIMITED_DATA.** |
| *"The AI automatically sounds sirens to save towns."* | **AI actuation is permanently locked out (DMA 2005); human sign-off is mandatory.** |
| *"All sensor data on the dashboard is live."* | **Every stream displays exact provenance: Open-Meteo is [LIVE], IoT is [SIMULATED].** |
