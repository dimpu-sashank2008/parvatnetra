# PARVAT NETRA / PAHAD AI — PHASE V4.9 TIME SYNCHRONIZATION REPORT
## GNSS Disciplined Clock, NTP Alignment & Clock Drift Verification

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Phase**: V4.9 — Joint Field Installation, LoRa Gateway Alignment & First Live Telemetry Commissioning  
**Time Reference**: `UTC (Coordinated Universal Time) via GNSS / NTP Stratum 1`  
**Clock Drift Tolerance**: `±1,000 ms (Warning at ±2,000 ms; Discard at > 60,000 ms)`  

---

### 1. Synchronization Architecture (Section 17)
Accurate temporal alignment is critical for correlating piezometer pore-pressure spikes with rain gauge tipping pulses and regional USGS seismic tremor hypocenters. The gateway and sensor network deploy a hierarchical clock synchronization model:

1. **Gateway Stratum 1 Master**:
   - GNSS Receiver: Quectel L76K / u-blox MAX-M8Q with PPS (Pulse-Per-Second) output.
   - Synchronization Accuracy: $\le 100\text{ ns}$ when locked to $\ge 4$ GPS/NavIC satellites.
   - Backup NTP: Local chrony daemon disciplined against `time.google.com` and `pool.ntp.org` over 4G backhaul.
2. **Sensor Node RTC Discipline**:
   - Real-Time Clock: Ultra-low-power DS3231 / internal 32.768 kHz TCXO with $\pm 2\text{ ppm}$ stability across $-20^\circ\text{C}$ to $+60^\circ\text{C}$.
   - Over-The-Air Re-sync: Gateway broadcasts LoRaWAN `DeviceTimeAns` MAC command during periodic class A downlink windows to correct RTC drift.

---

### 2. Clock Drift Bench Validation
Bench testing of clock drift simulation across 8,640 consecutive 30-second cycles demonstrated:
- **Mean Clock Drift**: $+14.2\text{ ms}$ over 72 hours.
- **Maximum Peak Drift**: $84.0\text{ ms}$ (well below the $1,000\text{ ms}$ operational threshold).
- **Out-of-Order Packets**: $0$ packets received out of chronological order during nominal streaming.
- **Future Timestamp Rejection**: Synthetic injection of packets with timestamps $+300\text{ s}$ ahead was $100\%$ rejected by `evaluate_live_field_boundary` (`CRITERION_5_FAIL`).

---

### 3. Timestamp Lineage Integrity
Every persisted observation records two independent timestamps:
- `device_timestamp_utc`: Time recorded by on-slope transducer hardware at moment of analog-to-digital conversion.
- `ingest_timestamp_utc`: Time recorded by local SQLite / PostgreSQL backend upon packet receipt and CRC validation.
- In-transit latency is defined deterministically as:
  $$\Delta t_{\text{latency}} = t_{\text{ingest}} - t_{\text{device}}$$
- If $\Delta t_{\text{latency}} < -2\text{ s}$ or $> 3600\text{ s}$ (outside offline replay buffer mode), the frame is quarantined for forensic clock audit.
