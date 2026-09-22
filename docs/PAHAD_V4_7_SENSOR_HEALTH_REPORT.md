# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Transducer Health Monitoring, Plausibility Boundaries & Anomaly Detection Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.7 — Sensor Hardware Acceptance & Calibration Traceability  
**Modules**: `engine/telemetry_trust_engine.py`, `services/telemetry_contract.py`  
**Test Suites**: `tests/test_v4_7_hardware_acceptance.py`, `tests/test_v4_7_telemetry_chain.py`  

---

## 1. Transparent Health & Trust Scoring Architecture

PARVAT NETRA strictly rejects opaque "AI confidence scores" for sensor telemetry. Instead, the `TelemetryTrustEngine` calculates a transparent, deterministic composite compliance score ($0-100\%$) and classifies each reading into three distinct trust states:

1. **`VERIFIED`**: Sensor identity authenticated, NABL calibration valid, timestamp synchronized within $30\text{s}$, reading within physical limits, and rate of change normal.
2. **`DEGRADED`**: Telemetry usable with confidence penalties due to non-critical anomalies (e.g., calibration overdue, clock drift $> 120\text{s}$, battery $< 15\%$, or marginal RSSI $< -95\text{ dBm}$).
3. **`UNVERIFIED`**: Telemetry dropped or rejected from safety calculations due to critical failures (e.g., CRC corruption, impossible values, future timestamps, or unverified hardware identity).

---

## 2. Physical Sensor Plausibility Limits

Every incoming reading is strictly checked against physical and geological boundaries established for Himalayan terrain:

| Transducer Type | Physical Parameter | Minimum Bound | Maximum Bound | Engineering Unit | Maximum Rate of Change ($\Delta / \text{h}$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Piezometer** | Pore-water pressure | $-10.0$ | $250.0$ | $\text{kPa}$ | $40.0\text{ kPa/h}$ |
| **Inclinometer** | Shear displacement | $-500.0$ | $500.0$ | $\text{mm}$ | $60.0\text{ mm/h}$ |
| **Tiltmeter** | Biaxial deflection | $-45.0$ | $45.0$ | $\text{deg}$ | $10.0^\circ/\text{h}$ |
| **Soil Moisture** | Volumetric water content | $0.0$ | $1.0$ | $\text{m}^3/\text{m}^3$ | $0.5\text{ m}^3/\text{m}^3/\text{h}$ |
| **Rain Gauge** | Precipitation intensity | $0.0$ | $300.0$ | $\text{mm}$ | $150.0\text{ mm/h}$ |
| **Crack Sensor** | Joint aperture dilation | $0.0$ | $200.0$ | $\text{mm}$ | $30.0\text{ mm/h}$ |

*Any reading outside these bounds is immediately rejected with status `REJECTED_IMPOSSIBLE_VALUE`.*

---

## 3. Sensor Anomaly Detection Mechanisms

1. **Flatline Detection (Frozen Transducer)**:
   If a transducer emits identical values across multiple reporting cycles despite environmental rainfall or barometric fluctuations, variance is computed over an 8-sample rolling window:
   $$\sigma^2 = \frac{1}{N}\sum_{i=1}^N (x_i - \bar{x})^2$$
   If $\sigma^2 = 0.0$ over $> 6\text{ hours}$, status degrades to `DEGRADED` with reason code `FLATLINE_DETECTED`.

2. **Rate-of-Change Spike Anomaly**:
   Transducer delta between consecutive packets is normalized against elapsed time:
   $$\text{Rate} = \frac{|x_t - x_{t-1}|}{\Delta t_{\text{hours}}}$$
   If $\text{Rate} > 3 \times \text{Max Rate}$, quality drops to `DEGRADED` with reason code `NOISE_EXCESS`.

3. **Battery & Link Margin Health**:
   - $\text{Battery} < 15\%$: Flagged as `LOW_BATTERY`, health degraded.
   - $\text{RSSI} < -95\text{ dBm}$: Flagged as `MARGINAL_RF_LINK`, health degraded.
   - Elapsed time $> 900\text{s}$ ($> 15\text{ min}$): Classified as `STALE`.
   - Elapsed time $> 3600\text{s}$ ($> 1\text{ hr}$): Classified as `OFFLINE`.

---

## 4. Corridor Sensor Fleet Baseline

Because physical field deployment is currently pending (`NOT_INSTALLED`), all 5 sensors are held in lab inventory. In the absence of live slope transmissions, the sensor health monitor reports:
- **Corridor Telemetry Status**: `PHYSICAL_TELEMETRY_PENDING`
- **Active Streams**: 0
- **Degraded / Failed Streams**: 0
- **Safety Policy**: Fail-closed (Stream B inactive; system runs exclusively on Stream A regional synoptic intelligence).
