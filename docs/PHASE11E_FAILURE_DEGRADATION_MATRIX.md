# PARVAT NETRA / PAHAD AI — PHASE 11E
# SUBSYSTEM FAILURE & DEGRADATION MATRIX

## Document Information
- **Document Version**: 1.0.0
- **Standard**: Smart India Hackathon (SIH) 2026 Disaster-Intelligence Architecture
- **Scope**: Resilience, Fault-Tolerance, Circuit Breaking, and Graceful Degradation Protocols
- **Audit Date**: September 2026
- **Status**: AUDIT VERIFIED & VALIDATED

---

## 1. Executive Summary & Core Resilience Invariants

The PARVAT NETRA / PAHAD AI platform adheres to three non-negotiable architectural invariants during fault and outage conditions:

1. **Safety Fail-Closed Invariant**: Loss of upstream telemetry, network connectivity, or database access **must never** automatically cause a public warning to be broadcast or a physical siren to sound. Emergency sirens and public SMS remain locked in dry-run/disabled mode (`SIREN_DRY_RUN=1`, `ENABLE_PUBLIC_DISPATCH=0`).
2. **Deterministic Fallback Invariant**: When external upstream APIs (IMD, USGS, CDSE Copernicus, OmniRoute) fail or time out, the system must deterministically degrade to calibrated physics (Mohr-Coulomb FoS), cached telemetry, or local PostGIS geometric routing. The system **never crashes with an unhandled 500 exception**.
3. **Data Honesty & Provenance Invariant**: Every metric emitted during degraded states must clearly state its operational provenance (`[LIVE]`, `[CACHED]`, `[HISTORICAL]`, `[DETERMINISTIC]`, or `[SIMULATED]`). No simulated or cached value may ever claim to be `[LIVE]`.

---

## 2. Comprehensive Subsystem Degradation Matrix

| Subsystem | State | Trigger Condition | System Behavior & Fallback | Provenance Badge | Operational Impact & Mitigation | Recovery Action |
|:---|:---:|:---|:---|:---:|:---|:---|
| **IMD Weather Service** | `NORMAL` | IMD REST API responds within 3.5s with valid precipitation and forecast JSON. | Uses real-time 1h rainfall, 24h/72h cumulative precipitation, and IMD radar reflectivity. | `[LIVE]` | Full precision CRI and landslide probability forecasting. | Nominal continuous operation. |
| | `DEGRADED` | IMD REST API latency > 3.5s, HTTP 429/500, or network unreachable. | Falls back to local in-memory SQLite/Redis cache (TTL: 30 min). Uses previous reading + decay model. | `[CACHED]` | Warnings note weather freshness. CRI calculated with cached precipitation. | Auto-reconnects on next polling cycle with exponential backoff. |
| | `FAILED` | Cache expired (> 30 min) and IMD API unreachable. | Emits fallback climatological baseline for sector/district based on historical monsoon normals. | `[HISTORICAL]` | Flagged in EOC Command Brief as `WEATHER_STALE`. Sensitivity warnings raised. | Restores `[LIVE]` state immediately upon first valid HTTP 200 payload. |
| | `RECOVERY` | IMD API responds HTTP 200 with valid timestamped JSON. | Cache re-populated; provenance reverted to `[LIVE]`; alerts re-evaluated. | `[LIVE]` | Normal operations restored without manual intervention. | State transition logged in audit log. |
| **NCS / USGS Seismic Service** | `NORMAL` | National Centre for Seismology / USGS FDSN API responds within 5.0s with earthquake catalogue. | Calculates peak ground acceleration (PGA) and seismic destabilization factor for all 5 corridors. | `[LIVE]` | Real-time seismic trigger corroborated in multi-modal fusion. | Nominal continuous operation. |
| | `DEGRADED` | Primary NCS endpoint fails; USGS fallback succeeds within 8.0s. | Switches transparently to USGS Global FDSN endpoint for NER bounding box. | `[LIVE / FALLBACK]` | Latency increases by ~1-2s; seismic events captured accurately. | Primary NCS retried periodically every 5 minutes. |
| | `FAILED` | Both NCS and USGS endpoints time out or fail. | Assumes zero active shaking (PGA = 0.0); falls back to ambient seismic baseline. | `[DETERMINISTIC]` | Seismic score defaults to background noise (0/100). Geotech and weather components carry load. | Auto-reconnects on next scheduled check. |
| | `RECOVERY` | Valid earthquake GeoJSON received from either provider. | Computes epicentral distances and resets baseline PGA to real observations. | `[LIVE]` | Full seismic corroboration restored. | Alert state re-evaluated. |
| **Sentinel-1 / EO InSAR Service** | `NORMAL` | Copernicus CDSE OData API returns recent SAR orbits within 8.0s. | InSAR line-of-sight (LOS) deformation velocities and coherence maps ingested. | `[LIVE]` | Millimetric ground displacement tracked across slope sectors. | Nominal 12-day repeat cycle processing. |
| | `DEGRADED` | CDSE API down or no recent acquisition (< 12 days). | Uses most recent processed interferometric velocity field from local PostGIS store. | `[HISTORICAL]` | InSAR component relies on cumulative historical subsidence trends. | Periodically checks CDSE catalog every 6 hours. |
| | `FAILED` | No historical InSAR available for newly added sector. | InSAR weight proportionally redistributed among slope geometry and pore-water pressure. | `[DETERMINISTIC]` | InSAR contribution marked 0%; overall CRI remains mathematically bounded. | Ingests baseline DEM when catalog is available. |
| | `RECOVERY` | CDSE API available and new SLC product downloaded. | Local raster recomputed; full multi-modal InSAR fusion resumed. | `[LIVE]` | Provenance badge restored to `[LIVE]`. | State logged. |
| **Neon PostgreSQL / PostGIS DB** | `NORMAL` | PostgreSQL server responds to TCP connect and spatial queries within 2.0s. | Full spatial querying, incident logging, auth validation, and vector road graph lookups. | `[LIVE]` | Complete end-to-end relational and geospatial persistence. | Nominal continuous operation. |
| | `DEGRADED` | Network timeout (> 2.0s) or connection pool exhaustion. | `/api/health` reports status `503 DEGRADED`. Read-only corridor geometries served from local memory cache. | `[CACHED]` | Incident submissions queued in local memory/SQLite buffer; UI shows degraded banner. | Pool worker retries connection with backoff. |
| | `FAILED` | Database completely unreachable or credentials invalid. | In-memory corridor registry (`CORRIDOR_REGISTRY`) serves static boundaries and sensors. | `[DETERMINISTIC / IN-MEMORY]` | Real-time inference continues in-memory; historical persistence temporarily suspended. | Auto-reconnects when database connectivity returns. |
| | `RECOVERY` | PostgreSQL handshake succeeds and connection re-established. | `/api/health` status flips from `503 DEGRADED` to `200 UP`. Offline buffer drained. | `[LIVE]` | Normal operations resumed. No data loss for buffered edge events. | Reconnection event recorded. |
| **Edge IoT / LoRa Sensor Mesh** | `NORMAL` | Gateways receive LoRa packets with valid CRC-16, battery, and telemetry. | Real-time pore pressure, tilt, and soil moisture fed into Mohr-Coulomb FoS engine. | `[LIVE]` | Continuous slope stability mechanics calculation every 30-60s. | Nominal edge mesh operation. |
| | `DEGRADED` | Packet CRC-16 failure or missed heartbeats (> 120s) from specific sensor node. | Node marked `OFFLINE`; corrupted packet rejected immediately (`CRC-16 mismatch`). | `[DEGRADED]` | Neighboring nodes in cluster provide spatial interpolation; alert generated if key node drops. | Node sends valid packet; restored to `ONLINE`. |
| | `FAILED` | Entire gateway drops offline (power/backhaul failure). | System falls back to hydrological infiltration model driven by IMD weather data. | `[SIMULATED / DETERMINISTIC]` | Direct physical telemetry absent; conservative safety margin applied to FoS. | Gateway reconnects via cellular/satellite backhaul. |
| | `RECOVERY` | Gateway re-establishes MQTT/TCP connection and flushes local buffer. | Time-series backfilled into observation store; FoS engine uses live telemetry. | `[LIVE]` | Normal high-fidelity geotechnical calculation restored. | Recovery status broadcast to EOC dashboard. |
| **OmniRoute Local AI Gateway** | `NORMAL` | Local inference server on `http://localhost:20128/v1` responds within 2.5s. | LLM generates multi-lingual SitReps, tactical decision briefs, and translation broadcasts. | `[LIVE / AI-GENERATED]` | Rich situational context and multi-dialect voice synthesis enabled. | Nominal inference operation. |
| | `DEGRADED` | OmniRoute response time > 5.0s or queue depth > 10. | Requests shed to fast deterministic templates; non-critical translations deferred. | `[DETERMINISTIC]` | Concise template-based SitReps displayed in EOC; no latency penalty on telemetry. | OmniRoute queue drains; returns to full generative mode. |
| | `FAILED` | OmniRoute offline or process crashed (`ECONNREFUSED`). | Standard bilingual (English/Hindi) deterministic warning cards rendered immediately. | `[DETERMINISTIC]` | Zero impact on safety gates, FoS, or CRI calculation. EOC receives standard NDMA template. | Service supervisor restarts OmniRoute process. |
| | `RECOVERY` | OmniRoute endpoint responds HTTP 200 to health probe. | Full AI-generated SitRep and tactical briefing features automatically re-enabled. | `[LIVE / AI-GENERATED]` | EOC dashboard resumes dynamic multilingual synthesis. | State transition logged. |
| **Authority Review & Siren Gates** | `NORMAL` | Dual-officer cryptographic tokens (`AUTH-v1`) supplied for alert escalation. | Alert state transitions through `READY_FOR_AUTHORIZATION` -> `AUTHORIZED` -> `DISPATCHED`. | `[VERIFIED]` | Strict protocol followed; siren trigger verified. | Normal protocol. |
| | `DEGRADED` | Single officer token supplied or network latency between EOC and relay. | Alert remains held in `READY_FOR_AUTHORIZATION`; 2-of-3 quorum requirement enforced. | `[PENDING_SECOND_AUTH]` | Siren and public dispatch remain locked. No unilateral or automatic trigger allowed. | Second officer authenticates with valid credentials. |
| | `FAILED` | Relay hardware unreachable, power lost, or missing authentication token. | Physical relay driver remains fail-closed; siren emulator records `DRY_RUN_EMULATOR`. | `[FAIL-CLOSED / SAFE]` | Complete physical safety preserved; no false alarms emitted to public. | Manual physical override or technician verification required. |
| | `RECOVERY` | Hardware relay reports health check OK and token verified. | Armed state restored in `DRY_RUN` mode until explicit live authorization. | `[ARMED / DRY_RUN]` | Normal fail-safe operation restored. | System status verified by EOC Commander. |

---

## 3. Circuit Breaker Configuration & Policies

To prevent cascading failures, the platform implements localized circuit breakers on all external dependencies:

```
[External Request]
        │
        ▼
┌──────────────────┐       Timeout / 5xx       ┌──────────────────┐
│   CLOSED STATE   │ ────────────────────────> │    OPEN STATE    │
│  (Normal Calls)  │                           │  (Fast Fallback) │
└──────────────────┘                           └──────────────────┘
        ▲                                                │
        │               Successful Probe                 │  Wait Cooldown (30s)
        └────────────────────────────────────────────────┘
```

1. **Failure Threshold**: 3 consecutive failed requests or timeouts trip the circuit breaker into `OPEN` state.
2. **Cooldown Period**: 30 seconds before allowing a single canary probe (`HALF-OPEN`).
3. **Fail-Fast Response**: While `OPEN`, calls return immediately with the designated fallback payload and provenance badge in `< 1ms`.

---

## 4. Verification & Validation Records

- **Harness Execution**: `scratch/phase11e_reliability_audit.py`
- **Weather Fallback Test**: Verified clean transition to `[CACHED]` provenance without exception.
- **Seismic Fallback Test**: Verified operational status and recent event capture without crash.
- **Corrupt Packet Test**: Corrupted LoRa payload with invalid CRC-16 was rejected with `ValueError: CRC-16 mismatch` and did not taint the telemetry store.
- **DB Degraded Test**: When PostgreSQL was unreachable, `/api/health` cleanly emitted HTTP 503 with `"status": "DEGRADED"` and detailed error diagnostics without throwing an unhandled exception.
