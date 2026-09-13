# PAHAD AI — SIH Presentation Demonstration Scenario Guide

**Scenario Title**: Active Teesta Basin Monsoon Failure Sequence  
**Location**: NH-10 Strategic Himalayan Lifeline Corridor (Km 48 / 29th Mile, Sikkim)  
**Total Steps**: 13 Deterministic Checkpoints  
**Duration**: 2 to 4 Minutes (Configurable: 1x, 2x, FAST)  
**Standard Provenance**: `[DEMO SCENARIO ACTIVE]`  

---

## 1. Scenario Rationale & Design Invariants

Live jury evaluation requires demonstrating the full life-safety cycle of a catastrophic mountain disaster without relying on uncertain live weather or fabricating historical data.

The **Active Teesta Basin Monsoon Failure Sequence** executes a mathematically deterministic progression across the entire early warning lifecycle:
$$\text{Normal Baseline} \longrightarrow \text{Hydrological Loading} \longrightarrow \text{Physical Failure} \longrightarrow \text{Multi-Modal Corroboration} \longrightarrow \text{Evacuation \& Safe Corridor Routing}$$

---

## 2. Detailed Step-by-Step Sequence (13 Checkpoints)

### Step 1: Normal Baseline
- **Telemetry State**: Rainfall: 12.0 mm, Piezometer: 12.4 kPa, Slope: 38.4°, Soil Cohesion: 18 kPa.
- **Physics Calculation**: Mohr-Coulomb Physical FoS = 1.450 (Stable equilibrium).
- **AI Event Model**: 24h P(event) = 11.0%, CRI = 22.0 / 100 (LOW RISK).
- **Signal Concordance**: 0/3 signals active. No warning required.
- **Provenance**: `[DEMO / BASELINE]`

### Step 2: Rain Onset (IMD AWS)
- **Telemetry State**: IMD AWS Mangan logs sudden monsoon downpour of 48.5 mm/h. 24h cumulative rainfall: 48.5 mm.
- **Physics Calculation**: FoS declines to 1.220 as topsoil begins saturation.
- **AI Event Model**: 24h P(event) = 42.0%, CRI = 42.0 / 100 (MODERATE RISK).
- **Signal Concordance**: 1/3 signals active (Rainfall I-D exceeded).
- **Action**: Advisory dispatched to BRO highway patrol.

### Step 3: Cumulative Infiltration & Pore Pressure Rise
- **Telemetry State**: Cumulative infiltration deepens; in-situ vibrating wire piezometer registers 38.4 kPa pore-water pressure.
- **Physics Calculation**: Effective normal stress declines; FoS drops to 1.080 (Marginal stability).
- **AI Event Model**: 24h P(event) = 62.0%, CRI = 58.0 / 100 (ELEVATED RISK).
- **Signal Concordance**: 1/3 signals active (Precipitation threshold).
- **Action**: Pre-position heavy plant equipment at Rangpo staging depot.

### Step 4: FoS Drops Below 1.0 (Limit State Shear Failure)
- **Telemetry State**: Shear stress exceeds shear strength on the basal slip surface.
- **Physics Calculation**: Mohr-Coulomb FoS breaches limit state: **FoS = 0.745 (< 1.0)**.
- **AI Event Model**: CRI climbs to 72.0 / 100 (HIGH RISK).
- **Signal Concordance**: 2/3 signals active (Physical FoS < 1.0 + Rainfall I-D exceeded).
- **Action**: Halt heavy commercial vehicle traffic on NH-10.

### Step 5: AI Event Model Reaches 0.84
- **Telemetry State**: Calibrated Scikit-learn GBDT multi-horizon classifier processes telemetry window.
- **Model Output**: 6h = 78%, 12h = 82%, **24h = 84.2%**, 48h = 88%.
- **Signal Concordance**: All three primary signals now elevated.
- **Action**: Alert Sikkim State EOC and Kalimpong District Disaster Management Authority.

### Step 6: 2-of-3 Signal Agreement Satisfied
- **Constitutional Verification**: 
  1. *Physical Stability*: FoS = 0.745 < 1.0 (CONFIRMED)
  2. *Rainfall Loading*: Mandal-Sarkar I-D curve exceeded (CONFIRMED)
  3. *Statistical AI*: Calibrated GBDT P(event) >= 0.80 (CONFIRMED)
- **Status**: **3 of 3 signals verified** (Threshold is 2-of-3). Zero chance of single-sensor false alarm.
- **Action**: Initiate autonomous emergency alert protocol.

### Step 7: Evacuation Advisory Generated
- **Risk Score**: Composite Risk Index reaches **86.4 / 100** (CRITICAL RED).
- **Policy Escalation**: Autonomous Siren & Evacuation Protocol triggered.
- **Visual Alert**: Persistent RED emergency lockdown order displayed.
- **Action**: "CRITICAL AUTONOMOUS LOCKDOWN ORDER — Mandatory Evacuation within 15 km."

### Step 8: 15 km Spatial Geofence Constructed
- **Spatial Geometry**: Geodesic circle of radius 15.0 km centered on NH-10 Km 48 (27.245° N, 88.512° E).
- **Impact Assessment**: 4,820 residents across 6 revenue settlements identified inside impact perimeter.
- **Action**: Civil defense checkpoints established at Rangpo and Melli border gates.

### Step 9: Multi-Channel Dispatch (Push + SMS + Edge Siren)
- **Web Push**: 1,420 active tokens within geofence notified with audio chime.
- **Mobile Push / SMS**: 1,240 registered subscriber phone numbers messaged in Nepali, Hindi, English.
- **Edge Siren**: LoRa mesh air-raid siren node #EDGE-SK-01 activated at 115 dB.
- **CAP Protocol**: OASIS CAP v1.2 XML payload broadcast to NDMA SACHET gateway.

### Step 10: Dynamic Route Re-Calculation (Safe Corridor Active)
- **Routing Engine**: Dijkstra / A* graph applies maximum traversal penalty (9999) to severed NH-10 Km 48.
- **Safe Diversion Corridor**: Traffic dynamically re-routed via the **NH-717A bypass** (Rhenock - Rongli - Pakyong corridor).
- **Result**: Evacuating convoys safely diverted away from the unstable mountain face.

### Step 11: Field Sensor Corroboration
- **In-Situ Verification**: Borehole inclinometer registers 14.2 mm shear creep displacement.
- **Drone / CCTV Vision**: Computer vision aperture detector measures 4.2 cm tension crack widening.
- **Ground Truth**: Physical slope movement empirically corroborated.

### Step 12: Post-Event Recovery State
- **Field Response**: Border Roads Organisation (BRO Project Swastik) deployment of dozers and excavators.
- **Safety Impact**: **ZERO CASUALTIES**. Early-warning lead time achieved: **42 minutes prior to catastrophic rockfall**.
- **Action**: Debris clearance and geotechnical shotcrete/grouting stabilization underway.

### Step 13: Evaluation Complete
- **Final Status**: `[DEMO COMPLETE: 13/13 VERIFIED]`
- **Verification Summary**: Every stage of the national early warning and life-safety lifecycle demonstrated and verified deterministically.
