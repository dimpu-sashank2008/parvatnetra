# PARVAT NETRA / PAHAD AI — PHASE 6C
## Physical Sensor & Edge Bench Commissioning Final Engineering Report

**Project**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Phase**: 6C — Physical Sensor + Edge Bench Commissioning  
**Status**: COMPLETED  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Date**: 2026-09-10  
**Final Verdict**: `HARDWARE_BENCH_READY` (with `PHYSICAL_DEPLOYMENT_PENDING`)  

---

## 1. Executive Summary

Phase 6C moves PARVAT NETRA / PAHAD AI from verified institutional data connectors (Phase 6B) to a comprehensive physical sensor and edge bench commissioning infrastructure.

### Critical Invariants Preserved:
1. **Zero False Deployment Claims**: In the absence of physical borehole instruments connected on the NH-10 Pakyong / Singtam slopes, the platform operational status remains strictly:
   $$\mathbf{PHYSICAL\_DEPLOYMENT\_PENDING}$$
2. **Strict Provenance Integrity**: All bench simulator outputs are branded `provenance = "[SIMULATED]"`. Zero bench simulator data is exported or ingested into operational machine learning training sets.
3. **Decoupled Local Safety**: On-site edge corridor acoustic sirens (110 dB) operate under an autonomous safety policy in default `DRY_RUN` mode. Physical actuation requires multi-threshold sensor confirmation and authenticated HMAC authorization, cleanly separated from regional Common Alerting Protocol (CAP v1.2) public broadcasts.

---

## 2. Deliverables & Component Matrix

### 2.1 Embedded Firmware & Abstraction Layer (`firmware/`)
- `firmware/interfaces.py`: Hardware-independent interfaces for transducers (`PiezometerReader`, `TiltReader`, `RainGaugeReader`, `SoilMoistureReader`, `TemperatureReader`), battery monitor, signal monitor, RTC clock, and local circular FIFO buffer (`LocalCircularBuffer`).
- `firmware/packet_codec.py`: 18-byte packed binary LoRa frame codec (Big-Endian) with CRC-16-CCITT integrity validation and conversion to canonical JSON telemetry packets.
- `firmware/esp32_node.py`: Full Python reference runtime simulating the ESP32 state machine: initialize $\to$ read $\to$ validate $\to$ timestamp $\to$ package $\to$ buffer $\to$ transmit $\to$ retry with exponential backoff $\to$ heartbeat.
- `firmware/esp32_firmware_reference.cpp`: Production C++/ESP-IDF firmware source code for flashing onto real physical ESP32-S3 / ESP32-WROOM-32D nodes with SX1262 LoRa transceivers and FreeRTOS deep sleep management.

### 2.2 Hardware-In-The-Loop (HITL) & Physical Port Detection
- `services/hardware_interface.py`: Multi-transport stream ingestion (Serial/USB, TCP, MQTT). Enumerates connected serial ports and accurately categorizes physical presence into four states:
  - `NO_PHYSICAL_DEVICE`
  - `BENCH_SIMULATOR`
  - `PHYSICAL_DEVICE_CONNECTED`
  - `PHYSICAL_DEVICE_ACTIVE`
- Enforces timekeeping synchronization and calculates `clock_offset_ms`, rejecting severe drift ($>300\text{s}$) and future timestamps ($>10\text{s}$).

### 2.3 Enhanced 8-Stage Commissioning & Calibration Verification
- `scripts/commission_sensor.py`: Enforces the authoritative 8-stage pipeline:
  $$\text{REGISTER} \to \text{INSTALL} \to \text{CALIBRATE} \to \text{CONNECT} \to \text{HEARTBEAT} \to \text{TELEMETRY} \to \text{VALIDATE} \to \text{ACCEPT}$$
  Records evidence trails and metrology engineer signatures. Yields explicit exit codes:
  - `0`: `ACCEPTED` (certified with SHA-256 digital certificate)
  - `1`: `REJECTED` (invalid calibration curve, out-of-bounds coords, degraded quality)
  - `2`: `COMMISSIONING_FAILED` (missing prerequisite stage)
- `engine/sensor_calibration.py`: Extended with `certificate_ref`, `technician`, validity windows, and `is_calibrated()` validation.

### 2.4 Multi-Factor Sensor Health Runtime
- `engine/sensor_registry.py`: Implemented `get_composite_sensor_health(device_id)` evaluating battery level, signal RSSI, clock offset drift, calibration status, and heartbeat freshness.
- Output ratings: `GOOD`, `DEGRADED`, `INVALID`, `OFFLINE`.

### 2.5 Bench Simulator Harness
- `services/bench_simulator.py`: Isolated test harness generating 8 stress scenarios:
  `BASELINE_NORMAL`, `RAIN_SURGE`, `PORE_PRESSURE_SPIKE`, `TILT_ACCELERATION`, `DISPLACEMENT_SLIP`, `SENSOR_DROPOUT`, `PACKET_LOSS`, and `GATEWAY_OUTAGE`.
  All generated telemetry is stamped `[SIMULATED]`.

### 2.6 REST APIs
- `GET /api/iot/bench/status`: Reports real-time physical device presence, port enumerations, bench simulator status, and confirms `physical_deployment_state = "PHYSICAL_DEPLOYMENT_PENDING"`.

---

## 3. Automated Test Verification

| Test Suite File | Focus Area | Items | Status |
| :--- | :--- | :---: | :---: |
| `tests/test_hardware_packet.py` | 18-byte binary frame, CRC-16-CCITT, packing, canonical JSON conversion | 7 | **PASSED** |
| `tests/test_hardware_serial.py` | Port detection, HITL stream ingestion, clock drift rejection | 10 | **PASSED** |
| `tests/test_hardware_buffer.py` | Local circular FIFO buffer, capacity rollover, offline replay | 3 | **PASSED** |
| `tests/test_hardware_recovery.py`| Gateway reboot, power cycle, network outage buffering & flush | 3 | **PASSED** |
| `tests/test_sensor_commissioning_hardware.py` | 8-stage CLI commissioning, technician sign-off, calibration rejections | 5 | **PASSED** |
| `tests/test_sensor_health_runtime.py` | Multi-factor health ratings (GOOD, DEGRADED, INVALID, OFFLINE) | 7 | **PASSED** |
| `tests/test_hardware_pahad_pipeline.py` | Sensor $\to$ Gateway $\to$ ObservationStore $\to$ Sector Snapshot $\to$ Alert Policy $\to$ Siren | 3 | **PASSED** |
| **Phase 6C Total** | | **38** | **38/38 PASSED (100%)** |

---

## 4. Documentation Index

1. `docs/PHASE6C_HARDWARE_BENCH_AUDIT.md`: Pre-implementation audit and gap analysis.
2. `docs/PHASE6C_HARDWARE_REFERENCE.md`: ESP32 node and Raspberry Pi gateway reference architecture, pinout, power budget, and BLE GATT profile.
3. `docs/PHASE6C_PACKET_SPECIFICATION.md`: Compact 18-byte binary frame byte layout, scaling math, and canonical JSON schema.
4. `docs/PHASE6C_BENCH_TEST_PLAN.md`: Bench simulation protocols and environmental stress scenarios.
5. `docs/PHASE6C_COMMISSIONING_PROCEDURE.md`: Standard Operating Procedure (SOP) for 8-stage field and bench commissioning.
6. `docs/PHASE6C_HARDWARE_REPORT.md`: This comprehensive engineering report.
