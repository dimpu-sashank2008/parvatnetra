---
name: disaster-lifecycle-ux
description: >-
  Workflows, state transitions, and dual-persona UX specifications for PARVAT NETRA.
  Use when developing Citizen experiences, Authority control rooms, alert dispatch flows,
  or testing the flagship Incident A-17 demonstration scenario.
---

# PARVAT NETRA — Disaster Lifecycle & Persona UX Specification

PARVAT NETRA guides stakeholders through the complete operational continuum:
**Predict → Detect → Explain → Warn → Prioritise → Respond → Recover**

---

## 1. Persona Separation & Primary User Journeys

### Persona A: Citizen Experience (`/citizen`)
Designed for villagers, pilgrims, tourists, and transport drivers on mountain corridors.
- **Priority**: Extreme clarity, offline-first reliability, low cognitive load, multilingual support.
- **Key Modules**:
  1. **Status Banner**: Immediate localized risk indicator (`SAFE`, `WATCH`, `ALERT`, `EVACUATE`).
  2. **Live Risk Map**: Color-coded corridors with nearby shelters and relief camps.
  3. **Safe Navigation Drawer**: Calculates `SAFEST` hazard-aware evacuation routes with real-time detour guidance.
  4. **Hazard Reporting (Crowdsourced SOS)**: Simple 3-tap submission (Category + Photo + Auto-GPS).
  5. **Multilingual AI Assistant**: Audio & text emergency queries in Hindi, English, and regional dialects.

### Persona B: Authority Operations Control Room (`/authority`)
Designed for District Disaster Management Authorities (DDMA), NDRF, SDRF, Police, and PWD/BRO engineers.
- **Priority**: High data density, tactical situational awareness, rapid operational decision-making.
- **Key Modules**:
  1. **Unified Tactical GIS**: Full-screen vector map integrating slope DEM, sensor stations, and road assets.
  2. **Evidence Fusion Panel**: Time-series charts for piezometers, rainfall accumulation, inclinometers, and optical CCTV clips.
  3. **Infrastructure Exposure Ledger**: Instant counts of threatened population, hospitals, bridges, and blocked routes.
  4. **Incident Action Dispatch**: One-click broadcast of regional SMS/App emergency alerts and official road closure directives.
  5. **Recovery Board**: Post-event debris clearance assignments, road restoration timelines, and audit logs.

---

## 2. Flagship Demonstration Scenario: Incident A-17

All platform evaluations center around **Incident A-17** along the NH-58 Chamoli/Joshimath corridor:

```
[Phase 1: WATCH]
Monsoon precipitation accelerates -> Sensor Station S-04 logs 42 mm/h.
Risk score elevates to 38/100. Automated watch advisory generated.

[Phase 2: DETECT & EXPLAIN]
Piezometer PZ-09 logs sudden pore pressure spike (14 -> 46 kPa).
Borehole inclinometer INCL-02 detects 16 mm horizontal displacement.
Physics engine computes FoS = 0.94 (< 1.0). Fused risk score reaches 89/100 (WARNING).
Explainability panel displays: "Primary driver: Pore saturation + shear displacement".

[Phase 3: WARN & PRIORITISE]
Threat level escalates to EVACUATE (Red).
Exposure analysis identifies: 2,400 residents in Village Pipalkoti, 1 Bridge, 4.2 km NH-58.
Authority triggers Emergency Broadcast; Citizen app sounds critical alert banner.

[Phase 4: RESPOND]
Authority marks NH-58 Mile 42-46 as CLOSED.
Citizen Safe Routes engine dynamically recalculates detour via Link Road 4B (Safest Route).
NDRF Unit 7 dispatched to establish cordon.

[Phase 5: RECOVER]
Drone reconnaissance uploads orthomosaic showing 4,200 m³ rock-debris volume.
BRO task ticket #REC-204 created with high priority for earthmoving equipment.
```
