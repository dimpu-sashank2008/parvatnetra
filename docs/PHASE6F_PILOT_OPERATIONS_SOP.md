# PARVAT NETRA / PAHAD AI — PHASE 6F
## Controlled Supervised Pilot Standard Operating Procedure (SOP)

**Document ID**: `PAHAD-SOP-6F-01`  
**Classification**: National Landslide Early Warning System Operational Doctrine  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Corridor**: Primary: `CORR-NH10-SIKKIM-KM48` (Pakyong District, Sikkim / Project Swastik BRO)  
**Effective Date**: September 2026  
**Operational Mode**: `SUPERVISED_PILOT` / `SHADOW`  
**Primary Invariant**: $\mathbf{AI\ recommendation \ne public\ emergency\ alert}$  

---

## 1. System Activation & Initialization

### 1.1 Pre-Activation Verification
Before activating the platform for a supervised operational shift:
1. Ensure the server environment is booted:
   ```bash
   python -m app
   ```
2. Verify system health and operational readiness via REST API:
   ```bash
   curl -s http://localhost:8080/api/health
   curl -s http://localhost:8080/api/pahad/data-status
   curl -s http://localhost:8080/api/pahad/event-model/status
   ```
3. Inspect active pilot profile and mode:
   - Confirm mode is strictly `SHADOW` or `SUPERVISED_PILOT`.
   - Confirm `PUBLIC_DISPATCH = DISABLED`.
   - Confirm corridor sirens are configured in `DRY_RUN`.

### 1.2 Multi-Modal Telemetry Check
- Confirm Open-Meteo REST API fallback is streaming current precipitation (`[LIVE / OPEN_METEO]`).
- Confirm USGS seismic API is active for the Himalayan bounding box (`[LIVE / USGS]`).
- Confirm static GLO-30 DEM elevation and slope rasters are loaded (`[CACHED]`).
- Inspect IoT Gateway status (`services/edge_gateway.py`). In the absence of physical slope sensors, confirm telemetry status is `PHYSICAL_DEPLOYMENT_PENDING`.

---

## 2. Continuous Monitoring Regime

### 2.1 Shift Monitoring Schedule
- **Monsoon Season (June 1 – October 15)**: 24/7 continuous operations with 8-hour duty rotations.
- **Pre-Monsoon / Dry Season**: Daily 12-hour monitoring shifts with automated SMS/Telegram paging for trigger exceedance.

### 2.2 Routine Telemetry Observation
Operators must monitor the live dashboard and logs:
- **Precipitation Intensity**: Alert if $R_{1h} \ge 25.0\text{ mm}$ or $R_{24h} \ge 100.0\text{ mm}$.
- **Geotechnical Limit Equilibrium**: Monitor real-time Factor of Safety ($FoS$). Normal: $FoS \ge 1.30$; Marginal: $1.10 \le FoS < 1.30$; Critical: $FoS < 1.10$.
- **Data Freshness**: Verify that data freshness engine indicates `FRESH` ($\le 15\text{ min}$ for weather, $\le 5\text{ min}$ for seismic). If freshness degrades to `STALE`, investigate network uplinks.

---

## 3. Anomaly Detection & AI Review

### 3.1 Trigger Condition
An anomaly is triggered when any of the following occur:
1. Physical Mohr-Coulomb Factor of Safety drops below critical threshold ($FoS < 1.10$).
2. Precipitation exceeds Mandal-Sarkar regional trigger ($R_{24h} \ge 150.0\text{ mm}$).
3. Calibrated GBDT Event Classifier predicts high probability ($P(\text{event}_{24h}) \ge 0.70$).
4. IoT inclinometer/tilt rate exceeds $0.05^\circ/\text{hour}$ or pore pressure spikes $> 45\text{ kPa}$.

### 3.2 State Transition: `MONITORING` $\to$ `ANOMALY_DETECTED` $\to$ `PAHAD_EVALUATING`
- The system automatically creates a candidate incident record.
- The `PAHADLiveInference` engine computes multi-horizon predictions (6h, 12h, 24h, 48h).
- The `CorroborationEngine` evaluates whether $\ge 2$ independent evidence groups corroborate the hazard.

---

## 4. Multi-Source Corroboration (2-of-3 Rule)

### 4.1 Independent Modality Groups
Before an alert can escalate to `AUTHORITY_REVIEW`, at least two distinct modality groups must confirm the destabilization signal:
- **Group 1 (Physical Mechanics)**: $FoS < 1.10$ based on infinite-slope mechanics.
- **Group 2 (Hydrometeorology)**: Real-time rainfall or antecedent moisture exceeding regional saturation thresholds.
- **Group 3 (Empirical ML Classifier)**: Calibrated GBDT event probability $P(\text{event}) \ge 0.70$.
- **Group 4 (Telemetry Spikes)**: In-situ borehole tilt or pore-pressure acceleration.
- **Group 5 (Earth Observation)**: InSAR LOS velocity $\ge 15\text{ mm/year}$ or acute NDVI loss.
- **Group 6 (Field Human Intelligence)**: Verified citizen or BRO field scarp reports.

### 4.2 Single Signal Interlock
If only one modality triggers (e.g. rain spike without slope stress, or model anomaly on dry slope):
- The event is tagged `CORROBORATION_FAILED`.
- The hazard is classified as an **Advisory (YELLOW)**.
- Public dispatch remains locked; notifications are restricted to operator inspection.

---

## 5. Field Verification Workflow

### 5.1 Tactical Patrol Dispatch
When an anomaly achieves 2-of-3 corroboration:
1. The operations desk automatically dispatches a field verification task to the nearest Border Roads Organisation (BRO Swastik) or SDRF patrol unit via the mobile app.
2. Patrol inspects candidate scarp locations:
   - Crown tension cracks: measure aperture ($> 10\text{ mm}$ indicates imminent shear).
   - Toe seepage or muddy water discharge from slope face.
   - Retaining wall bulging or road pavement offset.
3. Patrol uploads geotagged photo evidence with GPS accuracy $\le 25\text{ m}$ using the offline-capable Flutter field app.

---

## 6. Authority Review & Sign-Off

### 6.1 Strict Invariant
$$\mathbf{AI\ recommendation \ne public\ emergency\ alert}$$
Under no circumstances may the AI engine trigger sirens, block highways, or issue public evacuation alerts autonomously.

### 6.2 Authority Queue Inspection
1. The designated Authority Officer (District Disaster Management Officer / Sub-Divisional Magistrate / BRO Task Force Commander) logs into the Authority Portal.
2. The review interface displays:
   - The Composite Risk Index (CRI) and Factor of Safety ($FoS$).
   - The Calibrated Event Probability ($P(\text{event})$).
   - The 2-of-3 Corroboration Breakdown ("Why" explainability matrix).
   - Real-time field inspection photos and patrol notes.
   - Dynamic polygon geofence depicting the hazard footprint.
3. Authority Action:
   - **APPROVE**: Enter authenticated digital PIN / HMAC token to authorize public warning.
   - **REJECT**: Document reason (e.g. controlled excavation, blasting false positive) $\to$ State transitions to `REJECTED_FALSE_ALARM`.
   - **REQUEST MORE EVIDENCE**: Re-dispatch patrol for secondary inspection.

---

## 7. Warning Generation & Dynamic Geofencing

### 7.1 Hazard Polygon Delineation
- Dynamic geofence polygon is generated based on slope geometry, digital elevation flowlines, and predicted runout runout length ($L = H / \tan 32^\circ$).
- Buffer of $500\text{ m}$ is automatically applied along the affected highway corridor (`SK-NH10-KM48`).

### 7.2 OASIS CAP v1.2 Payload Formulation
- The warning payload is assembled in international standard Common Alerting Protocol (CAP v1.2) XML and JSON schemas.
- Mandatory fields:
  - `identifier`: Unique disaster serial (e.g. `IN-SK-2026-NH10-001`).
  - `sender`: Authenticated Sikkim SDMA / DDMA credential.
  - `status`: `Actual` (or `Draft` / `Test` during pilot).
  - `msgType`: `Alert` (or `Update` / `Cancel`).
  - `urgency`: `Immediate` | `severity`: `Severe` or `Extreme`.
  - `areaDesc`: "NH-10 Km 48, Pakyong District, Teesta River Corridor".
  - `polygon`: Exact coordinate boundary.

---

## 8. Notification & Dispatch Protocols

### 8.1 Pilot Mode Guardrails
- In `SHADOW` or `SUPERVISED_PILOT` mode:
  - Public cell broadcast is **STRICTLY SUPPRESSED**.
  - Notifications are dispatched only to:
    1. Incident Command Post dashboard.
    2. SDRF / NDRF quick response teams.
    3. BRO highway patrol units.
    4. Local police control room.

### 8.2 Acoustic Corridor Siren Protocol
- Sirens operate in `DRY_RUN` mode by default.
- Physical siren activation during field drills requires:
  1. `SIREN_HARDWARE_ENABLED = 1` in environment.
  2. Physical test authorization token with duration hard-capped at $5.0\text{ seconds}$.
  3. Pre-announcement to local communities to avoid panic.

---

## 9. Field Tactical Response & Evacuation Routing

### 9.1 Emergency Traffic Diversion
1. BRO Swastik checkpoints at Rangpo and Singtam divert heavy vehicle traffic to alternate strategic corridor `NH-717A` (Pedong – Rhenock – Pakyong bypass).
2. The `SafeRoutesEngine` updates road graphs dynamically to calculate the **SAFEST** hazard-free evacuation corridors without reloading the client map.

### 9.2 Staging & Relief Deployment
- Pre-designated NDRF search and rescue staging areas:
  - Staging Point A: Singtam Ground.
  - Staging Point B: Pakyong Airport Helipad.

---

## 10. Timeout Escalation Engine

### 10.1 SLA Thresholds
- **Critical Anomaly Review SLA**: $15\text{ minutes}$.
- If an authority officer does not review a critical corroboration within $15\text{ minutes}$:
  - The `TimeoutEscalationService` triggers automated escalation.
  - SMS and priority push notifications are dispatched to the Secondary Approver (State Relief Commissioner / SDMA Director).
  - Event log is tagged: `ESCALATED_TIMEOUT`.

---

## 11. Incident Resolution & Demobilization

### 11.1 De-Escalation Criteria
An incident transitions to `RESOLVED` and `CLOSED` only when:
1. Precipitation intensity ceases ($R_{24h} < 20\text{ mm}$ for 24 continuous hours).
2. Geotechnical Factor of Safety recovers to stable equilibrium ($FoS \ge 1.30$).
3. Borehole displacement and tilt rates return to baseline ($< 0.005^\circ/\text{day}$).
4. Physical geotechnical inspection by BRO engineers certifies the carriageway safe for traffic.

### 11.2 Public Cancellation Broadcast
- An official CAP v1.2 `Cancel` message is dispatched to all notification channels.
- Highway status on the public map transitions back to `OPEN / NORMAL`.

---

## 12. Emergency Rollback Protocol

### 12.1 Purpose & Triggers
The emergency rollback procedure provides immediate manual de-escalation in the event of:
- Malfunctioning sensor generating runaway false alerts.
- Network packet corruption triggering bogus corroboration.
- Accidental trigger during non-emergency maintenance.

### 12.2 Execution Steps
1. The duty officer executes the rollback CLI or API:
   ```bash
   python -c "from engine.pilot_profile import PILOT_MANAGER; print(PILOT_MANAGER.execute_emergency_rollback('SK-NH10-KM48', 'op-duty', 'Sensor fault rollback', 'AUTH-TOKEN-REVOKE-9999'))"
   ```
2. The rollback engine immediately executes:
   - `PUBLIC_DISPATCH_FORCED_DISABLED`
   - `SIREN_HARDWARE_DEACTIVATED_DRY_RUN`
   - `ACTIVE_ALERTS_CANCELLED`
   - `CORRIDOR_STATE_RESET_TO_MONITORING`
3. All actions are immutably logged in `pahad_observations.db` with an SHA-256 audit record.

---

## 13. False Alarm Review & Post-Event Analysis

### 13.1 False Alarm Debriefing
- Within 24 hours of any false alarm or manual rollback, the technical team must convene a debriefing session.
- Document:
  1. Triggering transducer or telemetry stream.
  2. Why the 2-of-3 corroboration engine triggered.
  3. Failure mode (sensor drift, lightning transient, wildlife disturbance, cable breach).
  4. Corrective actions (recalibrate transducer, adjust threshold, blacklist noisy channel).

### 13.2 Post-Event Scientific Analysis
- For all actual slope movements:
  1. Archive all raw 1-minute telemetry in `data/raw/` for model training.
  2. Compute warning lead time (Time of First Prediction $\to$ Time of Failure).
  3. Update Geological Survey of India (GSI) event inventory.
