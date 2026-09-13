# PHASE 6C — PHYSICAL SENSOR & HARDWARE BENCH COMMISSIONING AUDIT

**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Phase**: 6C — Physical Sensor + Edge Bench Commissioning  
**Status Entering Phase**: Phase 6A (Complete), Phase 6B (Complete)  
**Evaluation Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Author**: PARVAT NETRA / PAHAD AI Core Engineering Team  
**Date**: 2026-09-10  

---

## 1. Executive Summary & Audit Scope

The transition of PARVAT NETRA / PAHAD AI from verified institutional connectors (Phase 6B) to physical sensor and edge bench commissioning (Phase 6C) establishes the hardware contracts, embedded firmware abstractions, and edge-to-cloud telemetry pipelines necessary for hillslope instrumentation.

This audit evaluates:
1. **Sensor Transducer Specifications**: Validating mechanical and electrical limits for vibrating-wire piezometers, in-place MEMS inclinometers, biaxial tiltmeters, tipping-bucket rain gauges, and soil moisture probes.
2. **Edge Concentrator Protocol**: Auditing LoRaWAN IN865 radio parameters, 18-byte compact binary frames, and local SQLite offline buffering.
3. **Commissioning State Machine**: Auditing the 8-stage verification pipeline (`REGISTER` $\to$ `INSTALL` $\to$ `CALIBRATE` $\to$ `CONNECT` $\to$ `HEARTBEAT` $\to$ `TELEMETRY` $\to$ `VALIDATE` $\to$ `ACCEPT`).
4. **Hardware-In-The-Loop Readiness**: Assessing serial/USB, TCP, and MQTT stream ingestion interfaces.
5. **Acoustic Siren Relay Security**: Verifying physical relay abstraction and dry-run safety gates.
6. **Physical Deployment Reality**: Explicitly distinguishing attached bench simulators from genuine field-deployed sensors.

---

## 2. Comprehensive Subsystem Audit Matrix

| Subsystem / Component | Current Repo Asset | Tested In | Operating Status | Gaps Identified | Phase 6C Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Piezometer Interface** | `docs/PHASE6A_SENSOR_SPECIFICATION.md` | Phase 6A | `SPECIFIED` | No standalone firmware driver abstraction | Implement `PiezometerReader` in `firmware/interfaces.py` |
| **Inclinometer / Tilt** | `docs/PHASE6A_SENSOR_SPECIFICATION.md` | Phase 6A | `SPECIFIED` | No biaxial resultant calc in firmware | Implement `TiltReader` with vector magnitude in `firmware/` |
| **Rain Gauge Pulse** | `docs/PHASE6A_SENSOR_SPECIFICATION.md` | Phase 6A | `SPECIFIED` | Debounce interrupt logic unmodeled | Implement `RainGaugeReader` with 50ms software debounce |
| **Soil Moisture TDR** | `docs/PHASE6A_SENSOR_SPECIFICATION.md` | Phase 6A | `SPECIFIED` | SDI-12 scaling parser missing | Implement `SoilMoistureReader` (0–1.0 $m^3/m^3$ bounds) |
| **18-Byte Binary Frame** | `docs/PHASE6A_EDGE_PROTOCOL.md` | Phase 6A | `PARTIAL` | Binary encoder/decoder lacks unit test suite | Implement `firmware/packet_codec.py` with CRC-16-CCITT |
| **ESP32 Edge Firmware** | *None* | Phase 6B | `NOT_IMPLEMENTED` | Missing C++ and Python node reference code | Implement `firmware/esp32_node.py` & `.cpp` reference |
| **Local FIFO Buffer** | `services/edge_gateway.py` | Phase 6A | `OPERATIONAL` | Device-side flash circular buffer unmodeled | Implement `LocalBuffer` in `firmware/` with flash replay |
| **Serial / USB HITL** | *None* | Phase 6B | `NOT_IMPLEMENTED` | No live serial port listener for bench testing | Implement `services/hardware_interface.py` with port discovery |
| **Calibration Verification**| `engine/sensor_calibration.py` | Phase 6A/6B | `OPERATIONAL` | Missing technician & certificate reference metadata | Extend `CalibrationRecord` with technician & certificate fields |
| **Sensor Health Runtime** | `engine/sensor_registry.py` | Phase 6A/6B | `PARTIAL` | Composite scoring (battery, RSSI, drift, calib) missing | Implement `get_composite_health()` in `SensorRegistry` |
| **Bench Test Harness** | *None* | Phase 6B | `NOT_IMPLEMENTED` | Bench testing requires ad-hoc scripts | Implement `services/bench_simulator.py` tagged `[SIMULATED]` |
| **Edge Anomaly Safety** | `engine/edge_alert_policy.py` | Phase 6A | `OPERATIONAL` | Needs clear decoupling from public CAP v1.2 | Verify edge siren safety decoupling and audit logging |
| **Physical Detection** | *None* | Phase 6B | `NOT_IMPLEMENTED` | System cannot detect whether USB hardware is connected | Implement physical device detection state machine |

---

## 3. Provenance & Invariant Audit

### 3.1 Provenance Segregation
- Invariant: Bench testing data generated during evaluation must be explicitly stamped `provenance = "[SIMULATED]"`.
- Invariant: Zero synthetic or bench data may be ingested into historical training datasets (`real_train.csv`, `real_val.csv`).
- Invariant: In the absence of physically wired borehole instruments on the NH-10 Pakyong slope, the operational status must remain:
  $$\mathbf{PHYSICAL\_DEPLOYMENT\_PENDING}$$

### 3.2 Siren Safety & Public Alert Decoupling
- Invariant: On-site edge corridor acoustic sirens (110 dB) are intended for immediate traffic chokepoint clearance during communications blackout.
- Invariant: Edge sirens must NOT trigger regional NDMA/SDRF Common Alerting Protocol (CAP v1.2) public warning broadcasts without central EOC multi-source confirmation.
- Invariant: Physical siren relay actuation requires:
  $$\text{SIREN\_HARDWARE\_ENABLED}=1 \quad \land \quad \text{dry\_run}=\text{False} \quad \land \quad \text{HMAC-SHA256 Token}$$

---

## 4. Hardware Reference Architecture Decision

1. **Microcontroller**: Espressif ESP32-WROOM-32 / ESP32-S3 (Dual Xtensa LX7 @ 240 MHz, 512 KB SRAM, 4 MB SPI Flash). Low power deep-sleep ($<15\ \mu\text{A}$), hardware SPI/I2C/UART interfaces.
2. **LoRa Transceiver**: Semtech SX1262 / SX1268 via SPI interface. Frequency: 865–867 MHz (IN865), bandwidth 125 kHz, Spreading Factor SF7 to SF12, output power +14 dBm.
3. **Gateway Platform**: Raspberry Pi Compute Module 4 (CM4) / Industrial NXP i.MX8 with Waveshare SX1302 LoRaWAN Gateway HAT.
4. **Primary Backhaul**: Cellular 4G/LTE Cat-M1 / Ethernet with fallback to offline SQLite circular buffer.
5. **Local Maintenance / Commissioning**: BLE 5.0 (Custom GATT Service `0000FE60`) for smartphone field technician setup.

---

## 5. Audit Conclusion & Next Steps

The existing codebase contains robust protocol specifications (`PHASE6A_SENSOR_SPECIFICATION.md`, `PHASE6A_EDGE_PROTOCOL.md`) and operational gateway/validation services (`edge_gateway.py`, `telemetry_contract.py`).

Phase 6C must bridge the remaining gaps:
1. Provide concrete embedded firmware source and hardware-independent abstractions in `firmware/`.
2. Implement 18-byte LoRa packet encoder/decoders with complete CRC-16 mathematical verification.
3. Deliver a robust Hardware-In-The-Loop (HITL) interface in `services/hardware_interface.py`.
4. Deploy the isolated bench simulator (`services/bench_simulator.py`) for automated failure mode testing.
5. Enhance commissioning and calibration state tracking.
6. Verify the entire end-to-end telemetry chain from firmware packet through ObservationStore to PAHAD risk calculations.
