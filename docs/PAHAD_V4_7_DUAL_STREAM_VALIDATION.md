# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Dual-Stream Architecture & Fail-Closed Safety Validation Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.7 — Sensor Hardware Acceptance & Calibration Traceability  
**Dual-Stream State**: `DEGRADED_SYNOPTIC_ONLY` (Stream A Operational, Stream B Pending Telemetry)  
**Authoritative Ledger**: `reports/pahad_v4_7_result.json`  

---

## 1. The Dual-Stream Early Warning Architecture

PARVAT NETRA decouples hillslope hazard intelligence into two complementary temporal-spatial streams:

```
                            ┌──────────────────────────────────────────────┐
                            │               PARVAT NETRA                   │
                            │       Multi-Modal Evidence Fusion            │
                            └──────────────────────┬───────────────────────┘
                                                   │
                 ┌─────────────────────────────────┴─────────────────────────────────┐
                 │                                                                   │
                 ▼                                                                   ▼
   ┌───────────────────────────┐                                       ┌───────────────────────────┐
   │         STREAM A          │                                       │         STREAM B          │
   │ Regional Synoptic Model   │                                       │ In-Situ Kinematic Stream  │
   ├───────────────────────────┤                                       ├───────────────────────────┤
   │ • IMD Radar & Rainfall    │                                       │ • Piezometer (Pore Water) │
   │ • Antecedent Precip (API) │                                       │ • Inclinometer (Shear)    │
   │ • Infinite Slope FoS      │                                       │ • Tiltmeter (Deflection)  │
   │ • Sentinel-1 InSAR        │                                       │ • Tipping Bucket Gauge    │
   │ • CWC River Hydrometry    │                                       │                           │
   │ Horizons: 24h/48h/72h/168h│                                       │ Horizons: 15m/1h/3h/6h    │
   │ Model: Production V3      │                                       │ Model: NOT_TRAINED        │
   │ STATUS: AVAILABLE         │                                       │ STATUS: UNAVAILABLE       │
   └───────────────────────────┘                                       └───────────────────────────┘
```

---

## 2. Cryptographic Isolation of Production Model V3

Production Model V3 weights (`models/pahad_lstm_v3_weights.pt`) govern Stream A regional forecasts:
- **Canonical SHA-256**: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`
- **Immutability Verification**: Bit-for-bit identical before and after all Phase V4.7 operations.
- **Research Isolation**: Experimental model V4.5 (`31e16ce0...`) remains strictly offline in `models/` with zero production routing.

---

## 3. Fail-Closed Graceful Degradation Protocol

When Stream B in-situ telemetry is missing or degraded (as in the current phase where physical field deployment is pending):
1. **Zero Blocker on Stream A**: Stream A continues to deliver regional landslide susceptibility, Factor of Safety (FoS) assessments, and synoptic weather risk without interruption.
2. **Deterministic Provenance Badging**: All corridor UI cards and API responses display explicit provenance badges:
   - Regional Weather & FoS: `[LIVE]` / `[DETERMINISTIC_PHYSICS]`
   - Corridor In-Situ Telemetry: `[PHYSICAL_TELEMETRY_PENDING]`
3. **No Synthetic Masquerading**: No mock sensor data is injected into operational risk calculations.
4. **Composite CRI Preservation**: In-situ kinematic terms receive a mathematically neutral zero weighting, ensuring the Composite Risk Index (CRI) reflects true regional physics rather than hallucinations.

---

## 4. Public Alert Safety & The 2-of-3 Corroboration Rule

Autonomous alarm activation is strictly prohibited. To generate an operational Level 3 (RED) evacuation recommendation, the platform enforces:
- **2-of-3 Corroboration**: Evidence must converge across at least two independent modalities (e.g., IMD extreme rainfall threshold breach + InSAR ground velocity acceleration, or InSAR + field geotechnical piezometer threshold).
- **Mandatory Human Authority Authorization**: Dispatches require sign-off by the designated District Disaster Management Authority (DDMA) or BRO swastik commander with a cryptographic token.
- **Localhost Isolation**: Public dispatch channels (CAP XML feeds, SMS gateways, sirens, SACHET) are permanently locked in dry-run mode (`ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`).
