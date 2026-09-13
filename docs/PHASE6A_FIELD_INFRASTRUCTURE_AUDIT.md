# PARVAT NETRA / PAHAD AI — Phase 6A Field Infrastructure Audit

**Document ID**: `PAHAD-AUDIT-PHASE6A-01`  
**Classification**: Geotechnical Telemetry & Field Deployment Infrastructure Audit  
**Phase**: Phase 6A — Field Deployment Infrastructure  
**Date**: September 2026  
**Status**: AUDIT COMPLETE — BASELINE ESTABLISHED  

---

## 1. Executive Summary

Phase 6A transitions PARVAT NETRA / PAHAD AI from `PARTIALLY_OPERATIONAL` software toward **field-deployable hardware infrastructure**. 

The purpose of this audit is to rigorously inspect all existing IoT, edge gateway, telemetry ingestion, device management, and calibration components across the repository, identify architectural and security gaps, and establish the technical roadmap for real field deployment without fabricating live hardware connectivity.

---

## 2. Comprehensive Component Audit Matrix

| COMPONENT | EXISTS | WORKING | REAL | SIMULATED | GAP | ACTION |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **`services/device_gateway.py`** | YES | PARTIAL | NO | YES | Automatically marks unverified packets as `[LIVE]`; seeds 3 fake demo devices (`PZ-NH10-KM48-01`, `INC-NH10-KM48-01`, `RG-PAKYONG-01`) when empty; lacks sequence tracking, deduplication, timestamp drift validation, and calibration verification. | Refactor to reject unauthenticated/unregistered devices; enforce strict `SIMULATED` vs `LIVE` provenance; delegate device tracking to `sensor_registry.py`. |
| **`backend/telemetry_streamer.py`** | YES | YES | NO | YES | Standalone infiltration simulation script coupling rainfall to synthetic VWC and tilt in PostgreSQL. Properly marked `[SIMULATED]`. | Maintain as isolated offline test harness under `PAHAD_EDGE_SIMULATION=1`; isolate from operational inference. |
| **`backend/edge/` (Phase 3.4 Edge Core)** | YES | YES | PARTIAL | YES | Provides binary packet decoder (`packet.py`), SQLite buffer (`edge_store.py`), LoRa mesh (`mesh.py`), siren relay (`siren_controller.py`), and routes (`routes.py`). Uses proprietary 24-byte binary format rather than canonical JSON/MQTT contracts; not integrated with `observation_store.py` or PAHAD live inference. | Standardize packet schema; unify edge store with canonical offline buffer contract; bridge edge alerts to `edge_alert_policy.py`. |
| **`engine/observation_store.py`** | YES | YES | YES | NO | SQLite-backed store (`pahad_observations.db`) with composite indices on `(sector_id, timestamp)`. Stores numerical observations but lacks relational device identity, calibration metadata, or gateway routing. | Integrate as backend store for verified physical sensor observations; maintain provenance tags. |
| **`engine/data_freshness.py`** | YES | YES | YES | NO | TTL tracking with 120s limit for IoT, 75% aging ratio, and confidence penalties. Fully operational. | Connect to incoming device telemetry timestamps to calculate real-time freshness. |
| **`engine/pahad_live_inference.py`** | YES | YES | PARTIAL | YES | Ingests IoT via `DeviceGateway.list_devices()`; accepts seeded demo devices and marks them `LIVE`; falls back to training-set medians ($u=26.0\text{ kPa}, \theta=3.5^\circ$). | Replace seeded fallback with explicit `sensor_registry.py` queries; if no active physical hardware is deployed, mark feature `[MISSING]` rather than fabricated live. |
| **`engine/pahad_models.py`** | YES | YES | YES | NO | Geotechnical Mohr-Coulomb equation for physical FoS calculation and 2-of-3 false-alarm suppression rule. Operational. | Ensure pore pressure ($u$) input explicitly derives from authenticated piezometers or transparent physics models (`[MODELLED]`). |
| **`app.py` (REST Endpoints)** | YES | PARTIAL | PARTIAL | NO | Contains `/api/edge/*` endpoints from Phase 3.4 blueprint, but lacks canonical `/api/iot/*` endpoints (`/api/iot/devices`, `/api/iot/gateways`, `/api/iot/health`, `/api/iot/telemetry`, `/api/iot/commission`, `/api/iot/calibration`). | Implement and register canonical `/api/iot/*` REST API blueprint with role-based authentication and rate limiting. |
| **`services/mqtt_ingestion.py`** | NO | NO | NO | NO | Missing dedicated MQTT client service to subscribe to field broker topics (`pahad/{state}/{sector}/{device}/telemetry`) with reconnect and persistence. | **[NEW]** Implement `services/mqtt_ingestion.py` with configurable broker URL, TLS, auth, and validation. |
| **`services/edge_gateway.py`** | NO | NO | NO | NO | Missing canonical edge concentrator service managing LoRaWAN packets, local buffering, and forward-syncing. | **[NEW]** Implement `services/edge_gateway.py` with persistent local SQLite buffer, exponential backoff, and deduplication. |
| **`engine/sensor_registry.py`** | NO | NO | NO | NO | Missing centralized physical device and sensor lifecycle registry tracking installation, firmware, battery, signal, and operational status. | **[NEW]** Implement `engine/sensor_registry.py` with 8 supported sensor types and 7 lifecycle states. |
| **`engine/sensor_calibration.py`** | NO | NO | NO | NO | Missing sensor calibration engine tracking zero offsets, scale factors, calibration expiry, and rejecting uncalibrated telemetry. | **[NEW]** Implement `engine/sensor_calibration.py` with calibration validation status and correction formulas. |
| **`engine/edge_alert_policy.py`** | NO | NO | NO | NO | Missing local edge safety policy evaluating local sensor thresholds for autonomous on-site siren arming independent of central cloud. | **[NEW]** Implement `engine/edge_alert_policy.py` with deterministic corridor hazard thresholds. |
| **`services/siren_controller.py`** | PARTIAL | PARTIAL | NO | YES | `backend/edge/siren_controller.py` exists as a local prototype, but lacks hardware abstraction for relays, authorized digital signature checks, and web guardrails. | **[NEW/REFACTOR]** Implement `services/siren_controller.py` enforcing `allowPhysicalSirenTest=false` default and authorization tokens. |
| **Mobile Integration (`parvat_netra_mobile`)** | YES | PARTIAL | PARTIAL | YES | `local_alert_service.dart` and `edge_test_screen.dart` exist, but rely on in-memory mock states; `api_client.dart` lacks `/api/iot/*` endpoints. | Add typed models for devices/gateways/calibration and connect to backend REST APIs. |
| **PostgreSQL Database Schema** | YES | PARTIAL | YES | NO | Neon PostgreSQL has `iot_sensors` and `sensor_telemetry` tables (from `backend/migrate_phase9.py`), but lacks `gateways`, `device_health`, `sensor_calibrations`, `edge_alerts`, and `telemetry_ingestion_log`. | Create Phase 6A migration script (`backend/migrate_phase6a.py`) adding missing tables, indices, and foreign keys. |
| **IoT / Edge Test Suites** | YES | PARTIAL | YES | NO | `tests/test_edge_*.py` covers Phase 3.4 edge prototype (8 files), but zero tests exist for MQTT ingestion, sensor registry, calibration, commissioning, or device health. | **[NEW]** Create comprehensive test suite covering all 10 required Phase 6A contracts. |
| **MCP Integration** | YES | PARTIAL | YES | NO | Neon MCP returns session 403 (unauthenticated); other MCP tools are developer tools (chrome-devtools, github, firebase). | Use direct `psycopg2` database connections via project configuration (`DATABASE_URL`). |

---

## 3. Critical Architectural Invariants for Phase 6A

1. **Zero Fake Hardware Claims**:
   - If no physical sensor hardware is physically connected, the device status must report `NOT_DEPLOYED` or `SIMULATED`.
   - Never mark simulated telemetry as `[LIVE]`.
   - All synthetic or simulated packets must carry `provenance = "[SIMULATED]"`.

2. **Decoupled Local Safety from Public Authority Broadcast**:
   - The local Edge Siren Controller may sound immediate on-site acoustic horns at mountain chokepoints (e.g. NH-10 Km 48) when local pore-pressure or tilt velocity thresholds are breached.
   - Local siren activation is strictly distinct from regional Common Alerting Protocol (CAP v1.2) public warning broadcasts, which mandate 2-of-3 multi-modal corroboration and District Magistrate / EOC officer digital authorization.

3. **Packet Integrity & Deduplication**:
   - Every incoming telemetry frame must be verified for sequence monotonicity, timestamp validity ($T_{packet} \le T_{server} + 30\text{s}$), spatial bounding within the NER polygon, and payload range sanity.
   - Replayed, duplicate, or out-of-order packets must be dropped or logged without corrupting the time-series store.

4. **Offline Edge Buffering with Idempotent Replay**:
   - Edge concentrators must buffer observations locally in SQLite during fiber/cellular backhaul severed conditions.
   - Upon backhaul restoration, buffered packets must be replayed in strict chronological order with idempotent server deduplication (`packet_id` / `device_id` + `sequence_number` + `timestamp`).

5. **Calibration Guardrail**:
   - Telemetry from sensors with `CALIBRATION_DUE` or `INVALID_CALIBRATION` must be flagged as `DEGRADED` or `INVALID` and penalized in confidence scoring before entering PAHAD AI.
