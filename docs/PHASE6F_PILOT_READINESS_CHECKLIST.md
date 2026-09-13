# PARVAT NETRA / PAHAD AI — PHASE 6F
## Controlled Supervised Pilot Go/No-Go Readiness Checklist

**Document ID**: `PAHAD-CHK-6F-01`  
**Classification**: Operational Readiness Verification Protocol  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Corridor**: Primary: `CORR-NH10-SIKKIM-KM48` (Pakyong District, Sikkim)  
**Target Profile**: `PILOT-NER-NH10-KM48`  
**Operational Shift Lead**: ____________________  
**Date & Time (UTC)**: ____________________  
**Active Mode**: `SUPERVISED_PILOT` / `SHADOW`  

---

## 1. Pre-Flight Governance & Environment Checklist

| Item # | Verification Check | Command / Verification Method | Expected Result | Checked | Notes / Evidence |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **G-01** | Non-Negotiable Invariant: AI != Alert | Verify operational doctrine in `docs/PHASE6F_PILOT_OPERATIONS_SOP.md` | Human-in-the-loop authorization strictly required | [ ] | Mandatory SIH Invariant |
| **G-02** | Public Dispatch Disabled | Inspect `PILOT_MANAGER.get_profile().safety_policy.public_dispatch_enabled` | Must evaluate to `False` | [ ] | Zero automated public siren/SMS |
| **G-03** | Siren Mode Dry-Run | Inspect `PILOT_MANAGER.get_profile().safety_policy.siren_hardware_enabled` | Must evaluate to `False` (`DRY_RUN`) | [ ] | Prevents acoustic panic |
| **G-04** | Anti-Auto Escalation Lock | Verify `auto_escalate_mode` is disabled | Must evaluate to `False` | [ ] | Manual mode progression only |
| **G-05** | Credential Leakage Audit | Run `python mcp/scripts/validate_config.py` | Exit code 0, 0 plaintext secrets in code | [ ] | Security compliance |
| **G-06** | Spatial Database Connectivity | Query Neon PostgreSQL connection string | Active pool connected, PostGIS extensions active | [ ] | Spatial tables verified |

---

## 2. Telemetry Ingestion & Freshness Checklist

| Item # | Verification Check | Command / Verification Method | Expected Result | Checked | Notes / Evidence |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **T-01** | Weather Feed Stream | Check Open-Meteo REST API fallback | Returns HTTP 200, precipitation values valid | [ ] | `[LIVE / OPEN_METEO]` |
| **T-02** | Weather Provenance Integrity | Check `services/imd_service.py` status | Returns `AUTH_REQUIRED`; zero fake IMD data | [ ] | Honest provenance |
| **T-03** | Seismic Feed Stream | Check USGS FDSNws public endpoint | Returns GeoJSON events within NER bounding box | [ ] | `[LIVE / USGS]` |
| **T-04** | Seismic Provenance Integrity | Check `services/ncs_service.py` status | Returns `AUTH_REQUIRED`; zero fake NCS data | [ ] | Honest provenance |
| **T-05** | Digital Elevation Model (DEM) | Query slope/aspect at $27.33^\circ\text{N}, 88.61^\circ\text{E}$ | Slope $= 35^\circ$ to $42^\circ$, Aspect $\approx 180^\circ$ | [ ] | `[CACHED / GLO-30]` |
| **T-06** | InSAR Velocity Archive | Query Sentinel-1 InSAR baseline | Historical LOS velocity available | [ ] | `[CACHED]` |
| **T-07** | In-Situ IoT Grid Status | Check `engine/sensor_inventory.py` | Status: `PHYSICAL_DEPLOYMENT_PENDING` | [ ] | No phantom sensors claimed |
| **T-08** | Observation Store Persistence | Query `engine/observation_store.py` count | Database accessible, read/write thread-safe | [ ] | SQLite / PostGIS sync |

---

## 3. PAHAD AI Model & Inference Checklist

| Item # | Verification Check | Command / Verification Method | Expected Result | Checked | Notes / Evidence |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **M-01** | Model Registry Metadata | `curl -s http://localhost:8080/api/pahad/event-model/status` | `model_status: TRAINED_LIMITED_DATA`, $N=17$ events | [ ] | Canonical registry sync |
| **M-02** | Dataset SHA-256 Hash | Match `dataset_hash` against `real_train.csv` | Exactly matches `79ece554...` | [ ] | Tamper-evident data lineage |
| **M-03** | Model A vs Model B Decoupling | Run live inference test on Pakyong sector | FoS (Mohr-Coulomb) and $P(\text{event})$ distinct | [ ] | Physical vs Empirical separated |
| **M-04** | Multi-Horizon Forecasts | Request 6h, 12h, 24h, 48h probabilities | All 4 horizons returned within $[0.0, 1.0]$ | [ ] | Horizon models active |
| **M-05** | Probability Calibration | Inspect calibration metadata | Platt sigmoid calibration verified | [ ] | ECE & Brier score verified |
| **M-06** | Out-of-Distribution (OOD) Guard | Pass impossible slope ($110^\circ$) to inference | OOD flagged, confidence penalized, alert suppressed | [ ] | Safety interlock verified |
| **M-07** | Physics LSTM Integrity | Inspect `engine/pahad_lstm.py` | Identified strictly as `MATHEMATICAL_SURROGATE` | [ ] | Zero fabricated deep weights |

---

## 4. Alerting & Operational Workflow Checklist

| Item # | Verification Check | Command / Verification Method | Expected Result | Checked | Notes / Evidence |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **A-01** | 2-of-3 Corroboration Engine | Pass single-modality spike (e.g. rain only) | Alert level restricted to YELLOW (Advisory) | [ ] | Single trigger blocked |
| **A-02** | Authority Review Queue | Trigger multi-source anomaly | State enters `AUTHORITY_REVIEW`, queues task | [ ] | Authority oversight active |
| **A-03** | Authority Token Requirement | Attempt authorization with blank/invalid token | Request rejected with HTTP 403 / error | [ ] | PIN / HMAC enforced |
| **A-04** | Dynamic Geofencing | Inspect generated hazard polygon | Polygons wrap NH-10 KM48 with $500\text{m}$ buffer | [ ] | Road corridor delineated |
| **A-05** | CAP v1.2 Message Formulation | Inspect XML / JSON payload | Valid OASIS CAP v1.2 schema with polygon | [ ] | Standard compliance |
| **A-06** | Timeout Escalation Engine | Simulate unreviewed critical anomaly $> 15\text{m}$ | Escalates to secondary approver, logs event | [ ] | SLA fail-safe verified |
| **A-07** | Emergency Rollback Function | Execute `execute_emergency_rollback()` | Immediate de-escalation to `MONITORING`, audit logged | [ ] | Instant manual kill-switch |

---

## 5. Communications, Mobile & Incident Response Checklist

| Item # | Verification Check | Command / Verification Method | Expected Result | Checked | Notes / Evidence |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **C-01** | Mobile Offline Store | Inspect `parvat_netra_mobile` SQLite | Local caching active, 4 user roles supported | [ ] | Offline field resilience |
| **C-02** | Field Evidence Synchronization | Ingest mobile photo / GPS evidence packet | Photo hash, GPS coordinates stored in observation DB | [ ] | Field patrol feedback loop |
| **C-03** | Tactical Evacuation Routing | Query `SafeRoutesEngine` for NH-10 bypass | Dynamic route via NH-717A calculated without reload | [ ] | Evacuation corridor verified |
| **C-04** | Multilingual Alert Localization | Inspect alert output translations | Verified translations in Hindi, Nepali, English | [ ] | Regional language support |

---

## 6. Final Pilot Go / No-Go Decision Sign-Off

### Decision Criteria:
- **GO FOR SUPERVISED PILOT**: All items in Sections 1 through 5 marked `[X] Checked`. System operates in `SUPERVISED_PILOT` or `SHADOW` mode with human sign-off mandatory and public sirens disabled.
- **NO-GO**: Any item in Sections 1 through 5 unverified or failed.

### Sign-Off Signatures:

**1. Lead Technical Systems Engineer**:  
Name: ________________________________  
Signature: ____________________________  
Date/Time: ____________________________  

**2. Geotechnical & AI Metrology Lead**:  
Name: ________________________________  
Signature: ____________________________  
Date/Time: ____________________________  

**3. District Disaster Management Authority (DDMA) Duty Officer**:  
Name: ________________________________  
Signature: ____________________________  
Date/Time: ____________________________  
