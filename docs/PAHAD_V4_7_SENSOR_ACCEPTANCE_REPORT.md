# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Sensor Acceptance Lifecycle & Stage Transition Audit Report

**Document Version**: 1.0.0  
**Phase**: V4.7 Engineering  
**Engine Implementation**: `engine/sensor_acceptance_engine.py`  
**Test Suite**: `tests/test_v4_7_commissioning.py`  

---

## 1. Acceptance Stage Enforcement Matrix

The `SensorAcceptanceEngine` strictly enforces entry prerequisites for each lifecycle stage:

| Stage | Prerequisites & Evidence Mandatory Requirements | Failure Behavior |
| :--- | :--- | :--- |
| **`PLANNED`** | Unique `sensor_id`, corridor binding, sensor class | Rejects duplicate IDs |
| **`RECEIVED`** | Delivery receipt document / shipping manifest reference | Remains in `PLANNED` |
| **`IDENTIFIED`** | Verified manufacturer, model, non-placeholder serial number, hardware revision | Transitions to `UNVERIFIED_IDENTITY` |
| **`CALIBRATED`** | NABL / certified laboratory calibration certificate reference, valid dates | Status `CALIBRATION_MISSING` / rejected |
| **`BENCH_ACCEPTED`** | Successful 18-byte LoRa HIL packet test, CRC16 pass log | Rejects transition to bench acceptance |
| **`INSTALLED`** | Physical field location: Latitude, Longitude, Elevation, Depth, Orientation, Installer | Rejects transition without physical coords |
| **`CONNECTED`** | Gateway binding, RSSI $\ge -115\text{ dBm}$, battery voltage $\ge 11.0\text{ V}$ | Remains `INSTALLED` |
| **`TELEMETRY_VALIDATED`** | $\ge 10$ consecutive valid observations without CRC errors or clock drift | Observation counter reset to 0 on failure |
| **`FIELD_COMMISSIONED`** | Human authorized credentials (`BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026`) | **Software-only commissioning strictly rejected** |
| **`MONITORING`** | Operational status confirmed by District Emergency Operations Centre (EOC) | Requires commissioned status |

---

## 2. Hardware Identity Verification Results

In `tests/test_v4_7_commissioning.py`:
- Sensors with verified serial numbers (e.g. `GK-4500AL-9988`) passed identity verification with `identity_verified = True`.
- Sensors with placeholder serial numbers (`TBD`, `UNKNOWN`, `none`, `0000`, `n/a`, `pending`, `""`) were immediately detected and isolated with `STATE_UNVERIFIED_IDENTITY`.
- Illegal stage jumps (e.g., trying to jump from `PLANNED` directly to `FIELD_COMMISSIONED`) were blocked by the state machine validator.
- Software-only attempts to claim `FIELD_COMMISSIONED` without authorized human inspector credentials were 100% rejected.
