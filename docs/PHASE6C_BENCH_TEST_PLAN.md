# PARVAT NETRA / PAHAD AI — PHASE 6C
## In-Situ Sensor Edge Bench Test Plan & Simulation Protocols

**Document**: `docs/PHASE6C_BENCH_TEST_PLAN.md`  
**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Status**: APPROVED TEST PLAN  
**Standard**: SIH 26001 / Phase 6C Quality Assurance  
**Date**: 2026-09-10  

---

## 1. Test Objectives & Boundaries

The Bench Test Plan validates the physical and embedded data pathway prior to field deployment on the NH-10 Pakyong / Tupul corridors.

### Non-Negotiable Test Rules:
1. **Simulation Marking**: All bench simulator data generated during testing MUST be stamped `provenance = "[SIMULATED]"`.
2. **Zero Model Contamination**: Bench simulator outputs must NEVER be exported or appended to operational training datasets (`real_train.csv`).
3. **No False Field Claims**: Successful completion of this bench test plan verifies edge software readiness (`HARDWARE_BENCH_READY`), but explicitly does NOT certify field installation (`PHYSICAL_DEPLOYMENT_PENDING`).

---

## 2. Bench Hardware Setup & Tooling

```
[ Workstation / Test Host ]
  - Python 3.11 Automated Test Runner (pytest)
  - Virtual Serial / COM Port Loopback (pty / com0com) or USB-to-UART CP2102 Bridge
  - Local Mosquitto MQTT Broker (port 1883)
  - Isolated SQLite Test Databases
        │
        ▼ (Bidirectional Serial @ 115200 baud / TCP Socket / MQTT)
[ ESP32 Node Emulator / Bench Hardware ]
  - Emulated Transducer Signals: Piezometer, Tiltmeter, Rain Gauge, Soil Moisture
  - Local Circular FIFO Buffer
  - Autonomous Anomaly State Machine (NORMAL -> WATCH -> CRITICAL)
        │
        ▼ (LoRa 18-Byte Binary Frame or JSON)
[ PARVAT NETRA Gateway & Ingestion Services ]
  - services/edge_gateway.py
  - services/hardware_interface.py
  - services/telemetry_contract.py
  - engine/observation_store.py
  - engine/edge_alert_policy.py
```

---

## 3. Test Scenarios & Stress Profiles

### Scenario A: Baseline Normal Operations (`BASELINE_NORMAL`)
- **Pore Pressure**: $10.0\text{ kPa}$ (Stable).
- **Tilt Resultant**: $0.05^\circ$ (Zero creep).
- **Rainfall Intensity**: $0.0\text{ mm/hr}$.
- **Expected Result**: Node reports `NORMAL` local safety state; Gateway accepts packet; Quality = `GOOD`; Siren remains silent.

### Scenario B: Monsoon Cloudburst Surge (`RAIN_SURGE`)
- **Pore Pressure**: Increasing steadily from $15.0\text{ kPa}$ to $32.0\text{ kPa}$.
- **Rainfall Intensity**: Cloudburst spike to $65.0\text{ mm/hr}$ ($>50.0\text{ mm/hr}$ Critical Threshold).
- **Expected Result**: Rain threshold triggered; Node flags local `CRITICAL` anomaly; Gateway evaluates acute corridor alert policy; Acoustic siren recommended in `DRY_RUN` mode.

### Scenario C: Slope Shear Acceleration (`SLOPE_SHEAR`)
- **Pore Pressure**: Critical saturation at $48.0\text{ kPa}$ ($>45.0\text{ kPa}$).
- **Tilt Acceleration**: $2.8^\circ/\text{day}$ ($>2.5^\circ/\text{day}$).
- **Shear Displacement**: $18.5\text{ mm/day}$ ($>15.0\text{ mm/day}$).
- **Expected Result**: Multi-sensor corridor threshold crossed; Gateway triggers local corridor warning policy; Traffic bypass advised.

### Scenario D: Cellular & Backhaul Network Outage (`NETWORK_OUTAGE`)
- **Condition**: Gateway internet connection intentionally dropped (`is_cloud_connected = False`).
- **Telemetry Stream**: Node continues transmitting 20 consecutive packets.
- **Expected Result**: Gateway local SQLite buffer accumulates 20 pending records (`BUFFERED_OFFLINE`); Zero packet loss.
- **Restoration**: Backhaul restored (`is_cloud_connected = True`); `flush_buffer()` replays records to Central ObservationStore in strict FIFO sequence; Duplicates cleanly rejected.

### Scenario E: Node Sudden Power Loss & Reboot (`POWER_CYCLE`)
- **Condition**: Sensor node power cut abruptly while sequence counter is at 150.
- **Reboot**: Node restarts; restores sequence counter from non-volatile memory or synchronizes with gateway; transmits sequence 151.
- **Expected Result**: Gateway validates non-decreasing sequence counter; no crash, no sequence corruption, zero packet loss.

### Scenario F: Clock Drift & Timestamp Desynchronization (`CLOCK_DRIFT`)
- **Condition**: Node transmits packet with timestamp skewed by $+600\text{ seconds}$ (future) or $-7200\text{ seconds}$ (stale).
- **Expected Result**: Telemetry validator flags `REJECTED_CLOCK_DRIFT_EXCESSIVE` or `REJECTED_FUTURE_TIMESTAMP`; Packet dropped from operational live feed.

### Scenario G: Calibration Expiry & Out-of-Bounds Transfer Function (`CALIBRATION_EXPIRY`)
- **Condition**: Node transmits data with an expired calibration certificate or zero-offset $>10000.0$.
- **Expected Result**: Sensor calibration engine downgrades quality to `DEGRADED` or `INVALID`; Confidence penalty applied to downstream PAHAD fusion.

---

## 4. Acceptance Verification Metrics

| Verification Check | Target Threshold | Method |
| :--- | :---: | :--- |
| **Packet Checksum Integrity** | $100.0\%$ CRC-16 accuracy | Byte-level bit corruption test |
| **FIFO Buffer Preservation** | $0$ dropped packets during backhaul loss | Disconnect test with 50 packets |
| **Deduplication Rejection** | $100.0\%$ multipath packets rejected | Repeat transmission with identical packet_id |
| **End-to-End Pipeline Latency** | $<250\text{ ms}$ (sensor packet to DB) | Timestamp difference instrumentation |
| **Siren Safety Guardrail** | $100.0\%$ physical actuation prevented in dry-run | Hardware relay inspection |
