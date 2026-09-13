# PARVAT NETRA / PAHAD AI — Phase 5 Authoritative Sub-Phase Audit

**Document ID**: PAHAD-AUDIT-PHASE5-AUTHORITATIVE  
**Classification**: National Disaster-Intelligence Engineering Audit  
**Authority**: PARVAT NETRA / PAHAD AI Architecture Review  
**Date**: September 2026  
**Status**: AUDIT COMPLETE  

---

## 1. AUTHORITATIVE ROADMAP SOURCE

To determine the authoritative roadmap of Phase 5 without relying on any single document, an exhaustive cross-referencing of all repository materials was conducted:
- **Architecture & Status Reports**: `docs/PHASE5_BASELINE_AUDIT.md`, `docs/PHASE5_DATA_STATUS.md`, `docs/PHASE5_LIVE_INFERENCE.md`, `docs/PAHAD_FULL_SYSTEM_STATUS.md`, `docs/PAHAD_PRODUCTION_ARCHITECTURE.md`.
- **Phase Reports & Manifests**: `docs/PHASE5B_MODEL_AUDIT.md`, `docs/PHASE5B_TEMPORAL_MODEL_REPORT.md`, `docs/PHASE5C_INTEGRATION_AUDIT.md`, `docs/PHASE5C_LIVE_INTEGRATION_REPORT.md`, `docs/PHASE5D_OFFLINE_AUDIT.md`, `docs/PHASE5D_OFFLINE_REPORT.md`, `docs/PHASE5D_SYNC_POLICY.md`, `docs/PHASE5D_PILOT_READINESS_REPORT.md`, `docs/PHASE5E_MOBILE_AUDIT.md`, `docs/PHASE5E_MOBILE_REPORT.md`, `docs/PHASE5E_DEVICE_VALIDATION_REPORT.md`.
- **Code Implementations**: `engine/pahad_live_inference.py`, `engine/pahad_prioritization.py`, `engine/model_registry.py`, `engine/data_freshness.py`, `engine/observation_store.py`, `engine/sector_snapshot.py`, `services/imd_service.py`, `services/ncs_service.py`, `services/sync_manager.py`, `services/offline_routing_service.py`, `parvat_netra_mobile/lib/`.
- **Test Suites**: `tests/test_pahad_phase5.py`, `tests/test_live_inference.py`, `tests/test_phase5b_*.py`, `tests/test_live_connectors.py`, `tests/test_freshness.py`, `tests/test_observation_store.py`, `tests/test_sector_snapshot.py`, `tests/test_sync_*.py`, `tests/test_offline_*.py`, `parvat_netra_mobile/test/mobile_core_test.dart`.

### Authoritative Progression Discovered:
The latest authoritative progression established across `docs/PHASE5C_LIVE_INTEGRATION_REPORT.md` (lines 121-123) and confirmed by implementation directories is:
- **Phase 5A**: Core Live Inference & Baseline Prioritization
- **Phase 5B**: Temporal Prediction & Multi-Horizon Early Warning
- **Phase 5C**: Real Data Connectors & Continuous Live Operations
- **Phase 5D**: Dual-Track: (1) Offline-First Architecture & Sync; (2) Data Reality, Label Decoupling & Pilot Readiness Gate
- **Phase 5E**: Flutter Mobile Field + Authority Application

No Phase 5F, 5G, or 5H documents, code, or tasks exist anywhere in the repository.

---

## 2. COMPLETE PHASE 5 SUB-PHASE LIST

1. **Phase 5A**: Core Live Inference & Baseline Architecture
2. **Phase 5B**: Real Temporal Prediction & Multi-Horizon Model Validation
3. **Phase 5C**: Real Data Connectors & Continuous Live Operations
4. **Phase 5D**: Offline-First Architecture, Resilient Sync & Pilot Readiness Gate
5. **Phase 5E**: Flutter Mobile Field + Authority Application
6. **Phase 5F**: NOT_APPLICABLE (0 repository references, never planned or scoped)
7. **Phase 5G**: NOT_APPLICABLE (0 repository references, never planned or scoped)
8. **Phase 5H**: NOT_APPLICABLE (0 repository references, never planned or scoped)

---

## 3. COMPLETION MATRIX

| Sub-Phase | Objective | Repository Evidence | Implementation | Tests | Status | Remaining Work |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Phase 5A** | Establish real-data live inference engine, dual-model separation (FoS vs Event), 8-state alert policy, and response prioritization across 8 NER states. | `docs/PHASE5_BASELINE_AUDIT.md`<br>`docs/PHASE5_LIVE_INFERENCE.md`<br>`docs/PAHAD_PRODUCTION_ARCHITECTURE.md` | `engine/pahad_live_inference.py`<br>`engine/pahad_prioritization.py`<br>`engine/pahad_alert_policy.py`<br>`services/device_gateway.py` | `tests/test_pahad_phase5.py` (8 passed)<br>`tests/test_live_inference.py` (40 passed)<br>`tests/test_failure_behavior.py` (27 passed) | **COMPLETE** | None |
| **Phase 5B** | Reconstruct dataset into antecedent windows (T-48h to T-6h, N=105), train multi-horizon classifiers (6h, 12h, 24h, 48h), prevent leakage, calibrate with Platt scaling, and produce OOD bounds. | `docs/PHASE5B_MODEL_AUDIT.md`<br>`docs/PHASE5B_TEMPORAL_MODEL_REPORT.md`<br>`models/phase5b_multi_horizon_metrics.json` | `engine/model_registry.py`<br>`scripts/train_phase5b_models.py`<br>`data/processed/phase5b_temporal_*.csv`<br>`models/pahad_ood_bounds.json` | `tests/test_phase5b_temporal_leakage.py` (passed)<br>`tests/test_phase5b_splits.py` (passed)<br>`tests/test_phase5b_dataset.py` (passed)<br>`tests/test_phase5b_ood.py` (passed)<br>`tests/test_phase5b_calibration.py` (passed) | **COMPLETE** | Sample volume limited (N=17 events); model status TRAINED_LIMITED_DATA |
| **Phase 5C** | Implement standalone real connectors (IMD, NCS, CDSE, USGS, Open-Meteo), indexed continuous `ObservationStore`, and configurable TTL `DataFreshnessEngine`. | `docs/PHASE5C_INTEGRATION_AUDIT.md`<br>`docs/PHASE5C_LIVE_INTEGRATION_REPORT.md`<br>`docs/MCP_INTEGRATION_STATUS.md` | `services/imd_service.py`<br>`services/ncs_service.py`<br>`services/eo_catalog_service.py`<br>`engine/data_freshness.py`<br>`engine/observation_store.py`<br>`engine/sector_snapshot.py` | `tests/test_live_connectors.py` (8 passed)<br>`tests/test_freshness.py` (10 passed)<br>`tests/test_observation_store.py` (10 passed)<br>`tests/test_sector_snapshot.py` (8 passed)<br>`tests/test_mcp_integration.py` (8 passed) | **COMPLETE** | Institutional tokens (`IMD_API_TOKEN`, `NCS_API_TOKEN`) absent; system operational via public fallbacks |
| **Phase 5D (Sync)** | Offline-first PWA web shell, pre-bundled NER vector GeoJSON package, mobile SQLite v2 caching, offline hazard routing, and REST push/pull sync endpoints. | `docs/PHASE5D_OFFLINE_AUDIT.md`<br>`docs/PHASE5D_OFFLINE_REPORT.md`<br>`docs/PHASE5D_SYNC_POLICY.md` | `static/sw.js`<br>`static/data/offline_core_package.json`<br>`services/sync_manager.py`<br>`services/offline_routing_service.py`<br>`static/js/offline_routing.js` | `tests/test_sync_api.py` (8 passed)<br>`tests/test_sync_manager.py` (8 passed)<br>`tests/test_offline_routing.py` (8 passed)<br>`tests/test_offline_resilience.py` (passed)<br>`tests/test_offline_web.py` (passed) | **COMPLETE** | None |
| **Phase 5D (Readiness)** | Rigorous data reality audit of 17 canonical events, decoupling labels from FoS, leakage audit, and formal institutional pilot readiness gate verdict. | `docs/PHASE5D_PILOT_READINESS_REPORT.md`<br>`canonical_event_inventory.json` | `data/raw/historical_landslides_ner.csv`<br>`engine/event_labeling.py`<br>`engine/event_features.py` | 17 verified events across 8 NER states; Zero leakage violations; Verdict: NOT_READY_FOR_PILOT | **COMPLETE** | System not ready for autonomous pilot until institutional MOU and in-situ sensors deployed |
| **Phase 5E** | Flutter Mobile Field + Authority Application: Role-aware operations (`PUBLIC`, `FIELD_OPERATOR`, `AUTHORITY`), 6 Himalayan languages, offline SQLite v2, geofenced alerts, incident reporting & verification, and Puro build configuration. | `docs/PHASE5E_MOBILE_AUDIT.md`<br>`docs/PHASE5E_MOBILE_REPORT.md`<br>`docs/PHASE5E_DEVICE_VALIDATION_REPORT.md` | `parvat_netra_mobile/lib/`<br>`parvat_netra_mobile/lib/services/`<br>`parvat_netra_mobile/lib/screens/`<br>`parvat_netra_mobile/android/` | `parvat_netra_mobile/test/mobile_core_test.dart` (41/41 passed via Puro Flutter)<br>`tests/test_mobile_sync_contract.py` (9 passed) | **COMPLETE** | Android SDK absent on host; validated via headless Dart and Python harnesses |
| **Phase 5F** | Hypothesized sub-phase. | Scanned entire repository; 0 matches. | None | None | **NOT_APPLICABLE** | Never defined |
| **Phase 5G** | Hypothesized sub-phase. | Scanned entire repository; 0 matches. | None | None | **NOT_APPLICABLE** | Never defined |
| **Phase 5H** | Hypothesized sub-phase. | Scanned entire repository; 0 matches. | None | None | **NOT_APPLICABLE** | Never defined |

---

## 4. 5A AUDIT

- **Original Objective**: Live multi-modal prediction pipeline, infinite slope Mohr-Coulomb Factor of Safety ($FoS$) model, empirical event probability classifier, emergency response prioritization, and 2-of-3 independent corroboration safety rule.
- **Files Implemented**:
  - `engine/pahad_live_inference.py`: Live inference orchestrator.
  - `engine/pahad_prioritization.py`: Emergency response prioritization formula ranking sectors by `(Pop * CRI * Weight) / ETA`.
  - `engine/pahad_alert_policy.py`: 8-state alert lifecycle with 2-of-3 corroboration gate.
  - `services/device_gateway.py`: IoT edge gateway for LoRaWAN/MQTT sensor packets.
- **APIs**:
  - `POST /api/pahad/live-inference`
  - `GET /api/pahad/response-prioritization`
  - `GET /api/pahad/regional-overview`
- **Tests**:
  - `tests/test_pahad_phase5.py` (8 passed in 61s)
  - `tests/test_live_inference.py` (40 passed)
  - `tests/test_failure_behavior.py` (27 passed)
- **Status**: COMPLETE.

---

## 5. 5B AUDIT

- **Original Objective**: Move from static single-row disaster observations to antecedent observation windows ($T-48	ext{h}, T-36	ext{h}, T-24	ext{h}, T-12	ext{h}, T-6	ext{h}$, $N=105$), decouple label assignment from FoS, remove circular CRI feature, train multi-horizon classifiers (6h, 12h, 24h, 48h) with Platt calibration and Out-of-Distribution (OOD) bounds.
- **Files Implemented**:
  - `engine/model_registry.py`: Centralized ModelRegistry with versioning and cryptographic SHA-256 hashes.
  - `scripts/train_phase5b_models.py`: Multi-horizon training pipeline with Platt scaling.
  - `data/processed/phase5b_temporal_full.csv` ($N=105$), `phase5b_temporal_train.csv` ($N=48$), `phase5b_temporal_val.csv` ($N=33$), `phase5b_temporal_test.csv` ($N=24$).
  - `models/pahad_ood_bounds.json` and `models/phase5b_multi_horizon_metrics.json`.
- **Tests**:
  - `tests/test_phase5b_temporal_leakage.py` (passed: 0 future violations, 0 window violations, 0 partition bleed).
  - `tests/test_phase5b_splits.py`, `tests/test_phase5b_dataset.py`, `tests/test_phase5b_ood.py`, `tests/test_phase5b_calibration.py` (passed).
- **Status**: COMPLETE. Limitation: Model status remains honestly classified as `TRAINED_LIMITED_DATA`.

---

## 6. 5C AUDIT

- **Original Objective**: Real data integration with zero synthetic fabrication in production mode. Return `AUTH_REQUIRED` or `UNAVAILABLE` when institutional credentials are missing. Connect public Open-Meteo and USGS endpoints. Continuous SQLite observation store, configurable freshness TTL engine, deterministic sector snapshots.
- **Files Implemented**:
  - `services/imd_service.py`: Standalone IMD connector returning structured `IMDObservation` objects.
  - `services/ncs_service.py`: Standalone NCS connector with USGS FDSNws GeoJSON NER bounding box fallback.
  - `services/eo_catalog_service.py`: CDSE Copernicus OData catalog search connector.
  - `engine/data_freshness.py`: `DataFreshnessEngine` with configurable TTLs (IMD 15m, NCS 5m, IoT 2m, satellite 1d, terrain 30d).
  - `engine/observation_store.py`: `ObservationStore` with SQLite database (`pahad_observations.db`) and composite indices.
  - `engine/sector_snapshot.py`: `SectorSnapshotBuilder` assembling 26 features, freshness status, and provenance summary.
- **APIs**:
  - `GET /api/pahad/data-status`
  - `GET /api/pahad/observations/latest`
  - `GET /api/pahad/observations/history`
  - `GET /api/system/provenance`
- **Tests**:
  - `tests/test_live_connectors.py` (8 passed)
  - `tests/test_freshness.py` (10 passed)
  - `tests/test_observation_store.py` (10 passed)
  - `tests/test_sector_snapshot.py` (8 passed)
  - `tests/test_mcp_integration.py` (8 passed)
  - Total: 44/44 passed (100% pass rate).
- **Actual Status**: Operational verdict is `PARTIALLY_OPERATIONAL` (Public feeds active, institutional feeds `AUTH_REQUIRED`).

---

## 7. 5D AUDIT

- **Original Objective**: Two tracks documented:
  1. Offline Maps & Resilient Sync: Service Worker v5.4.0, vector GIS package, mobile SQLite database, offline routing, push/pull sync endpoints.
  2. Data Reality, Label Audit & Pilot Readiness Gate: Canonical event inventory ($N=17$), FoS label decoupling, leakage audit, dataset lineage, and pilot readiness gate assessment.
- **Files Implemented**:
  - `static/sw.js`: PWA service worker with Cache-First app shell and Stale-While-Revalidate vector packages.
  - `static/data/offline_core_package.json`: 66 GeoJSON vector features covering 8 NER states.
  - `services/sync_manager.py`: Bidirectional sync manager handling `/api/sync/push` and `/api/sync/pull`.
  - `services/offline_routing_service.py` & `static/js/offline_routing.js`: Dual-tier offline routing with corridor blockage detection and `[OFFLINE ROUTE]` badging.
  - `canonical_event_inventory.json`: 17 documented disaster events across all 8 NER states with institutional provenance.
  - `engine/event_labeling.py` & `engine/event_features.py`: Decoupled label generation without FoS circular bias.
- **APIs**:
  - `POST /api/sync/push`, `GET /api/sync/pull`, `GET /api/sync/status`, `POST /api/sync/field-reports`, `GET /api/sync/offline-package`.
- **Tests**:
  - `tests/test_sync_api.py` (8 passed), `tests/test_sync_manager.py` (8 passed), `tests/test_offline_routing.py` (8 passed), `tests/test_offline_resilience.py` (passed), `tests/test_offline_web.py` (passed). Total: 51 passed.
- **Readiness Gate Verdict**:
  - Evaluated against 3 institutional gates:
    - Institutional Telemetry Gate: **FAILED** (`IMD_API_TOKEN`, `NCS_API_TOKEN` absent).
    - Sensor Grid Gate: **FAILED** (In-situ piezometers/inclinometers absent on candidate corridors).
    - Training Volume Gate: **LIMITED** ($N=17$ events, status `TRAINED_LIMITED_DATA`).
  - Final Verdict: `NOT_READY_FOR_PILOT`.

---

## 8. ALL OTHER 5.x AUDITS (PHASE 5E)

- **Phase 5E**: Flutter Mobile Field + Authority Application (`parvat_netra_mobile/`):
  - **Objective**: Build an operational field application for first responders, citizens, and command authorities. Must support online, offline, and reconnect/sync workflows without creating a second AI engine.
  - **Implementation**:
    - 10 Data Models: `auth_model.dart`, `forecast_model.dart`, `data_status_model.dart`, `sync_models.dart`, `route_model.dart`, `sector_snapshot_model.dart`, `field_report.dart`, `alert_model.dart`, `pahad_risk_snapshot.dart`, `shelter_model.dart`.
    - 7 Core Services: `api_client.dart`, `auth_service.dart`, `database_helper.dart` (SQLite v2), `sync_service.dart` (exponential backoff), `location_service.dart`, `localization_service.dart` (6 languages: en, hi, ne, bh, lp, as), `push_notification_service.dart`.
    - 12 UI Screens: `mobile_home_screen.dart`, `forecast_screen.dart`, `alerts_screen.dart`, `safety_routing_screen.dart`, `incident_reporting_screen.dart`, `incident_verification_screen.dart`, `data_status_screen.dart`, `login_screen.dart`, `citizen_mode_screen.dart`, `authority_mode_screen.dart`, `field_operations_screen.dart`, `pahad_explanation_dialog.dart`.
    - Android Build Configuration: Gradle 8.5, AGP 8.2.0, Kotlin 1.9.22, compileSdk 34, AndroidManifest with permissions.
  - **Tests**:
    - `parvat_netra_mobile/test/mobile_core_test.dart` (41/41 unit tests pass via Puro Flutter).
    - `tests/test_mobile_sync_contract.py` (9 passed).
    - `tests/test_mobile_field_api.py` (passed).
  - **Status**: COMPLETE.

---

## 9. DOCUMENTATION/CODE DISCREPANCIES

1. **Dual Track Labeling of Phase 5D**:
   - Both the Offline Architecture (`docs/PHASE5D_OFFLINE_REPORT.md`) and Data Reality / Pilot Readiness Gate (`docs/PHASE5D_PILOT_READINESS_REPORT.md`) share the "Phase 5D" identifier. They represent two complementary workstreams executed under the Phase 5D milestone.
2. **Model Metadata Synchronization**:
   - Running the legacy single-horizon script (`train_event_model.py`) updated `models/pahad_event_model.metadata.json` with a single 24h horizon schema, whereas Phase 5B generated multi-horizon artifacts (`models/phase5b_multi_horizon_metrics.json` and `models/pahad_ood_bounds.json`). Both models exist and operate independently.
3. **Mobile Device Execution Environment**:
   - `docs/PHASE5E_DEVICE_VALIDATION_REPORT.md` documents that host machine environment lacks an Android SDK installation on PATH; mobile logic was verified via headless Dart 3.13.2 and Python Flask integration tests.

---

## 10. REMAINING PHASE 5 WORK

- **Engineering Tasks**: Zero remaining. All sub-phases (5A, 5B, 5C, 5D, 5E) are designed, coded, tested, and audited.
- **Model Status**: The model status is permanently fixed as `TRAINED_LIMITED_DATA` due to $N=17$ historical landslide events. No further synthetic data generation is permitted.

---

## 11. BLOCKERS

- **Software / Repository Blockers**: None. Over 222 tests pass with zero failures.
- **External Institutional Blockers** (as established in Phase 5D):
  1. Formal Data Sharing Agreement / MOU needed with IMD and MoES NCS to provision live institutional Doppler Radar and seismic data feeds (`IMD_API_TOKEN`, `NCS_API_TOKEN`).
  2. Physical hardware deployment of LoRaWAN-connected in-situ vibrating-wire piezometers and borehole inclinometers along candidate test corridors (e.g. NH-10 Pakyong Km 48).

---

## 12. NEXT PHASE 5 SUB-PHASE

**NONE.**  
Every planned 5.x sub-phase has been completed. The next logical development milestone is **Phase 6: Mountain Corridor Hardware Deployment, In-Situ Sensor Pilot, and Institutional MOU Integration**.

---

## 13. ACCEPTANCE CRITERIA FOR THAT SUB-PHASE (PHASE 6 TRANSITION)

Original acceptance criteria for moving beyond Phase 5 into Phase 6:
1. [x] Physical FoS and empirical event probability strictly separated in architecture and APIs.
2. [x] Zero synthetic samples included in operational training datasets.
3. [x] Strict temporal holdout partitioning with zero lookahead or window leakage.
4. [x] Public live connectors (Open-Meteo, USGS) functional with graceful `AUTH_REQUIRED` handling for institutional feeds.
5. [x] SQLite `ObservationStore` and configurable TTL `DataFreshnessEngine` active.
6. [x] Offline-first vector GIS package and PWA/mobile SQLite caches operational.
7. [x] Bidirectional sync engine with exponential backoff and deterministic deduplication active.
8. [x] Mobile field application implemented across 6 languages with 41/41 unit tests passing.
9. [x] Pilot readiness assessment completed with objective gate verdict: `NOT_READY_FOR_PILOT`.
