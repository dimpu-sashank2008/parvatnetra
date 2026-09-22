# PARVAT NETRA / PAHAD AI — PHASE V5.2
## SENSOR INSTALLATION & 7-STAGE LIFECYCLE GOVERNANCE REPORT

**Corridor**: CORR-NH10-SIKKIM-KM48 (NH-10 Rangpo–Singtam, Sikkim, KM 48.2)  
**Authority**: PARVAT NETRA Metrology & Quality Assurance Directorate  
**Date**: September 2026  
**Verdict**: `V5_2_PHYSICAL_DEPLOYMENT_PENDING`  
**Classification**: `OFFICIAL USE ONLY / LOCALHOST AUDIT`  

---

### 1. Canonical 7-Stage Sensor Status Matrix
The PARVAT NETRA system governs hardware progression strictly through a sequential, non-skippable 7-stage lifecycle state machine:

```
[1. PLANNED]
     │ (Hardware Receipt + Nameplate Verification)
     ▼
[2. BENCH_ACCEPTED]
     │ (Bench Testing + Physical Handover to Field Crew)
     ▼
[3. PHYSICAL_VERIFIED]
     │ (Borehole Drilling / Surface Anchor Installation)
     ▼
[4. INSTALLATION_VERIFIED]
     │ (Wiring Continuity, LoRa Link SNR Check, Checklist)
     ▼
[5. COMMISSIONING_PENDING]
     │ (BRO / SSDMA Engineering Sign-off + Local Concentrator Sync)
     ▼
[6. FIELD_COMMISSIONED]
     │ (72-Hour Continuous Burn-in + QC Baseline Verification)
     ▼
[7. LIVE_MONITORING]
```

### 2. Stage Skipping Rules
1. **Direct Transitions Forbidden**: Transitioning directly from `PLANNED` or `BENCH_ACCEPTED` to `LIVE_MONITORING` or `FIELD_COMMISSIONED` is cryptographically and logically rejected by `PhysicalDeploymentEngine.validate_stage_transition()`.
2. **Mandatory Prerequisite Check**: Advancing to `INSTALLATION_VERIFIED` strictly requires documented borehole drilling logs and verified installation depths for downhole instruments (`PIEZOMETER`, `INCLINOMETER`).

### 3. Current Site Status Matrix

| Sensor ID | Sensor Type | Target Depth (m) | Current Stage | Installation Status | Next Required Evidence Gate |
|---|---|---|---|---|---|
| `PIEZO-NH10-KM48-01` | Piezometer | 12.0m | `BENCH_ACCEPTED` | `NOT_INSTALLED` | Nameplate photo + Challan (`PHYSICAL_VERIFIED`) |
| `INCL-NH10-KM48-01` | Inclinometer | 15.0m | `BENCH_ACCEPTED` | `NOT_INSTALLED` | Nameplate photo + Challan (`PHYSICAL_VERIFIED`) |
| `TILT-NH10-KM48-01` | Tiltmeter | 0.0m (Surface) | `BENCH_ACCEPTED` | `NOT_INSTALLED` | Nameplate photo + Challan (`PHYSICAL_VERIFIED`) |
| `RAIN-NH10-KM48-01` | Rain Gauge | 0.0m (Surface) | `BENCH_ACCEPTED` | `NOT_INSTALLED` | Nameplate photo + Challan (`PHYSICAL_VERIFIED`) |
| `GW-NH10-KM48-01` | LoRa Gateway | Mast Mount | `BENCH_ACCEPTED` | `NOT_INSTALLED` | Mast photo + Power telemetry (`PHYSICAL_VERIFIED`) |

### 4. Summary Findings
- **Sensors Marked Installed**: 0
- **Sensors In Active Ground Monitoring**: 0
- **Overall Corridor Installation Status**: `PHYSICAL_DEPLOYMENT_PENDING`
