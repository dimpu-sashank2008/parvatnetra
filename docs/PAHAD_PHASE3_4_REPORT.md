# PARVAT NETRA / PAHAD AI — PHASE 3.4 TECHNICAL REPORT
## Local Edge Network + LoRa Mesh + BLE + Siren + Sensor Gateway

**Document Reference**: `PAHAD_PHASE3_4_REPORT.md`  
**Problem Statement ID**: SIH 26001 (Smart India Hackathon)  
**Date of Verification**: September 2026  
**System Status**: `OPERATIONAL / READY FOR EVALUATION`

---

## 1. Executive Summary

Phase 3.4 implements an autonomous **local last-mile disaster warning architecture** that operates continuously in disconnected Himalayan corridors:
- **Radio Physical Layer**: 34-byte compact binary LoRa frame with CRC-16-CCITT integrity verification.
- **Local Persistence**: Full SQLite edge store with tables for readings, alerts, packets, and cloud sync queues.
- **Local Edge Safety Engine**: Evaluates regolith instability in $< 50\,\text{ms}$ (`SAFE`, `WATCH`, `WARNING`, `CRITICAL`) using Eastern Himalaya empirical thresholds.
- **Siren Controller**: Fail-safe acoustic alert manager defaulting to `DRY_RUN=true` with tamper-evident audit logging.
- **BLE Alert Bridge**: Point-to-point wireless gateway communicating with paired field units via HMAC-SHA256 authenticated packets.
- **LoRa Mesh Topology**: Supports direct and single-relay hops with deterministic sequence deduplication.
- **Cloud Resiliency**: Continuous background sync watchdog buffering records when disconnected and automatically flushing upon reconnection.
- **Unified UI**: Dedicated `/edge-network` mission-control dashboard and compact homepage telemetry ribbon.

---

## 2. Files Created & Modified

### Subsystem Modules (`backend/edge/`)
1. [`backend/edge/__init__.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/__init__.py): Package exports for edge symbols.
2. [`backend/edge/packet.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/packet.py): 34-byte binary packet serializer/deserializer with CRC-16-CCITT.
3. [`backend/edge/edge_store.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/edge_store.py): SQLite local persistence (`edge_store.db`) with sync queue management.
4. [`backend/edge/risk_evaluator.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/risk_evaluator.py): Deterministic Eastern Himalaya regolith risk thresholds.
5. [`backend/edge/siren_controller.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/siren_controller.py): Acoustic siren controller enforcing dry-run safety.
6. [`backend/edge/ble_bridge.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/ble_bridge.py): Point-to-point BLE alert bridge with allowlists and HMAC signing.
7. [`backend/edge/mesh.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/mesh.py): LoRa mesh topology tracking and packet deduplication.
8. [`backend/edge/gateway.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/gateway.py): Master EdgeGateway pipeline orchestrator.
9. [`backend/edge/sync.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/sync.py): Cloud sync queue manager with exponential backoff.
10. [`backend/edge/routes.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/routes.py): Flask Blueprint exposing 10 REST endpoints.
11. [`backend/edge/adapters.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/adapters.py): Sensor, LoRa, BLE, Siren, and MQTT hardware adapters.
12. [`backend/edge/sensor_node.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/backend/edge/sensor_node.py): Sensor node simulation and telemetry generation.

### Web Templates & UI
1. [`templates/edge_network.html`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/templates/edge_network.html): Standalone `/edge-network` mission-control monitoring dashboard.
2. [`templates/index.html`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/templates/index.html): Added compact "EDGE NETWORK" module ribbon and header link.

### Test Suites (`tests/`)
1. [`tests/test_edge_packet.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_packet.py): 6 tests (CRC, binary encode/decode, malformed rejection).
2. [`tests/test_edge_store.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_store.py): 6 tests (SQLite CRUD, queue stats, buffering).
3. [`tests/test_edge_risk.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_risk.py): 5 tests (Himalayan threshold evaluation, state transitions).
4. [`tests/test_edge_siren.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_siren.py): 5 tests (Dry-run safety invariants, test events, audit log).
5. [`tests/test_edge_ble.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_ble.py): 6 tests (HMAC signing, allowlist pairing, alert dispatch).
6. [`tests/test_edge_mesh.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_mesh.py): 6 tests (Deduplication, node health, topology).
7. [`tests/test_edge_gateway.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_gateway.py): 5 tests (End-to-end pipeline, offline buffer toggle).
8. [`tests/test_edge_api.py`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/tests/test_edge_api.py): 7 tests (REST endpoint contract tests).

### Documentation (`docs/`)
1. [`docs/PAHAD_EDGE_ARCHITECTURE.md`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/docs/PAHAD_EDGE_ARCHITECTURE.md): System architecture and hardware boundary.
2. [`docs/PAHAD_EDGE_PROTOCOL.md`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/docs/PAHAD_EDGE_PROTOCOL.md): 34-byte binary packet specification.
3. [`docs/PAHAD_SIREN_PROTOCOL.md`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/docs/PAHAD_SIREN_PROTOCOL.md): Acoustic siren state machine and dry-run safety.
4. [`docs/PAHAD_BLE_PROTOCOL.md`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/docs/PAHAD_BLE_PROTOCOL.md): BLE point-to-point bridge specification.
5. [`docs/PAHAD_PHASE3_4_REPORT.md`](file:///c:/Users/dimpu/Downloads/PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi/docs/PAHAD_PHASE3_4_REPORT.md): This comprehensive verification report.

---

## 3. Subsystem Technical Breakdown

### 3.1 34-Byte LoRa Binary Packet Layout
```
Offset    Field                  Type     Encoding
[0]       Version                uint8    1
[1]       Flags                  uint8    bit0=DEMO, bit1=RELAY_HOP, bit2=ALERT_TRIGGERED
[2:4]     Node ID Hash           uint16   CRC-16 over string node_id
[4:8]     Sequence               uint32   Monotonic counter
[8:12]    Timestamp              uint32   Epoch seconds
[12:16]   Soil Moisture VWC      float32  IEEE 754
[16:20]   Pore Pressure kPa      float32  IEEE 754
[20:24]   Tilt Angle deg         float32  IEEE 754
[24:28]   Rainfall mm/h          float32  IEEE 754
[28]      Battery %              uint8    0 - 100
[29:31]   Temperature C * 10     int16    Fixed-point Celsius
[31]      Humidity %             uint8    0 - 100
[32:34]   CRC-16-CCITT Checksum  uint16   Over bytes [0:32]
```

### 3.2 Eastern Himalaya Safety Thresholds (`EdgeRiskEvaluator`)
```python
anomaly_score = (
    0.35 * (soil_moisture / 55.0) +
    0.30 * (pore_pressure / 40.0) +
    0.20 * (tilt_degrees / 3.0) +
    0.15 * (rainfall_mm_h / 50.0)
)
```
- `CRITICAL`: Anomaly score $\ge 0.80$ OR $\ge 1$ critical limit (Rain $> 45\,\text{mm/h}$, Tilt $> 3.0^\circ$, Moisture $> 55\%$, Pore Pressure $> 38\,\text{kPa}$).
- `WARNING`: Anomaly score $\ge 0.40$ OR $\ge 2$ warning limits.
- `WATCH`: Anomaly score $\ge 0.35$ OR $\ge 1$ watch limit.
- `SAFE`: Normal baseline monitoring.

### 3.3 Offline Buffering & Resynchronization Scenario
Verified via `test_edge_gateway.py`:
1. Cloud link active → Packets processed and queued.
2. Simulated disconnect via `/api/edge/toggle-cloud` → Cloud becomes `OFFLINE`.
3. High-hazard packet injected → Gateway evaluates `WARNING` state, dispatches dry-run siren alert, buffers reading in SQLite `edge_sensor_readings`.
4. Cloud link restored → `EdgeSync` flushes queue to central PAHAD API.

---

## 4. Test Verification Results

### 4.1 Edge Subsystem Tests (`pytest tests/test_edge_*.py`)
```
tests/test_edge_api.py .......                                           [ 15%]
tests/test_edge_ble.py ......                                            [ 28%]
tests/test_edge_gateway.py .....                                         [ 39%]
tests/test_edge_mesh.py ......                                           [ 52%]
tests/test_edge_packet.py ......                                         [ 65%]
tests/test_edge_risk.py .....                                            [ 76%]
tests/test_edge_siren.py .....                                           [ 86%]
tests/test_edge_store.py ......                                          [100%]

============================= 46 passed in 2.84s ==============================
```

### 4.2 Master Combined Regression Suite
```bash
python -m pytest tests/test_mobile_api_contract.py tests/test_offline_*.py tests/test_event_*.py tests/test_edge_*.py tests/test_pahad_*.py -q
# Result: 208 passed in 56.13s (100% PASS RATE)
```
- **Phase 3.4 Edge Tests**: 46/46 PASSED
- **Phase 3.3 Mobile Contract Tests**: 9/9 PASSED
- **Phase 3.2/3.3 Offline Manifest & Field Reports**: 22/22 PASSED
- **Phase 3.1 Event Model & Validation**: 31/31 PASSED
- **PAHAD Multimodal Engine & Core Integrations**: 100/100 PASSED

---

## 5. Critical Honesty & Hardware Boundaries

Per Section 37 instructions:
1. **LoRa Radio Status**: The current environment uses `MockLoRaAdapter` and Python binary serialization (`struct >BBHIIffffBhB`). Physical SX1262 SPI radios are **not physically connected** to this development host.
2. **BLE Scope**: The BLE bridge is configured strictly for **paired local tactical units and road beacons**. It is **not** an un-paired mass civilian broadcast tool.
3. **Siren Actuation**: `SIREN_HARDWARE_ENABLED` is `false` and `SIREN_DRY_RUN` is `true`. All test events generate `SIREN_TEST_EVENT` audit records without driving real 120 dB acoustic transducers.
4. **Data Provenance**: Injected demo records are tagged explicitly as `[DEMO]`, buffered records as `[CACHED]`, and simulated hardware outputs as `[SIMULATED]`.

---

## 6. Acceptance Criteria Sign-Off

| Requirement | Status | Verification |
|---|---|---|
| Sensor Packet Schema | **COMPLETE** | `backend/edge/packet.py` (34-byte binary + JSON) |
| Packet Encoder / Decoder | **COMPLETE** | `EdgePacket.to_binary()` & `from_binary()` |
| SQLite Edge Store | **COMPLETE** | `EdgeStore` (`edge_store.db`, 5 tables) |
| Offline Buffering | **COMPLETE** | Verified via `test_edge_gateway.py` |
| Cloud Resynchronization | **COMPLETE** | `EdgeSync.flush_sync_queue()` |
| Edge Risk Evaluator | **COMPLETE** | `EdgeRiskEvaluator` (Himalayan thresholds) |
| Siren Dry-Run Safety | **COMPLETE** | `SirenController` (`DRY_RUN=true` default) |
| BLE Abstraction | **COMPLETE** | `BLEAlertBridge` (HMAC-SHA256 authenticated) |
| LoRa Mesh Topology | **COMPLETE** | `LoRaMesh` (Direct + Relay, deduplication) |
| Edge REST APIs | **COMPLETE** | 10 endpoints in `backend/edge/routes.py` |
| Edge Network Page | **COMPLETE** | `/edge-network` (`templates/edge_network.html`) |
| Mobile Edge Status | **COMPLETE** | Integrated into mobile drawer & EdgeTestScreen |
| Demo Injection | **COMPLETE** | `/api/edge/demo/inject` (`PAHAD_DEMO_MODE=1`) |
| No Accidental Transmission | **COMPLETE** | Dry-run invariants strictly enforced |
| Full Test Suite | **COMPLETE** | 46/46 Edge tests passed |
| Master Regressions | **COMPLETE** | 208/208 total tests passed |

**Conclusion**: PARVAT NETRA / PAHAD AI Phase 3.4 is complete, tested, documented, and verified.
