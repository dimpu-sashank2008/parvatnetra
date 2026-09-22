# PARVAT NETRA / PAHAD AI — PHASE V4.6
# Fail-Closed Telemetry Degradation & Fault Tolerance Report

**Document Version**: 1.0.0  
**Target Environment**: Remote Mountain Corridor (NH-10 Sikkim)  
**Safety Principle**: Fail-Closed Degradation (Zero False Assumptions of Safety)  

---

## 1. The Fail-Closed Philosophical Imperative

In critical disaster risk telemetry, system failures (cable shears, rockfall impacts, solar battery depletion, or LoRa RF link blockage) must NEVER lead to a false sense of security.

$$\textbf{Absence of Telemetry} \ne \textbf{Absence of Hazard}$$

If a borehole inclinometer stops sending packets, the system must **NOT** assume the displacement velocity is zero. Instead, it must immediately:
1. Mark the instrument node as `STALE` (at $15\text{ min}$) and then `UNAVAILABLE` (at $30\text{ min}$).
2. Emit an administrative alert `SENSOR_OFFLINE` to the telemetry journal.
3. Degrade the platform's composite confidence rating from `HIGH` ($0.90+$) to `MEDIUM_DEGRADED` ($0.50$).
4. Alert the EOC dashboard that localized site safety is **unverified**, recommending manual visual inspection patrols.

---

## 2. Sensor Failure Mode Matrix

| Failure Scenario | Detection Mechanism | System State Transition | Impact on Dual-Stream Inference | Mitigation & Action |
| :--- | :--- | :--- | :--- | :--- |
| **Piezometer Signal Loss** | No heartbeat for $>900\text{ s}$ | `LIVE` $\to$ `STALE` $\to$ `UNAVAILABLE` | Pore pressure triggers disabled; fallback to regional antecedent rainfall | Notify instrumentation engineer; dispatch BRO patrol |
| **Inclinometer Cable Severance** | Frame checksum error or timeout | Node marked `BAD` / `UNAVAILABLE` | Shear displacement velocity unavailable; confidence degraded | Inspect borehole casing head for rockfall severance |
| **Tiltmeter Drift / High Noise** | Excessive variance ($\Delta \theta > 10^\circ/\text{h}$) | Quality flag downgraded to `DEGRADED` | Trigger sensitivity lowered to avoid false alarms; telemetry marked degraded | Re-zero tilt sensor mount; verify bedrock anchor firmness |
| **Rain Gauge Clogging** | Zero tips during $>50\text{ mm}$ regional rain | Detected via IMD cross-comparison | Sensor flagged `SUSPECT_CLOGGED` | Dispatch field technician to clear leaf debris from funnel |
| **Edge Gateway Power Loss** | Battery $<10.0\text{ V}$ or 300s timeout | Gateway marked `OFFLINE` | All corridor sensors enter `STALE` state; edge buffer active | Solar panel cleaning / battery replacement dispatch |

---

## 3. Edge Buffering & Network Partition Resilience

When 4G LTE backhaul is severed due to monsoon landslides or optical fiber cuts:
- The local LoRaWAN gateway continues listening and storing raw binary frames in the local SQLite `EdgeBuffer` (`backend/edge/edge_store.py`).
- The ring buffer holds up to 100,000 observations (over 30 days of continuous operation for 5 sensors).
- Upon backhaul restoration, the gateway executes the `reconnect_and_replay` protocol, transmitting cached packets with original timestamps and transport tag `EDGE_BUFFER_REPLAY`.
- The server accepts replayed packets without flagging them as future or duplicate, restoring the complete historical sequence.
