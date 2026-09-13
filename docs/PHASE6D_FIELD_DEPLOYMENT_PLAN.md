# PARVAT NETRA / PAHAD AI — PHASE 6D
## Himalayan Corridor Field Deployment Plan

**Document Reference**: `docs/PHASE6D_FIELD_DEPLOYMENT_PLAN.md`  
**Classification**: National Disaster Intelligence / Geotechnical Early Warning  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Current Operational Status**: `FIELD_VALIDATION_READY`  
**Physical State**: `PHYSICAL_DEPLOYMENT_PENDING`  
**Date**: September 2026  

---

## 1. Scope & Strategic Mission

This document defines the deployment engineering plan for instrumenting critical mountain highway and railway corridors across the North-Eastern Region (NER) of India. The primary mission is to deliver real-time physics-informed, AI-fused early warning before catastrophic slope failure and road washouts.

---

## 2. Monitored Corridors Matrix

```
+--------------------------+-----------------------+----------+---------+--------------------+----------------+
| CORRIDOR ID              | NAME                  | STATE    | SLOPE   | RISK RATING        | STATUS         |
+--------------------------+-----------------------+----------+---------+--------------------+----------------+
| CORR-NH10-SIKKIM-KM48    | NH-10 Teesta Gorge    | Sikkim   | 42.5°   | CRITICAL           | APPROVED       |
| CORR-TUPUL-MANIPUR-RLY   | Tupul Railway Section | Manipur  | 48.0°   | CRITICAL           | APPROVED       |
| CORR-MELTHUM-MIZORAM     | Melthum Quarry Scarp  | Mizoram  | 46.2°   | HIGH               | APPROVED       |
| CORR-NH717A-PEDONG-RISSI | NH-717A Bypass        | W.Bengal | 38.0°   | HIGH               | SURVEYED       |
| CORR-DIMA-HASAO-ASSAM    | Lumding-Badarpur Line | Assam    | 41.0°   | HIGH               | SURVEYED       |
+--------------------------+-----------------------+----------+---------+--------------------+----------------+
```

---

## 3. Instrumentation Package Specification

### 3.1 Transducer Allocation per Site
- **Toe/Colluvium Zone**: Vibrating-wire piezometer (Geokon 4500S, 0–500 kPa) installed in vertical borehole below seasonal water table.
- **Shear Plane Slip Horizon**: In-place MEMS borehole inclinometer string (RST Instruments, ±30° range, 0.001° resolution).
- **Surface Retaining Structure / Scarp**: Biaxial surface tiltmeter (0–15° deflection) and joint crack extensometer (0–100 mm dilation).
- **Corridor Met Mast**: Tipping bucket rain gauge (0.2 mm/tip) with integrated solar insolation sensor.

### 3.2 Power & Autonomy Budget
- **Battery**: 12.8V 20Ah LiFePO4 pack with integrated BMS.
- **Solar PV Array**: 40W monocrystalline panel, angled at 35° South.
- **Average Current Draw**: 42–48 mA nominal, 120 mA transmit burst.
- **Autonomous Reserve**: Minimum 5.0 days operation with 0% solar insolation (monsoon overcast).

---

## 4. Edge Concentrator Gateway Topology

- **Hardware Base**: Raspberry Pi Compute Module 4 + SX1302 8-channel LoRaWAN concentrator HAT.
- **RF Spectrum**: 868.1 MHz (IN865 / EU868 standard), Spreading Factor SF9, 125 kHz BW.
- **Backhaul Channels**: Primary 4G/5G LTE cellular; secondary BSNL/RailTel OFC; fallback Iridium satellite link.
- **Edge Storage**: SQLite circular ring buffer with 100,000-record capacity for offline buffering during fiber/cellular severances.

---

## 5. Non-Negotiable Safety Invariants

1. **Zero Fabrication**: In the absence of real borehole sensors anchored in Himalayan rock, status remains strictly `PHYSICAL_DEPLOYMENT_PENDING`.
2. **Provenance Honesty**: Telemetry generated on bench simulators is stamped `[SIMULATED]`. Topographic Fresnel calculations are labeled `ESTIMATED`.
3. **Public Siren Safety**: On-site 110 dB corridor acoustic horns are disarmed during deployment validation under `DRY_RUN` mode. Physical sounding requires HMAC authorization token and `SIREN_HARDWARE_ENABLED=1`.
4. **Field Shadow Operations**: Live corridor data streams into `FIELD_SHADOW_ACTIVE` mode, logging FoS, event probability, and CRI without dispatching public sirens or CAP alerts.
