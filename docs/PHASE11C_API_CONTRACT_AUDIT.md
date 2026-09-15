# PARVAT NETRA / PAHAD AI — PHASE 11C API CONTRACT AUDIT
**Forensic Audit of REST APIs, Authentication Gates, Schemas, Fallbacks & Consumers**

---

## 1. Executive Summary

This document establishes the verified forensic audit of the external and internal API contracts across the PARVAT NETRA / PAHAD AI platform. Every evaluated endpoint is mapped to its exact HTTP method, statutory authentication requirement, wire schemas, fail-closed fallback mechanisms, provenance attribution, and primary frontend consumer.

---

## 2. Comprehensive API Contract Audit Matrix

| Endpoint | Method | Auth Required | Request Schema | Response Schema | Fallback Behavior | Provenance Tag | Frontend Consumer |
|---|---|:---:|---|---|---|---|---|
| `/api/pahad/live-inference` | `GET`, `POST` | None (Public read) | `sector_id` (str), `latitude` (float), `longitude` (float), `horizon_hours` (int, opt), `features` (dict, opt) | `{ status: "SUCCESS", inference: { sector_id, event_probability, fos_physical, cri, risk_band, top_drivers, feature_provenance, data_quality_level, confidence } }` | Swith to regional training medians with explicit `[MISSING]` and `imputed=True` flags | `[LIVE]`, `[CACHED]`, `[MODELLED]`, `[MISSING]`, `[SIMULATED]` | `templates/index.html` (Prediction Card, Gauge Ring) |
| `/api/pahad/forecast` | `GET`, `POST` | None (Public read) | `sector_id` (str), `latitude` (float), `longitude` (float), `horizons` (str: "6,12,24,48") | `{ status: "SUCCESS", forecast: { sector_id, horizons: { "6h": { p_event }, "12h": {...}, "24h": {...}, "48h": {...} }, limitations: [...] } }` | Evaluates multi-horizon classifier or scaled probability map | `[MODELLED]`, `[HISTORICAL]` | `templates/index.html` (Horizon Matrix: h6, h12, h24, h48) |
| `/api/pahad/data-status` | `GET` | None (Public read) | Query: None | `{ status: "SUCCESS", data_streams: { weather: { status, provider }, seismic: {...}, terrain: {...}, iot: {...} }, demo_mode: bool, event_model: {...} }` | Reads active provider registry status and cache freshness | `[LIVE]`, `[CACHED]`, `[HISTORICAL]`, `[SIMULATED]` | System Health Modal, Data Quality Badge |
| `/api/pahad/highest-risk-corridor` | `GET` | None (Public read) | `force_refresh` (int/bool, opt), `state` (str, opt) | `{ status: "SUCCESS", highest_risk_corridor: { id, name, state, cri, risk_band, fos, event_probability, rainfall_24h, data_quality_level }, ranked_corridors: [...], count: int, tie_breaker: str }` | Serves cached top corridor (TTL: 60s) if within freshness; runs deterministic tie-breaker | `[LIVE / MODELLED]` | `templates/index.html:initHighestRiskCorridor()` |
| `/api/pahad/event-model/status` | `GET` | None (Public read) | Query: None | `{ status: "SUCCESS", model_status: "TRAINED_LIMITED_DATA", model_version: str, dataset_hash: str, real_event_rows: 17, training_samples: 16, validation_samples: 12, test_samples: 8, deep_lstm_status: "NOT_TRAINED" }` | Returns in-memory model registry metadata | `[HISTORICAL]` | Model Governance Card, Prototype Footer |
| `/api/pahad/event-model/data-quality` | `GET` | None (Public read) | Query: None | `{ status: "SUCCESS", total_records: int, real_events_count: 17, negative_controls_count: int, synthetic_demo_samples: 25, feature_completeness: float, date_range: {...} }` | Reads `data/manifests/` and dataset split statistics | `[HISTORICAL]` | Data Integrity Modal |
| `/api/siren/activate` | `POST` | **MANDATORY** (HMAC dual-key authority token) | `{ corridor_id: str, duration_seconds: int, token: str, reason: str }` | `{ status: "SUCCESS" / "UNAUTHORIZED", dry_run: true, physical_actuation: false, event_id: str, execution_log: str }` | **FAIL-CLOSED**: If token invalid or `SIREN_DRY_RUN=1`, physical GPIO is decoupled; audit log created | `[SIREN_DRY_RUN_HMAC]`, `[SIREN_DRY_RUN_EXECUTED]` | EOC Command Console (`btn-activate-siren`) |
| `/api/siren/status` | `GET` | None (Read-only) | Query: `corridor_id` (str, opt) | `{ status: "SUCCESS", siren_status: { armed: bool, dry_run: true, hardware_enabled: false, relay_state: "OPEN" } }` | Queries local `SirenController` instance | `[SIMULATED / DRY_RUN]` | EOC Siren Arming Indicator |
| `/api/siren/dry-run` | `POST` | Auth (Officer session) | `{ action: "TEST", duration_seconds: 5 }` | `{ status: "SUCCESS", mode: "DRY_RUN_EMULATION", acoustic_output_db: 0.0 }` | Executes dry-run test without driving relays | `[DRY_RUN_EMULATION]` | Bench Simulator / Test Rig |
| `/api/eoc/incidents` | `GET`, `POST` | Auth (EOC Officer) | GET: filter query; POST: `{ incident_type, sector_id, severity, coordinates, narrative }` | `{ status: "SUCCESS", incidents: [...], count: int }` | Queries PostGIS `incidents` table; falls back to SQLite buffer | `[LIVE]`, `[FIELD_VERIFIED]` | Incident Triage Board |
| `/api/authority/review` | `POST` | **MANDATORY** (Magistrate / Incident Commander) | `{ alert_id: str, decision: "APPROVE"|"REJECT", magistrate_id: str, pin: str, signature: str }` | `{ status: "SUCCESS", alert_id: str, state: "AUTHORIZED"|"REJECTED", timestamp_utc: str }` | **FAIL-CLOSED**: Rejection blocks downstream public CAP/SMS dispatch | `[AUTHORITY_SIGNED]` | Magistrate Sign-Off Modal |
| `/api/assistant/chat` | `POST` | None (CSRF / Session) | `{ message: str, context: { current_corridor: str, role: str } }` | `{ status: "SUCCESS", response: str, consultative_only: true, safety_interlock_engaged: bool }` | Intercepts actuation keywords; enforces consultative decision support | `[AI_CONSULTATIVE]` | Voice & Chat Assistant Modal |

---

## 3. Forensic Observations on Error Handling & Security

1. **Safety Enforcement**:
   - Actuation endpoints (`/api/siren/activate`, `/api/notifications/dispatch`) strictly reject unauthenticated calls with HTTP 401/403.
   - Even when authenticated in staging/evaluation, `SIREN_DRY_RUN=1` and `ENABLE_PUBLIC_DISPATCH=0` prevent hardware relay closure or civilian telecom broadcast.
2. **Missing Feature Graceful Degradation**:
   - `/api/pahad/live-inference` does not throw an HTTP 500 when weather, seismic, or IoT sensors are offline. It applies training medians ($N=16$), explicitly populates `imputed_features`, sets `data_quality_level = "DEGRADED DATA"`, and reduces `confidence` to `LOW_CONFIDENCE`.
3. **No Phantom Coordinates**:
   - Coordinates are validated to ensure they reside in WGS84 and the Himalayan collision zone ($20^\circ\text{N}\text{--}30^\circ\text{N}, 88^\circ\text{E}\text{--}98^\circ\text{E}$).
