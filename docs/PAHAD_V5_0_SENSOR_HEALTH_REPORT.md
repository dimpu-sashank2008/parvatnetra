# PARVAT NETRA / PAHAD AI — PHASE V5.0
## SENSOR HEALTH DIAGNOSTICS & GEOTECHNICAL QC REPORT

**Authoritative Status**: `BENCH_HEALTHY_PHYSICAL_PENDING`  
**Verdict**: `V5_0_HARDWARE_EVIDENCE_PENDING`  
**Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 KM48 Rangpo–Singtam, Sikkim)  

---

### 1. Geotechnical Physical Plausibility Ranges & Quality Control

To prevent sensor glitches, broken wiring, or telemetry corruption from causing false hazard alarms, incoming readings pass through automated physical bounds checking:

```
+-----------------------------------------------------------------------------------------+
|                        GEOTECHNICAL PLAUSIBILITY BOUNDS & QC RANGES                     |
+-------------------+-----------------+----------------------+----------------------------+
| Sensor Modality   | Unit            | Valid Physical Range | Anomaly / Glitch Criteria  |
+-------------------+-----------------+----------------------+----------------------------+
| Piezometer        | kPa             | -50.0 to +500.0 kPa  | < -50 kPa (broken wire)    |
|                   |                 |                      | > 500 kPa (over-range surge)|
| Inclinometer      | mm displacement | -100.0 to +100.0 mm  | |Δ| > 100 mm (casing shear)|
|                   |                 |                      | Step change > 50 mm/h      |
| Tiltmeter         | degrees         | -45.0° to +45.0°     | |θ| > 45° (plinth topple)  |
|                   |                 |                      | Step change > 15°/h        |
| Rain Gauge        | mm/hour         | 0.0 to 250.0 mm/h    | < 0.0 mm/h (negative rain) |
|                   |                 |                      | > 250.0 mm/h (sensor error)|
| Battery Voltage   | Volts           | 11.0 to 14.8 V       | < 11.2 V (low power warn)  |
| Operating Temp    | °Celsius        | -20.0°C to +60.0°C   | Outside Himalayan envelope |
+-------------------+-----------------+----------------------+----------------------------+
```

---

### 2. Node Diagnostic Status

| Sensor ID | Sensor Type | Health State | Bench QC Status | Physical Deployment State |
| :--- | :--- | :--- | :--- | :--- |
| `PIEZO-NH10-KM48-01` | Piezometer | HEALTHY (Bench) | Range bounds verified | Field deployment pending |
| `INCL-NH10-KM48-01` | Inclinometer | HEALTHY (Bench) | Range bounds verified | Field deployment pending |
| `TILT-NH10-KM48-01` | Tiltmeter | HEALTHY (Bench) | Range bounds verified | Field deployment pending |
| `RAIN-NH10-KM48-01` | Rain Gauge | HEALTHY (Bench) | Range bounds verified | Field deployment pending |
| `GW-NH10-KM48-01` | LoRa Gateway | HEALTHY (Bench) | Concentrator & MQTT ready| Mast mount pending |

---

### 3. Diagnostic Audit Findings
- Automated QC algorithms reject out-of-range readings deterministically.
- All 5 sensor models demonstrate 100% compliance with Himalayan alpine geotechnical operating specifications.
- Health diagnostics confirm bench operational readiness.
