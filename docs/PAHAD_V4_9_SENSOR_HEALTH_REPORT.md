# PARVAT NETRA / PAHAD AI — PHASE V4.9 SENSOR HEALTH REPORT
## Diagnostic Telemetry, Hardware Integrity & Health Bounds Verification

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Phase**: V4.9 — Joint Field Installation, LoRa Gateway Alignment & First Live Telemetry Commissioning  
**Health Monitoring Status**: `BENCH_VALIDATED_FIELD_PENDING`  
**Monitored Parameters**: Battery Voltage, Enclosure Temp, RSSI, SNR, Dropout Counters  

---

### 1. Sensor Health Architecture (Section 22)
Physical sensors in rugged Himalayan gorges face severe environmental stress: monsoon flooding, rockfall impacts, sub-zero freeze-thaw cycles, and solar charging intermittency. Each node transmits periodic diagnostic health telemetry in addition to primary physical readings.

The health monitor tracks 4 primary health vectors:
1. **Power Subsystem**: LiFePO4 battery pack voltage ($3.0\text{ V}$ cutoff, $3.2\text{ V}$ nominal, $3.65\text{ V}$ float charge).
2. **Thermal Subsystem**: Internal electronics temperature ($-20^\circ\text{C}$ to $+65^\circ\text{C}$).
3. **RF Propagation Link**: Received Signal Strength Indicator ($\text{RSSI} \ge -125\text{ dBm}$) and Signal-to-Noise Ratio ($\text{SNR} \ge -15\text{ dB}$).
4. **Heartbeat & Dropout Counter**: Missing consecutive periodic intervals increment the dropout counter; $> 3$ consecutive misses trigger `SENSOR_DROPOUT` warning.

---

### 2. Operational Health Thresholds

| Sensor Node | Primary Physical Metric | Normal Health Range | Warning Threshold | Critical Fault Action |
| :--- | :--- | :--- | :--- | :--- |
| `PIEZO-NH10-KM48-01` | Pore Water Pressure | $0–250\text{ kPa}$ | $> 350\text{ kPa}$ | Isolate node; trigger pore-pressure alert |
| `INCL-NH10-KM48-01` | Cumulative Displacement| $0–15\text{ mm}$ | $> 25\text{ mm}$ | Flag shear-plane kinematic anomaly |
| `TILT-NH10-KM48-01` | Biaxial Slope Angle | $-5^\circ\text{ to }+5^\circ$ | $> \pm 10^\circ$ | Immediate slope tilt alert |
| `RAIN-NH10-KM48-01` | Rainfall Intensity | $0–50\text{ mm/h}$ | $> 80\text{ mm/h}$ | Cloudburst alert to EOC coordinator |
| `GW-NH10-KM48-01` | Battery Voltage | $12.0–14.4\text{ V}$ | $< 11.5\text{ V}$ | Low-power telemetry throttled to 15 min |

---

### 3. Current Health Status
Because physical installation on the NH-10 slope is pending joint field deployment with BRO Project Swastik:
- **Physical Nodes Online**: `0 / 5`
- **Bench / HIL Nodes Online**: `5 / 5` (bench operational)
- **Sensor Dropout State**: All nodes currently classified as `PHYSICAL_TELEMETRY_PENDING`.
- **Corridor Aggregate Health**: `BENCH_READY / PENDING_FIELD_INSTALLATION`.
