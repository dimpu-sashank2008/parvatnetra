# PARVAT NETRA / PAHAD AI — PHASE 11K
## JUDGE Q&A EVIDENCE SHEET
**SIH 2026 — TOP-500 → TOP-5 EVALUATION PREPARATION**
*Defensible, Evidence-Backed Responses to Technical, Operational, and Safety Inquiries*

---

### Q1: What exactly does AI do in PARVAT NETRA?
**Evidence-Backed Answer:**  
AI does not replace geotechnical physics or statutory authorities; it performs three distinct, mathematically rigorous tasks:
1. **Multimodal Feature Fusion:** Integrates heterogeneous data streams (hydrometeorology, InSAR/NDVI, piezometric pore-water pressure, seismicity, and slope geometry) into a unified state vector.
2. **Empirical Event Probability Estimation:** Evaluates a Platt-calibrated Gradient Boosting Classifier (`PAHAD-Event-Classifier`) to estimate the conditional likelihood of a slope failure given antecedent rainfall and terrain characteristics.
3. **Operational Decision Support & Triage:** Synthesizes complex geotechnical telemetry into an explainable, 4-tier Composite Risk Index (CRI) and recommends statutory standard operating procedures (SOP Stage 1 to 4) under the Disaster Management Act, 2005.  
*Repository Proof:* `engine/pahad_event_classifier.py`, `engine/pahad_data_fusion.py`, `services/ai_triage.py`.

---

### Q2: Why not just use rainfall thresholds like traditional warning systems?
**Evidence-Backed Answer:**  
Rainfall is an external trigger, not the mechanical cause of slope failure. In the Himalayas:
- Slopes with identical rainfall fail at wildly different thresholds depending on antecedent soil moisture, geotechnical shear strength (cohesion $c'$ and friction angle $\phi'$), slope gradient ($\beta$), and anthropogenic toe cutting.
- In dry pre-monsoon conditions, heavy rain merely saturates the vadose zone without triggering failure; whereas late-monsoon light rain on saturated colluvium causes catastrophic failure.  
*Repository Proof:* `engine/pahad_geotechnical.py` calculates effective stress $\sigma' = \sigma - u$, showing that pore-water pressure ($u$) rather than surface precipitation alone dictates shear failure.

---

### Q3: Why calculate Factor of Safety (FoS)?
**Evidence-Backed Answer:**  
Factor of Safety ($FoS$) provides a deterministic, physically grounded engineering foundation rooted in limit equilibrium:
$$\text{FoS} = \frac{c' + (\gamma z \cos^2\beta - u)\tan\phi'}{\gamma z \sin\beta \cos\beta}$$
- When $FoS > 1.3$, the slope is physically stable under configured parameters.
- When $1.0 \le FoS \le 1.3$, the slope is in conditional equilibrium.
- When $FoS < 1.0$, calculated driving shear stresses exceed resisting shear strength.  
Crucially, $FoS$ is not an empirical black box; it obeys Mohr-Coulomb physical mechanics and provides immediate physical explainability to Border Roads Organisation (BRO) and civil engineers.  
*Repository Proof:* `engine/pahad_engine.py`, `tests/test_pahad_engine.py`.

---

### Q4: Why calculate Composite Risk Index (CRI) instead of relying solely on FoS?
**Evidence-Backed Answer:**  
$FoS$ measures physical slope stability at a single point, but disaster risk is a function of hazard, vulnerability, and exposure:
$$\text{CRI} = H \times V \times 100 \quad \text{where } H = 0.40S + 0.35P + 0.25A$$
- An unstable slope ($FoS = 0.85$) in an uninhabited, barren gorge poses minimal civil risk ($V = 0.5$).
- An unstable slope ($FoS = 0.95$) directly abutting the lifeline highway NH-10 near 29th Mile Settlement (Pakyong District) with heavy transit and military traffic represents an extreme societal risk ($V = 1.25$).  
CRI bridges the gap between pure geotechnical physics and emergency operational prioritization.  
*Repository Proof:* `engine/pahad_data_fusion.py`, `PROJECT_HANDOFF.md` Section 3.

---

### Q5: What is the training dataset for the event model?
**Evidence-Backed Answer:**  
The event model is trained exclusively on real, curated historical events from Geological Survey of India (GSI) records and national disaster incident logs across the North Eastern Region:
- **Total Master Ground-Truth Samples:** 36 records in `data/labels/event_labels.csv`.
- **Documented Landslide Events ($y=1$):** 17 events across 15 NER districts (2022–2024).
- **Defensible Stable Control Windows ($y=0$):** 19 verified non-failure windows during monitored monsoon seasons.
- **Strict Separation:** Synthetic demo records are isolated in `data/features/demo_train.csv` and are strictly excluded from operational model training.  
*Repository Proof:* `data/README.md`, `reports/pahad_data_quality_report.md`.

---

### Q6: Why is your training dataset small (36 samples)?
**Evidence-Backed Answer:**  
We practice strict scientific honesty. High-resolution geotechnical sensor data and multi-modal meteorological observations linked to precisely timestamped historical landslide failure planes across NER are rare in national repositories.  
Rather than fabricating synthetic data or hallucinating hundreds of fake landslides to inflate accuracy metrics, we restricted supervised event modeling to 36 rigorously verified historical records. As mandated by scientific auditing, our model status is formally designated as `TRAINED_LIMITED_DATA`.  
*Repository Proof:* `docs/PAHAD_MODEL_CARD.md`, `reports/PHASE11J_DATA_ARTIFACT_PARITY.json`.

---

### Q7: What are your current model metrics?
**Evidence-Backed Answer:**  
On our held-out real evaluation partition:
- **Calibration Quality (Brier Score):** `0.0824` (demonstrating well-calibrated probabilistic output via Platt Sigmoid).
- **Evaluation Strategy:** Temporal Holdout (training on earlier seasons, validating on subsequent periods) to avoid temporal leakage.
- **Limitation Statement:** Due to the small sample size (8 test samples), we report that test set accuracy and ROC-AUC are statistically constrained and must not be over-generalized as production deployment proof.  
*Repository Proof:* `models/pahad_event_metrics.json`, `reports/pahad_calibration_report.md`.

---

### Q8: Can this system generalize across the entire North Eastern Region (NER)?
**Evidence-Backed Answer:**  
Yes, at the architectural and physical tier, because:
1. **Geotechnical Physics Generalization:** The infinite-slope Mohr-Coulomb equations parameterize regional geological lithology (phyllite, schist, shale, sandstone) using Geological Survey of India 1:50,000 lithological mapping across all 8 NER states.
2. **Standardized Spatial Grid:** Terrain attributes (slope, aspect, curvature, catchment area) are derived from nationwide SRTM 30m DEM tiles.
3. **26 Canonical Corridors:** Pre-configured corridors exist across Sikkim, Arunachal Pradesh, Assam, Meghalaya, Manipur, Mizoram, Nagaland, and Tripura.  
*Repository Proof:* `data/cache/terrain/`, `services/offline_routing_service.py`.

---

### Q9: What happens when the live weather API fails or disconnects?
**Evidence-Backed Answer:**  
The system implements a 4-tier deterministic failover:
1. `IMD API` (Primary National Tier — when configured).
2. `Open-Meteo API` (Secondary Live Global Fallback).
3. `Local Disk Cache` (Serves last verified observation within 900s TTL).
4. `Himalayan Climatological Model` (Deterministic localized rainfall estimation).  
When live feeds fail, the system automatically degrades its provenance badge to `[CACHED]` or `[FALLBACK]`, lowers data quality confidence to `DEGRADED`, and logs the event without interrupting core monitoring.  
*Repository Proof:* `services/weather_service.py`, `tests/test_weather_service.py` (8/8 PASSED).

---

### Q10: What happens when in-situ geotechnical sensors fail or deliver corrupted data?
**Evidence-Backed Answer:**  
PARVAT NETRA never halts due to missing telemetry. In-situ sensors are corroborated against regional satellite and hydrometeorological signals. If a piezometer disconnects:
- The missing feature is flagged with provenance `MISSING`.
- Physical $FoS$ falls back to hydrological steady-state water table estimation ($m = h/z$ derived from 72h antecedent rainfall).
- Data quality rating drops from `COMPLETE` to `PARTIAL DATA`, and the UI displays an explicit warning.  
*Repository Proof:* `engine/pahad_data_fusion.py`, `engine/pahad_geotechnical.py`.

---

### Q11: What happens when the network fails completely in a remote mountain valley?
**Evidence-Backed Answer:**  
The entire platform is built for Himalayan field resilience:
1. **Local Offline Graph Routing:** BRO freight and civilian bypass calculations fall back to pre-compiled local NetworkX graphs without calling external routing APIs.
2. **Zero External CDN Dependencies:** Leaflet JS, CSS stylesheets, and vector assets are self-contained in `/static/`.
3. **Field Mobile Synchronization:** The mobile application queues field reports in SQLite/IndexedDB and synchronizes automatically upon reconnecting.  
*Repository Proof:* `services/offline_routing_service.py`, `docs/PHASE11J_DEPLOYMENT_HARDENING_REPORT.md`.

---

### Q12: Can AI trigger an acoustic siren independently?
**Evidence-Backed Answer:**  
**ABSOLUTELY NOT.** The system enforces hard physical and architectural safety interlocks:
- Environmental variable `SIREN_DRY_RUN=1` is enforced.
- The hardware relay driver is locked to `DRY_RUN_EMULATOR`.
- Voice assistant commands attempting to trigger or disarm sirens are intercepted and blocked by regex patterns.
- Siren activation requires an HMAC-signed command payload authorized by a designated EOC officer.  
*Repository Proof:* `backend/edge/siren_controller.py`, `services/pahad_voice_assistant.py`, `scratch/test_safety_gates.py`.

---

### Q13: Can PARVAT NETRA issue a public emergency alert (SMS/CAP) without human intervention?
**Evidence-Backed Answer:**  
**NO.** Under Section 30 of the Disaster Management Act, 2005, public warning authority is legally vested exclusively in the District Magistrate and State Disaster Management Authority (SDMA):
- `ENABLE_PUBLIC_DISPATCH=0` is hardcoded in the deployment configuration.
- `CAP_PRODUCTION_DISPATCH=0` and `SACHET_PRODUCTION_DISPATCH=0` gate public cell broadcasts.
- The AI produces an `AI_RECOMMENDATION`. The operational workflow enforces:  
  $$\text{AI Recommendation} \longrightarrow \text{EOC Authority Review} \longrightarrow \text{DM Approval} \longrightarrow \text{Authorized Dispatch}$$
*Repository Proof:* `services/eoc_service.py`, `engine/operational_state_machine.py`.

---

### Q14: How do you prevent false alarms from triggering unnecessary evacuations?
**Evidence-Backed Answer:**  
We enforce the **Multi-Signal Corroboration Rule (2-of-3)**:
An incident will NOT escalate to `STAGE 4 (RESPONSE)` or generate an evacuation recommendation unless at least 2 of the 3 distinct signals corroborate:
1. Physical Factor of Safety $FoS < 1.0$ (Mechanistic Limit Equilibrium).
2. Rainfall accumulation exceeds Mandal-Sarkar empirical I-D threshold.
3. Machine learning event likelihood $P(\text{event}) \ge 0.30$.  
A transient spike in a single sensor cannot trigger an alert recommendation.  
*Repository Proof:* `engine/pahad_data_fusion.py`, `tests/test_pahad_data_fusion.py`.

---

### Q15: How do you avoid data leakage between train and test datasets?
**Evidence-Backed Answer:**  
We built an explicit leakage verification script (`scripts/check_event_leakage.py`):
- **Temporal Holdout:** Data is split strictly chronologically (older seasons $\to$ Train; subsequent seasons $\to$ Val; most recent $\to$ Test).
- **Geographic Grouping:** Spatial sequences from the same localized failure cluster are never split across train and test.
- **Zero Future Features:** All features (e.g. 24h/72h rainfall) strictly precede the event timestamp.  
*Repository Proof:* `scripts/check_event_leakage.py`, `reports/pahad_validation_strategy.md`.

---

### Q16: What is the exact status of your temporal LSTM model?
**Evidence-Backed Answer:**  
The temporal LSTM is officially classified as **`NOT_TRAINED / MATHEMATICAL SURROGATE`**.  
While `engine/pahad_lstm.py` contains a mathematical surrogate representing sequence decay, we refuse to claim a deep recurrent neural network has been production-trained because requisite multi-year, minute-resolution in-situ sensor time-series datasets do not exist for these sectors.  
*Repository Proof:* `docs/PAHAD_MODEL_CARD.md`, `app.py`.

---

### Q17: What parts of PARVAT NETRA are live and operating today?
**Evidence-Backed Answer:**  
- **Live APIs:** Open-Meteo precipitation feeds and USGS global seismic telemetry.
- **Live Physics Engine:** Real-time infinite-slope Mohr-Coulomb Factor of Safety computation for 26 corridors.
- **Live Risk Ranking:** Dynamic Composite Risk Index (CRI) calculation and sector prioritization.
- **Live Offline Routing:** Multi-profile Dijkstra/A* freight and bypass road graph navigation.
- **Live RBAC & State Machine:** EOC incident triage, geofencing, and audit logging.  
*Repository Proof:* `app.py`, `PROJECT_HANDOFF.md`.

---

### Q18: What features remain blocked or require institutional deployment?
**Evidence-Backed Answer:**  
1. **IMD & NCS Institutional Connectors:** Blocked pending official ministerial API key provisioning (currently marked `UNCONFIGURED / AUTH_REQUIRED`).
2. **Physical Siren Hardware:** Kept in software dry-run emulation (`SIREN_DRY_RUN=1`) until physical sirens are commissioned on highway masts.
3. **Public Emergency Dispatch:** Locked to prevent civilian panic (`ENABLE_PUBLIC_DISPATCH=0`).
4. **Deep Sequence Modeling:** Blocked until multi-month in-situ sensor telemetry accumulates.  
*Repository Proof:* `docs/PHASE11H_RISK_REGISTER.md`.

---

### Q19: How would a state government or SDMA deploy this platform?
**Evidence-Backed Answer:**  
1. **Infrastructure Deployment:** Docker container deploys on State Data Centre (SDC) servers or National Informatics Centre (NIC) cloud in under 5 minutes.
2. **Corridor Configuration:** Civil authorities provide road shapefiles and sensor locations.
3. **Authority Integration:** District Magistrates receive authenticated EOC accounts with DMA 2005 authorization credentials.
4. **Institutional Gateway Activation:** IMD/CWC/NCS enterprise API credentials are configured in `.env`.  
*Repository Proof:* `Dockerfile`, `render.yaml`, `PROJECT_HANDOFF.md`.

---

### Q20: What is PARVAT NETRA’s single strongest differentiator compared to other SIH projects?
**Evidence-Backed Answer:**  
**Multimodal Scientific Grounding with Statutory Safety.**  
Most disaster tech projects present either a basic weather map or an unexplainable AI that claims 100% accuracy. PARVAT NETRA combines:
1. First-principles geotechnical mechanics (Mohr-Coulomb FoS) that civil engineers trust.
2. Multi-signal corroboration that filters out sensor noise and false alarms.
3. Strict legal alignment with India's Disaster Management Act, 2005 (AI recommends, human authority decides).
4. Complete scientific honesty regarding small datasets and data provenance.  
*Repository Proof:* Core Project Constitution & Agent Rules (`AGENTS.md`).
