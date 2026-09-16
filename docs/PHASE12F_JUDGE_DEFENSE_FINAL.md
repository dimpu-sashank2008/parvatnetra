# PARVAT NETRA • PAHAD AI — PHASE 12F FINAL JUDGE DEFENSE HANDBOOK
==================================================================
**Purpose**: Absolute Evaluator Defense & Scientific Integrity Doctrine  
**SIH 2026 Grand Finale**: Ministry of Development of North Eastern Region (MDoNER)  
**Quick-Access UI Panel**: Available via `[JUDGE DEFENSE 12E]` trigger on Dashboard  

---

## 1. THE 10 CANONICAL DEFENSES (RAPID EVALUATOR AUDIT)

### JQ-01: WHAT IS PAHAD AI?
* **Core Defense**: PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response) is the dual-engine geotechnical early warning system of PARVAT NETRA. It pairs deterministic infinite-slope Mohr-Coulomb limit equilibrium physics ($FoS$) with an empirical calibrated `GradientBoostingClassifier` predicting landslide event probabilities ($P(\text{event})$) across 6h, 12h, 24h, and 48h horizons. These outputs, alongside satellite InSAR line-of-sight subsidence velocities and antecedent precipitation, synthesize into the Composite Risk Index (CRI $[0-100]$).
* **Code Reference**: `engine/pahad_models.py` (Physics), `engine/pahad_event_predictor.py` (ML), `engine/pahad_live_inference.py` (CRI).
* **Limitation**: Model status is `TRAINED_LIMITED_DATA / RESEARCH PROTOTYPE` (calibrated on 17 historical failures, 19 controls).

### JQ-02: WHAT IS CRI?
* **Core Defense**: The Composite Risk Index (CRI) is a bounded $[0, 100]$ multi-criteria hazard aggregation stratified into four operational risk bands: STABLE ($<30$), WATCH ($30-50$), WARNING ($50-70$), and CRITICAL ($\ge 70$). CRI is transparent and deterministic—computed via audited weights across geotechnical shear stress, antecedent precipitation, satellite InSAR deformation, and seismo-tectonic peak ground acceleration.
* **Code Reference**: `engine/pahad_live_inference.py:calculate_composite_risk_index`.
* **Limitation**: Weight coefficients are calibrated on Eastern Himalayan steep schists and phyllites.

### JQ-03: WHY FOS?
* **Core Defense**: Factor of Safety ($FoS = \tau_f / \tau_d$) enforces Newtonian limit-equilibrium physical laws, preventing statistical machine learning from hallucinating false landslides on mechanically stable slopes. Formulated via infinite-slope Mohr-Coulomb mechanics:
  $$FoS = \frac{c' + (\gamma z \cos^2\beta - u)\tan\phi'}{\gamma z \sin\beta\cos\beta}$$
  If $FoS > 1.5$, structural hillslope failure is mechanically impossible regardless of noisy sensor readings.
* **Code Reference**: `engine/pahad_models.py:calculate_infinite_slope_fs`.
* **Limitation**: Evaluates 1D translational infinite slope; 3D rotational slip requires localized borehole logs.

### JQ-04: WHY ML?
* **Core Defense**: Static limit-equilibrium formulas evaluate instantaneous stability but lack predictive temporal lead time. Our calibrated `GradientBoostingClassifier` evaluates non-linear multi-variate interactions—such as 72h antecedent rainfall saturation curves, cumulative pore pressure buildup, regional lithological susceptibility, and geomorphic curvature—to output well-calibrated event probabilities (Platt scaling / $Brier = 0.082$) over 6h, 12h, 24h, and 48h horizons.
* **Code Reference**: `engine/pahad_event_predictor.py:predict_event_probability`.
* **Limitation**: Calibrated on documented NER landslide inventory (`TRAINED_LIMITED_DATA`).

### JQ-05: WHY NOT LSTM?
* **Core Defense**: PARVAT NETRA strictly rejects deep learning theater. Training a recurrent neural network (LSTM/GRU) requires dense, unbroken multi-year sequence observations with accurate failure timestamps. Historical GSI catalogs have timestamp uncertainties of $\pm 6\text{h}$ to $24\text{h}$ and sparse intervals. Under `engine/pahad_temporal_gate.py`, training recurrent models is blocked under the hard gate `DATA_COLLECTION_REQUIRED`. Module `engine/pahad_lstm.py` is explicitly identified as an unweighted temporal surrogate (`NOT_TRAINED / SURROGATE`).
* **Code Reference**: `engine/pahad_temporal_gate.py`, `engine/pahad_lstm.py`.
* **Limitation**: Recurrent deep learning is frozen until 12+ months of continuous in-situ IoT telemetry is collected.

### JQ-06: WHAT IS LIVE?
* **Core Defense**: Live data comprises authenticated, real-time public feeds: Open-Meteo NWP weather (hourly precipitation, temperature, wind), USGS Global Earthquake API (M2.5+ events), National Center for Seismology (NCS) India regional seismic feed, PostGIS spatial network routing graph, and local persistent SQLite observation store.
* **Code Reference**: `engine/pahad_explanation_engine.py:LiveDataStatusAuditor`.
* **Limitation**: Upstream third-party rate limits and external internet routing latency.

### JQ-07: WHAT IS SIMULATED?
* **Core Defense**: In-situ borehole sensors, physical siren hardware, and offline institutional feeds are transparently badged as `[SIMULATED]` or `[AUTH_REQUIRED]`—never fabricated as live. In-situ piezometers and borehole inclinometers are explicitly disclosed as `PHYSICAL FIELD DEPLOYMENT: NOT VERIFIED`. IMD Radar is marked `[AUTH_REQUIRED]`. Sentinel-1 InSAR is marked `[HISTORICAL / PROCESSED]`.
* **Code Reference**: `engine/pahad_explanation_engine.py:get_provider_truth_audit`.
* **Limitation**: Physical hardware deployment requires state capital expenditure.

### JQ-08: HOW DO YOU PREVENT FALSE ALERTS?
* **Core Defense**: False alerts are prevented through a 3-tier defense: (1) **2-of-3 Multi-Signal Corroboration**: An alert requires convergence across at least two independent domains: [A] Geotechnical ($FoS < 1.15$), [B] Hydrological ($Rain_{24h} > 75\text{mm}$), [C] InSAR ($v_{LOS} < -10\text{mm/yr}$). A single outlier sensor cannot trigger an alert; (2) **Temporal Persistence**: Anomalies must persist across 2 consecutive polling cycles; (3) **Statutory Human-in-the-Loop**: DMA 2005 mandates District Authority sign-off.
* **Code Reference**: `engine/pahad_explanation_engine.py:evaluate_corroboration`.
* **Limitation**: Radar shadow and monsoon cloud cover can introduce latency in InSAR updates.

### JQ-09: CAN AI TRIGGER THE SIREN?
* **Core Defense**: **ABSOLUTELY NOT.** Under the Disaster Management Act 2005 (Sections 30 & 34) and NDMA standard operating procedures, autonomous algorithmic activation of public sirens or mass emergency broadcasts is strictly illegal. The system maintains permanent safety interlocks: `ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`, `PUBLIC_DEMO_TEST_ONLY=1`. When voice assistant or API receives an actuation command like "Sound the siren", it immediately returns `REJECTED_SAFETY`.
* **Code Reference**: `services/pahad_voice_assistant.py`, `app.py:dispatch_siren`.
* **Limitation**: Requires authenticated human Incident Commander authorization.

### JQ-10: WHAT IS YOUR BIGGEST LIMITATION?
* **Core Defense**: Our most significant technical limitation is the absence of a dense, verified in-situ physical sensor network (borehole piezometers and inclinometers) continuously deployed along all 300+ Northeast highway corridors. In-situ telemetry in the prototype is simulated based on physical soil mechanics equations rather than physical hardware embedded in the hillsides (`Physical field deployment: NOT VERIFIED`).
* **Code Reference**: `docs/PAHAD_MODEL_CARD.md`, `engine/pahad_temporal_gate.py`.
* **Limitation**: Full operational deployment requires hardware capital expenditure by BRO / State Disaster Authorities.

---

## 2. PIVOT STRATEGY: HOW TO WIN EVALUATOR RESPECT

| When the Judge Says... | Do NOT Say... | DO Say (The PARVAT NETRA Pivot)... |
| :--- | :--- | :--- |
| *"Your ML accuracy must have false positives."* | *"Our model has 99% accuracy."* | *"You're entirely right, Professor. Single ML models overfit. That is why our architecture prevents ML from acting alone: we enforce limit-equilibrium Mohr-Coulomb physics ($FoS$) and our 2-of-3 Corroboration Heuristic."* |
| *"You can't deploy this tomorrow without real sensors."* | *"The sensors are real, they are working right now."* | *"Sir, we completely agree. That is why our UI transparently badges in-situ sensors as [SIMULATED] and discloses 'Physical field deployment: NOT VERIFIED'. We built the verified software intelligence layer ready for state hardware integration."* |
| *"Why isn't this connected to the national siren grid?"* | *"We can turn on the siren with one API call."* | *"Under Indian law (DMA 2005 Sections 30 & 34), autonomous AI actuation of public sirens is illegal. We have permanently locked our hardware relays in dry-run mode (`SIREN_DRY_RUN=1`) because public safety mandates human authority sign-off."* |
