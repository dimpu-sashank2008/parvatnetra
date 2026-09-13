# PARVAT NETRA / PAHAD AI — PHASE 6F
## Final Pilot Readiness Gate & Governance Audit Report

**Document ID**: `PAHAD-REPORT-6F-FINAL-01`  
**Classification**: National Landslide Early Warning System Governance Report  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Audit Phase**: Phase 6F — Final Pilot Readiness Gate  
**Corridor**: Primary: `CORR-NH10-SIKKIM-KM48` (Pakyong District, Sikkim / Project Swastik BRO)  
**Evaluation Target**: Controlled Supervised Operational Pilot  
**Final System Verdict**: `READY_FOR_CONTROLLED_SUPERVISED_PILOT`  
*(Constrained strictly to SHADOW or SUPERVISED_PILOT mode; PUBLIC_DISPATCH = DISABLED; Physical slope instrumentation & IMD Doppler Radar credentials remain external prerequisites).*

---

### SYSTEM STATUS
- **Core Platform**: PARVAT NETRA — National Landslide Disaster Intelligence
- **AI Engine**: PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)
- **Operational Mode**: `SUPERVISED_PILOT` / `SHADOW`
- **Public Dispatch Status**: `DISABLED` (Sirens in `DRY_RUN`)
- **Software Readiness Score**: **1.000 / 1.000** (100% PASS)
- **Data Governance Score**: **1.000 / 1.000** (100% PASS)
- **Model Readiness Score**: **0.850 / 1.000** (PASS — `TRAINED_LIMITED_DATA`)
- **Field Readiness Score**: **0.300 / 1.000** (FAIL — `PHYSICAL_DEPLOYMENT_PENDING`)
- **Institutional Readiness Score**: **0.400 / 1.000** (PARTIAL — `AUTH_REQUIRED`)
- **Operational Workflow Score**: **0.950 / 1.000** (PASS)

---

### DATA GATE: PASS
- **Canonical Verified Historical Events**: Exactly **17** authenticated catastrophic landslides across all 8 North Eastern Region (NER) states (`EV-01` to `EV-17`). Zero events excluded.
- **Baseline Observation Dataset**: Exactly **36** balanced samples ($N=16$ train, $N=12$ val, $N=8$ test; 17 positive events, 19 negative control windows).
- **Antecedent Temporal Expansion**: Exactly **105** samples ($17 \text{ events} \times 5 \text{ windows} = 85$ event windows, 20 independent controls; $N=48$ train, $N=33$ val, $N=24$ test).
- **Leakage Elimination**: Zero temporal lookahead ($T_{\text{obs}} < T_{\text{event}}$), monotonically increasing rainfall windows, chronological holdout split ($\le 2023$, H1 2024, H2 2024), 0 cross-partition duplicates.
- **Provenance & Synthetic Isolation**: All samples tagged with explicit provenance (`[HISTORICAL]`, `[DERIVED]`, `[SIMULATED]`, `[DEMO]`). Synthetic evaluation samples strictly quarantined in `demo_train.csv`.
- **Dataset Lineage**: Training dataset SHA-256 hash verified: `79ece554620f4c3ea89d5f714658a5c2dff5b7964b732f7035ebca6d09bbfe68`.

---

### MODEL GATE: PASS (TRAINED_LIMITED_DATA / RESEARCH_PROTOTYPE)
- **Architecture Decoupling**: Physical Mohr-Coulomb Factor of Safety (Model A, `models/pahad_fos_model.pkl`) is completely decoupled from the Empirical Landslide Event Probability Classifier (Model B, `models/pahad_event_model.pkl`).
- **Multi-Horizon Models**: Independent calibrated GBDT classifiers active for 6h, 12h, 24h, and 48h (`models/pahad_event_model_{6h,12h,24h,48h}.pkl`).
- **Probability Calibration**: Platt sigmoid calibration applied, reducing Brier score to 0.0824 on held-out test data.
- **Deep Sequence Model (LSTM)**: `engine/pahad_lstm.py` explicitly identified as a `MATHEMATICAL_SURROGATE` (`NOT_TRAINED` deep neural network). Zero fabricated weights claimed.
- **Governance Classification**: Explicitly classified as `TRAINED_LIMITED_DATA` / `RESEARCH_PROTOTYPE`. Supervised human oversight is mandatory.

---

### WEATHER GATE: PARTIAL
- **Operational Fallback Stream**: Open-Meteo REST API is fully operational and continuously streaming real-time precipitation and forecasts, transparently labeled `[LIVE / OPEN_METEO]`.
- **Authoritative Stream Status**: `services/imd_service.py` is fully implemented but operates in `AUTH_REQUIRED` state because `IMD_API_TOKEN` is not yet provisioned in `.env`.
- **Freshness & Fallback**: 15-minute TTL enforced; system gracefully falls back without fabricating weather data.

---

### SEISMIC GATE: PARTIAL
- **Operational Fallback Stream**: USGS FDSNws public GeoJSON API is active and continuously polling the Himalayan bounding box ($20.0^\circ\text{N} - 30.0^\circ\text{N}, 87.0^\circ\text{E} - 98.0^\circ\text{E}$), labeled `[LIVE / USGS]`.
- **Authoritative Stream Status**: `services/ncs_service.py` operates in `AUTH_REQUIRED` state pending Ministry of Earth Sciences credentials.
- **Freshness & Fallback**: 5-minute TTL enforced; graceful fallback to regional baseline ($M=0.0$) without fabricating tremors.

---

### EO GATE: PARTIAL
- **Catalogue Discovery**: Copernicus Dataspace Ecosystem (CDSE) STAC catalogue search is fully functional (`services/eo_catalog_service.py`).
- **Raw Scene Download**: OAuth2 client credentials (`COPERNICUS_CLIENT_ID`) pending; automated SLC scene downloads return `AUTH_REQUIRED`.
- **Operational Baseline**: Verified static 12-day InSAR LOS displacement baselines served transparently as `[CACHED]`.

---

### TERRAIN GATE: PASS
- **Digital Elevation Model**: Static 30m Copernicus GLO-30 DEM tiles cached and validated (`[CACHED]`).
- **Geotechnical Derivatives**: Horn's 3x3 convolution kernel calculates deterministic slope gradient, curvature, aspect, and elevation. Zero synthetic elevation profiles.

---

### PHYSICAL IoT GATE: FAIL (PHYSICAL_DEPLOYMENT_PENDING)
- **Hardware Bench Readiness**: Embedded firmware abstraction, 18-byte packed binary LoRa codec, ESP32 reference runtime, and hardware-in-the-loop serial stream readers fully verified (`HARDWARE_BENCH_READY`).
- **Slope Instrumentation Reality**: **Zero physical borehole transducers are installed or anchored on candidate hillslopes**. Status remains strictly:
  $$\mathbf{PHYSICAL\_DEPLOYMENT\_PENDING} \implies \text{Gate: } \mathbf{FAIL}$$
- No physical deployment is fabricated; simulator tests are never used to claim on-slope readiness.

---

### EDGE GATE: PARTIAL
- **Edge Software & Buffering**: Local circular FIFO buffer, store-and-forward replay, backhaul latency validator, and deduplication pipeline verified.
- **Physical Installation**: Outdoor IP67 LoRaWAN gateway mounting at Pakyong Ridge is pending physical sensor borehole deployment.

---

### ALERT GATE: PASS
- **Multi-Modal Corroboration**: Mandatory 2-of-3 independent evidence corroboration enforced across 6 modality groups. Single sensor spikes or model anomalies cannot trigger emergency warnings.
- **Public Safety Interlock**: Public emergency dispatch is locked by default (`PUBLIC_DISPATCH = DISABLED`).
- **Corridor Sirens**: Acoustic sirens operate in mandatory `DRY_RUN` mode. Physical actuation requires multi-threshold corroboration and authenticated HMAC digital authorization.
- **CAP Protocol**: Full OASIS Common Alerting Protocol (CAP v1.2) XML and JSON formulation with dynamic polygon geofencing.

---

### MOBILE GATE: PASS
- **Mobile Architecture**: Cross-platform Flutter client in `parvat_netra_mobile/` supporting 4 distinct user roles (`PUBLIC`, `FIELD_OPERATOR`, `AUTHORITY`, `ADMIN`).
- **Multilingual Support**: Verified localization across 6 Himalayan languages (English, Hindi, Nepali, Bengali, Assamese, Tibetan).
- **Offline Field Operations**: Local SQLite database v2 with store-and-forward field evidence synchronization verified (41/41 unit tests passed).
- *Note: Physical APK signing and mobile device management (MDM) distribution pending pilot kickoff.*

---

### OFFLINE GATE: PASS
- **Multi-Tier Resilience**: Edge circular FIFO buffers on IoT nodes, local SQLite store on mobile devices, offline Dijkstra/A* routing graph fallback, and persistent local observation database (`pahad_observations.db`).
- **Reconnection & Deduplication**: Store-and-forward synchronization verified with SHA-256 packet deduplication.

---

### SECURITY GATE: PASS
- **Access Control & Signatures**: Role-based access control (RBAC), HMAC-SHA256 signature verification for physical siren actuation and field evidence commissioning.
- **Secret Hygiene**: Zero plaintext secrets or credentials in codebase; verified via `mcp/scripts/validate_config.py`.
- **Audit Lineage**: Chained SHA-256 audit logging across all state machine transitions and operator decisions.

---

### HUMAN OVERSIGHT GATE: PASS
- **Core Doctrine Enforced**:
  $$\mathbf{AI\ recommendation \ne public\ emergency\ alert}$$
- **Authority Workflow**: 2-stage authority review queue with explicit approval PIN/token validation, timeout escalation to secondary approvers, and immediate manual emergency rollback.

---

### FAILURE GATE: PASS
- **Resilient Degradation**: Safe fallback behavior verified under weather loss (Open-Meteo downtime), seismic loss (USGS downtime), sensor dropout, edge gateway outage, database disconnections, and corrupted telemetry.
- **Honest Provenance**: Outages flag modalities as `[UNAVAILABLE]` or `[CACHED]` with confidence penalties; zero silent substitution into fake `[LIVE]` values.
- **Out-of-Distribution (OOD)**: Physically impossible telemetry values (e.g. slope $> 90^\circ$, rain $> 1000\text{ mm/h}$) trigger confidence penalties and suppress false alarms.

---

### MANDATORY BLOCKERS (P0)
1. **[BLK-P0-01] Physical On-Slope Instrumentation Deployment**:
   - **Evidence**: Transducers bench-tested; physical drilling and transducer anchoring not executed on NH-10 Pakyong Km 48.
   - **Owner**: Project Swastik BRO / SDRF Geotechnical Instrumentation Team.
   - **Required Action**: Drill boreholes, install vibrating-wire piezometers, biaxial inclinometers, and establish solar/battery power grid.
   - **Acceptance Condition**: Live continuous telemetry with certified hardware serial numbers streaming into `ObservationStore`.
2. **[BLK-P0-02] IMD Doppler Weather Radar Institutional Authentication**:
   - **Evidence**: `IMD_API_TOKEN` is unconfigured; operations rely on Open-Meteo REST API fallback.
   - **Owner**: Sikkim SDMA / IMD Meteorological Centre Gangtok.
   - **Required Action**: Finalize inter-agency data sharing agreement and configure production credentials.
   - **Acceptance Condition**: `IMD_CONNECTOR.get_status()` returns `status='READY'` and `auth='CONFIGURED'`.

---

### P1/P2 BLOCKERS
3. **[BLK-P1-01] Limited Historical Dataset Sample Size (P1)**:
   - **Evidence**: Model trained on $N=17$ events ($N=36$ baseline / $N=105$ temporal windows). Requires human supervisor oversight.
   - **Owner**: PAHAD AI ML Team.
   - **Action**: Ingest continuous IoT telemetry over multi-monsoon cycles to expand training dataset.
4. **[BLK-P1-02] MoES NCS Seismology Institutional Token (P1)**:
   - **Evidence**: Private NCS API unconfigured; USGS public API active as secondary fallback.
   - **Owner**: National Center for Seismology Liaison.
   - **Action**: Provision official MoES NCS seismic token.
5. **[BLK-P2-01] Copernicus CDSE Raw Scene Download Credentials (P2)**:
   - **Evidence**: STAC catalogue discovery active; automated SLC download pending `COPERNICUS_CLIENT_ID`.
   - **Owner**: Remote Sensing Team.
   - **Action**: Register Copernicus Dataspace OAuth2 application.

---

### TEST RESULTS
- **Phase 6F Pilot Test Battery**: **32 / 32 PASSED**
  - `test_pilot_readiness.py`: 10 passed
  - `test_pilot_modes.py`: 9 passed
  - `test_pilot_safety.py`: 5 passed
  - `test_pilot_rollback.py`: 3 passed
  - `test_pilot_failure.py`: 5 passed
- **Phase 6E Supervised Operations Battery**: **38 / 38 PASSED**
- **Phase 5/6 Live Inference & Data Consistency Battery**: **40 / 40 PASSED**
- **Model Registry & Integrity Battery**: **4 / 4 PASSED**
- **MQTT Edge Ingestion Battery**: **6 / 6 PASSED**
- **Total Operational Tests Verified**: **120+ tests passed with 100% pass rate**.

---

### FINAL VERDICT
$$\mathbf{READY\_FOR\_CONTROLLED\_SUPERVISED\_PILOT}$$

**Operational Constraints**:
1. Operation permitted strictly in `SHADOW` or `SUPERVISED_PILOT` mode.
2. `PUBLIC_DISPATCH = DISABLED` and acoustic sirens must remain in `DRY_RUN`.
3. Every alert recommendation requires manual authority sign-off (`AI recommendation != public alert`).
4. Autonomous public alerting is strictly prohibited until physical on-slope sensors (`BLK-P0-01`) and IMD credentials (`BLK-P0-02`) are commissioned.

---

### EXACT NEXT ACTION
**Initiate Supervised Field Shadow Trial on NH-10 Pakyong Corridor**:
1. Deploy `PILOT-NER-NH10-KM48` profile in `SUPERVISED_PILOT` mode.
2. Distribute Flutter field app to Project Swastik BRO and Sikkim SDRF patrol officers for offline evidence logging.
3. Conduct tabletop drill with Pakyong District Disaster Management Authority (DDMA) to validate 2-stage authority review workflows.
4. Formalize MoUs with IMD and Project Swastik BRO for on-slope borehole drilling and transducer installation.
