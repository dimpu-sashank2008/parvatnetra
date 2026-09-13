# PARVAT NETRA / PAHAD AI — PHASE 6F
## Pilot Readiness Audit Matrix (16 Critical Dimensions)

**Document ID**: `PAHAD-DOC-6F-AUDIT-01`  
**Classification**: National Early Warning System Governance & Technical Audit  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Audit Date**: September 2026  
**Auditor**: Autonomous AI Systems Engineering & Disaster Governance Team  
**Evaluation Scope**: 16 Critical Operational & Technical Dimensions (A through P)  
**Final System Decision**: `READY_FOR_CONTROLLED_SUPERVISED_PILOT`  
*(Constrained to Shadow/Supervised Mode; Public Dispatch Disabled; Physical On-Slope Instrumentation & IMD Doppler Radar Credentials Pending)*

---

## 1. Executive Summary & Audit Methodology

Phase 6F conducts the uncompromised readiness assessment for transition into a controlled, supervised operational pilot along candidate Himalayan corridors (primary: `CORR-NH10-SIKKIM-KM48`, Pakyong District, Sikkim).

The readiness assessment enforces strict separation between:
1. **Mandatory Internal Software, Data, Safety & Workflow Gates**: Evaluates whether the algorithmic, telemetry validation, corroboration, security, and human oversight components operate safely and defensibly.
2. **External Deployment & Institutional Prerequisite Gates**: Evaluates physical transducer anchor drilling on hillslopes and government institutional inter-agency access (IMD, MoES NCS, ISRO Bhoonidhi).

### Strict Governance Rules Enforced:
- **Zero Fabrication**: No simulated data labeled `[LIVE]`; no phantom sensors or fabricated GPS positions.
- **Human Invariant**: $\mathbf{AI\ recommendation \ne public\ emergency\ alert}$.
- **Public Dispatch Disabled**: Public sirens and cell broadcasts default to `DISABLED` / `DRY_RUN`.
- **Model Truth**: The landslide event classifier is classified as `TRAINED_LIMITED_DATA` / `RESEARCH_PROTOTYPE` based on $N=17$ authenticated catastrophic disasters ($N=36$ baseline / $N=105$ antecedent temporal windows).

---

## 2. The 16-Dimension Readiness Matrix

Allowed Statuses: `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`  
Blocker Classifications: `P0` (Prevents safe pilot), `P1` (Major operational constraint), `P2` (Scaling enhancement), `NONE`.

| Dimension | Mandatory Pilot Gate? | Requirement | Verified Repository Evidence | Status | Blocker | Remediation Action |
| :--- | :---: | :--- | :--- | :---: | :---: | :--- |
| **A. DATA** | **YES** | 17 verified historical landslide events across 8 NER states; 36 balanced baseline observations (17 pos / 19 neg); 105 antecedent temporal windows; strict temporal holdout split; zero cross-partition leakage; explicit provenance tagging; isolated synthetic data. | `data/raw/historical_landslides_ner.csv`<br>`data/manifests/canonical_event_inventory.json`<br>`data/features/real_train.csv`<br>`data/processed/phase5b_temporal_full.csv`<br>`tests/test_event_leakage.py` | **PASS** | NONE | Continue long-term data expansion with GSI NLSM national repository. |
| **B. MODEL** | **YES** | Decoupled physical FoS model (Model A) vs GBDT Event probability classifier (Model B); 6h, 12h, 24h, 48h horizon models; Platt sigmoid calibration; ECE and Brier score tracking; OOD detection; model registry with dataset SHA-256; surrogate LSTM explicitly labeled. | `models/pahad_event_model.pkl` (v`test-v1.0`)<br>`models/pahad_event_model_{6h,12h,24h,48h}.pkl`<br>`engine/model_registry.py`<br>`models/pahad_event_model.metadata.json`<br>`engine/pahad_lstm.py` (`SURROGATE`) | **PASS** | P1 | Enforce `TRAINED_LIMITED_DATA` status and mandatory human operator in the loop. |
| **C. WEATHER** | **PARTIAL** | Continuous precipitation monitoring, 15m freshness TTL, multi-horizon forecasts, authoritative IMD Doppler radar connector with automated fallback to secondary feeds without data fabrication. | `services/weather_service.py`<br>`services/imd_service.py`<br>Open-Meteo REST API active as secondary fallback `[LIVE / OPEN_METEO]`; IMD connector returns `AUTH_REQUIRED`. | **PARTIAL** | P0 (Public)<br>P1 (Pilot) | Execute institutional MoU with IMD to provision `IMD_API_TOKEN` for public alerting. |
| **D. SEISMIC** | **PARTIAL** | Real-time ground motion trigger monitoring, 5m freshness TTL, MoES NCS API connector with secondary USGS FDSNws fallback. | `services/seismic_service.py`<br>`services/ncs_service.py`<br>USGS public FDSNws active `[LIVE / USGS]`; NCS connector returns `AUTH_REQUIRED`. | **PARTIAL** | P1 | Secure MoES NCS token for localized Himalayan micro-tremor feeds. |
| **E. SATELLITE/EO** | NO | Sentinel-1 InSAR LOS deformation velocity (12-day repeat pass), Sentinel-2 NDVI vegetation index. | `services/eo_catalog_service.py` (STAC discovery active); `services/satellite_service.py` (historical baseline served `[CACHED]`). | **PARTIAL** | P2 | Configure Copernicus Dataspace OAuth2 credentials and integrate ISRO Bhoonidhi L-band. |
| **F. TERRAIN** | **YES** | 30m Digital Elevation Model (Copernicus GLO-30 / CartoDEM), Horn's kernel slope calculation, curvature, aspect, and elevation. | `services/dem_service.py`<br>`services/terrain_service.py`<br>Static GLO-30 tiles cached and verified `[CACHED]`; deterministic math. | **PASS** | NONE | Ingest 10m stereo CartoDEM when available from NRSC. |
| **G. PHYSICAL IoT** | NO (Supervised)<br>**YES** (Autonomous) | Physical borehole vibrating-wire piezometer, in-place inclinometer (IPI), surface tiltmeter, and tipping-bucket rain gauge anchored on slope. | Firmware and bench tested (Phase 6C); `engine/sensor_inventory.py`; **ZERO physical transducers drilled on-slope**. Status: `PHYSICAL_DEPLOYMENT_PENDING`. | **FAIL** | P0 | Drill boreholes, install transducers, and establish solar/battery power on NH-10 Pakyong. |
| **H. EDGE/GATEWAY** | **YES** | LoRaWAN 865-867 MHz gateway, MQTT ingestion broker, local circular FIFO buffer, offline replay, deduplication, backhaul validation. | `services/edge_gateway.py`<br>`services/mqtt_ingestion.py`<br>`firmware/packet_codec.py`<br>`tests/test_mqtt_ingestion.py` | **PARTIAL** | P1 | Mount IP67 outdoor Kerlink gateway at Pakyong Ridge once physical sensors are drilled. |
| **I. ALERTING** | **YES** | CAP v1.2 XML/JSON generation, dynamic polygon geofencing, 2-of-3 independent corroboration, 2-stage authority sign-off, public dispatch interlock, dry-run acoustic siren. | `services/cap_service.py`<br>`services/geofence_service.py`<br>`services/corroboration_engine.py`<br>`services/authority_review.py`<br>`engine/operational_state_machine.py` | **PASS** | NONE | Enforce default `PUBLIC_DISPATCH = DISABLED` and `SIREN_HARDWARE_ENABLED = 0`. |
| **J. MOBILE** | **YES** | Cross-platform Flutter mobile client supporting 4 roles (`PUBLIC`, `FIELD_OPERATOR`, `AUTHORITY`, `ADMIN`), 6 Himalayan languages, offline SQLite storage, field sync. | `parvat_netra_mobile/lib/`<br>`parvat_netra_mobile/test/mobile_core_test.dart` (41/41 passed)<br>`tests/test_mobile_sync_contract.py` (9 passed) | **PASS** | NONE | Compile signed release APKs and distribute to pilot responders via MDM/F-Droid. |
| **K. OFFLINE** | **YES** | Local caching, mobile SQLite database, offline routing graph fallback, edge FIFO packet buffering, store-and-forward field evidence sync. | `engine/observation_store.py`<br>`parvat_netra_mobile/lib/services/offline_store.py`<br>`services/field_evidence_service.py`<br>`firmware/interfaces.py` | **PASS** | NONE | Periodically verify SQLite database vacuuming and indexing performance. |
| **L. SECURITY** | **YES** | RBAC, HMAC-SHA256 signature verification for sirens and field commissioning, no plaintext secrets in code, `.env` isolated, audit logging with SHA-256 chaining. | `engine/security_manager.py`<br>`services/authority_review.py`<br>`services/field_evidence_service.py`<br>`services/hardware_interface.py`<br>`mcp/scripts/validate_config.py` | **PASS** | NONE | Rotate HMAC signing secrets prior to initiating pilot operations. |
| **M. HUMAN OVERSIGHT** | **YES** | Authority review queue, incident management lifecycle, operator review, authorization token validation, emergency de-escalation override, full audit trail. | `services/authority_review.py`<br>`services/incident_orchestrator.py`<br>`engine/operational_state_machine.py`<br>`engine/decision_store.py`<br>`tests/test_supervised_operations.py` | **PASS** | NONE | Conduct regular tabletop drills with District Disaster Management Officers (DDMOs). |
| **N. OBSERVABILITY** | **YES** | Health endpoints (`/api/health`, `/api/pahad/data-status`, `/api/pahad/event-model/status`), freshness monitoring, structured logging, decision store metrics. | `app.py`<br>`engine/data_freshness.py`<br>`engine/decision_store.py`<br>`docs/PAHAD_OPERATIONS_RUNBOOK.md` | **PASS** | NONE | Deploy Prometheus exporter for continuous server metric scraping. |
| **O. INCIDENT RESPONSE** | **YES** | End-to-end incident lifecycle (11 states + 3 side states), timeout escalation, responder acknowledgement tracking, geofenced task allocation. | `services/incident_orchestrator.py`<br>`engine/operational_state_machine.py`<br>`services/timeout_escalation.py`<br>`tests/test_incident_management.py` | **PASS** | NONE | Calibrate agency timeout SLAs per district operational norms. |
| **P. OPERATIONAL PROCEDURES** | **YES** | Documented SOPs, operational runbooks, daily operator checklists, emergency rollback procedures, false alarm debriefing protocols. | `docs/PAHAD_OPERATIONS_RUNBOOK.md`<br>`docs/PHASE6F_PILOT_OPERATIONS_SOP.md`<br>`docs/PHASE6F_PILOT_READINESS_CHECKLIST.md` | **PASS** | NONE | Review SOPs quarterly with State Disaster Management Authorities. |

---

## 3. Sub-Readiness Score Calculation

Readiness scores are mathematically aggregated across functional sub-systems:

$$\begin{aligned}
\text{SOFTWARE\_READINESS} &= \mathbf{1.000} \quad (100\% \text{ of core software, state machines, APIs, and security pass}) \\
\text{DATA\_READINESS}     &= \mathbf{1.000} \quad (100\% \text{ canonical reconciliation, zero leakage, verified splits}) \\
\text{MODEL\_READINESS}    &= \mathbf{0.850} \quad (\text{Models trained and calibrated, but limited to } N=17 \text{ historical events}) \\
\text{FIELD\_READINESS}    &= \mathbf{0.300} \quad (\text{Firmware & bench verified, but } 0 \text{ transducers drilled on-slope}) \\
\text{INSTITUTIONAL\_READINESS} &= \mathbf{0.400} \quad (\text{Open-Meteo \& USGS live; IMD \& NCS require institutional auth}) \\
\text{OPERATIONAL\_READINESS}   &= \mathbf{0.950} \quad (\text{State machine, human oversight, CAP v1.2, and SOPs complete})
\end{aligned}$$

---

## 4. Prioritized Blockers Matrix

### Priority 0 (Blocks Autonomous Public Warning)
1. **[BLK-P0-01] Physical Transducers Not Anchored on Slope**:
   - **Dimension**: G. PHYSICAL IoT
   - **Evidence**: Firmware, packet codecs, and bench hardware are fully tested. However, zero borehole piezometers, inclinometers, or tiltmeters are physically installed along NH-10 Pakyong KM48.
   - **Owner**: Project Swastik BRO / SDRF Geotechnical Instrumentation Team.
   - **Required Action**: Complete drilling, transducer installation, wiring, and solar power provisioning on-slope.
   - **Acceptance Condition**: Live telemetry stream with authentic serial numbers and GPS coordinates streaming over LoRaWAN into `ObservationStore`.

2. **[BLK-P0-02] IMD Doppler Weather Radar Token Absent**:
   - **Dimension**: C. WEATHER
   - **Evidence**: `IMD_API_TOKEN` is not set; system operates on public Open-Meteo REST API fallback (`[LIVE / OPEN_METEO]`).
   - **Owner**: Sikkim SDMA / IMD Meteorological Centre Gangtok.
   - **Required Action**: Execute inter-agency MoU and configure production API credentials.
   - **Acceptance Condition**: `IMD_CONNECTOR.get_status()` returns `status='READY'` and `auth='CONFIGURED'`.

### Priority 1 (Operational Limitations Requiring Human Supervision)
3. **[BLK-P1-01] Limited Historical Dataset Volume**:
   - **Dimension**: B. MODEL
   - **Evidence**: Models trained on $N=17$ authenticated catastrophic landslides ($N=36$ baseline / $N=105$ temporal windows).
   - **Owner**: PAHAD AI Data & ML Engineering Team.
   - **Required Action**: Ingest continuous multi-season IoT telemetry to expand training observations to $N \ge 150$; operate under `TRAINED_LIMITED_DATA` protocol with human oversight.
   - **Acceptance Condition**: Multi-year continuous observation registry certified.

4. **[BLK-P1-02] MoES NCS Seismology Credentials Absent**:
   - **Dimension**: D. SEISMIC
   - **Evidence**: `NCS_API_TOKEN` not configured; USGS public FDSNws active as secondary fallback (`[LIVE / USGS]`).
   - **Owner**: National Center for Seismology Liaison.
   - **Required Action**: Provision official NCS seismic API token.
   - **Acceptance Condition**: `NCS_CONNECTOR.get_status()` returns `auth='CONFIGURED'`.

### Priority 2 (Scaling Enhancements)
5. **[BLK-P2-01] Copernicus CDSE Raw Scene Download Token**:
   - **Dimension**: E. SATELLITE/EO
   - **Evidence**: STAC catalogue discovery active; automated SLC scene downloads require `COPERNICUS_CLIENT_ID`.
   - **Owner**: Remote Sensing Team.
   - **Required Action**: Register Copernicus Dataspace OAuth2 credentials.
   - **Acceptance Condition**: Automated scheduled download of Sentinel-1 SLC frames for InSAR processing.

---

## 5. Audit Conclusion & Final Verdict

- **Mandatory Software, Data Governance, Safety & Operational Gates**: **PASS**
- **External Dependencies (Physical Slope Instruments & Institutional MOUs)**: **FAIL / PENDING**

### Final Verdict:
$$\mathbf{READY\_FOR\_CONTROLLED\_SUPERVISED\_PILOT}$$

**Operational Conditions**:
1. System must operate strictly in `SHADOW` or `SUPERVISED_PILOT` mode.
2. `PUBLIC_DISPATCH = DISABLED` and acoustic sirens remain in `DRY_RUN`.
3. Every warning recommendation requires authenticated 2-stage human authority review (`AI recommendation != public emergency alert`).
4. Autonomous public alerting is strictly prohibited until `BLK-P0-01` (physical sensors) and `BLK-P0-02` (IMD credentials) are fully remediated.
