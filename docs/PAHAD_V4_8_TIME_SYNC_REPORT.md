# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Multi-Tier Time Synchronization, Clock Drift & Latency Gating Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Modules**: `engine/telemetry_trust_engine.py`, `services/telemetry_contract.py`  
**Test Suite**: `tests/test_v4_8_real_telemetry_ingestion.py`  

---

## 1. Multi-Tier Clock Synchronization Hierarchy

In-situ telemetry packets traverse four distinct time domains before reaching the analytical core:

$$\begin{matrix}
T_{\text{sensor}} & \xrightarrow[\text{LoRa Uplink}]{} & T_{\text{gateway}} & \xrightarrow[\text{MQTT / TLS}]{} & T_{\text{server}} & \xrightarrow[\text{Pipeline}]{} & T_{\text{processing}} \\
\text{(Transducer RTC)} & & \text{(GNSS PPS Master)} & & \text{(NTP Central Server)} & & \text{(Feature Store)}
\end{matrix}$$

### Time Metrics Derived:
1. **Clock Offset**: $\Delta t_{\text{clock}} = T_{\text{sensor}} - T_{\text{server}}$
2. **Backhaul Transport Latency**: $\Delta t_{\text{latency}} = T_{\text{server}} - T_{\text{gateway}}$
3. **Total Pipeline Ingestion Delay**: $\Delta t_{\text{total}} = T_{\text{processing}} - T_{\text{sensor}}$

---

## 2. Strict Time-Gating Invariants

- **Zero Future Timestamp Tolerance**: Transducers cannot predict future time. Any incoming packet where $T_{\text{sensor}} - T_{\text{server}} > 30.0\text{ seconds}$ is immediately dropped with error code `REJECTED_FUTURE_TIMESTAMP`.
- **Clock Drift Warning Tier**: When $\lvert \Delta t_{\text{clock}} \rvert > 120.0\text{ seconds}$, observation quality degrades to `DEGRADED` with reason `CLOCK_DRIFT`.
- **Raw Timestamp Preservation**: Under no circumstance is a raw packet timestamp modified or overwritten. Normalized UTC timestamps are stored in distinct database columns (`sensor_timestamp_utc` vs `server_received_utc`).

---

## 3. Clock Inversion & Sequence Monotonicity

During gateway or edge sensor restarts, RTC resets can cause sequence or timestamp inversions:
- If a sensor re-initializes sequence numbers ($0$ after $65535$), the validator detects device restart via heartbeat metadata and resets the sequence tracker cleanly without crashing.
- Non-monotonic timestamps ($T_{\text{sensor}, n} < T_{\text{sensor}, n-1}$) within the same device session trip `PACKET_OUT_OF_ORDER` and are routed to forensic analysis.
