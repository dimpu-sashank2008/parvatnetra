# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Field Telemetry Commissioning & Site Acceptance Master Plan

**Document Version**: 1.0.0  
**Phase**: V4.7 Engineering  
**System Status**: BENCH_READY_FIELD_EVIDENCE_PENDING  
**Target Corridor**: `CORR-NH10-SIKKIM-KM48` (NH-10 Rangpo–Singtam Geological Corridor, Sikkim)  
**Safety Classification**: LIFE-CRITICAL GEOTECHNICAL EARLY WARNING  

---

## 1. Commissioning Objective & Guiding Principle

Phase V4.7 establishes the standard operating procedure (SOP) and technical protocol for transitioning in-situ hillslope instrumentation from bench/software verification to operational field readiness.

$$\textbf{BENCH\_ACCEPTED} \ne \textbf{FIELD\_INSTALLED} \ne \textbf{FIELD\_COMMISSIONED}$$

A software simulation or bench hardware-in-the-loop test can establish `BENCH_ACCEPTED`, but never `FIELD_COMMISSIONED`. True field commissioning requires physical installation in the mountain slope, verified GPS surveying, certified downhole calibration, stable consecutive telemetry transmissions, and authorized human sign-off.

---

## 2. Formal 10-Stage Sensor Acceptance Lifecycle

Every sensor follows a strict 10-stage state machine governed by `engine/sensor_acceptance_engine.py`:

```
   [1. PLANNED]
        |  (Delivery note / warehouse receipt)
        v
   [2. RECEIVED]
        |  (Hardware model, manufacturer, non-placeholder serial verified)
        v
   [3. IDENTIFIED]
        |  (NABL / factory calibration certificate reference)
        v
   [4. CALIBRATED]
        |  (18-byte LoRa bench test & CRC16 HIL pass)
        v
   [5. BENCH_ACCEPTED]  <--- CURRENT PILOT STATUS
        |  (Borehole drilling, depth, casing, GPS location evidence)
        v
   [6. INSTALLED]
        |  (LoRa/cable link to edge gateway established)
        v
   [7. CONNECTED]
        |  (>= 10 consecutive valid packets, stable clock, zero CRC errors)
        v
   [8. TELEMETRY_VALIDATED]
        |  (Human authorized inspector credentials sign-off)
        v
   [9. FIELD_COMMISSIONED]
        |  (Operational continuous monitoring)
        v
   [10. MONITORING]
```

---

## 3. Pilot Corridor Gating: `CORR-NH10-SIKKIM-KM48`

For the 5 registered instrument nodes on the NH-10 Rangpo–Singtam corridor:
- **`PIEZO-NH10-KM48-01`**: Stage `BENCH_ACCEPTED`. Physical borehole drilling and piezometer installation at 12m depth pending joint deployment with BRO Project Swastik.
- **`INCL-NH10-KM48-01`**: Stage `BENCH_ACCEPTED`. In-place inclinometer string casing pending borehole grouting.
- **`TILT-NH10-KM48-01`**: Stage `BENCH_ACCEPTED`. Bedrock anchor surface mount pending crown inspection.
- **`RAIN-NH10-KM48-01`**: Stage `BENCH_ACCEPTED`. Surface meteorology mast placement scheduled.
- **`GW-NH10-KM48-01`**: Stage `BENCH_ACCEPTED`. Solar power mast installation scheduled.

Overall Corridor State: **`PHYSICAL_TELEMETRY_PENDING`** (Verdict: `V4_7_BENCH_READY_FIELD_EVIDENCE_PENDING`).
