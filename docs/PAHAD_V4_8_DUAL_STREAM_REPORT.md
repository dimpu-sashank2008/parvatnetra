# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Dual-Stream Architecture, Fail-Closed Degradation & Corroboration Report

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Document Version**: 1.0.0  
**Phase**: V4.8 — Real Physical Corridor Telemetry Ingestion & Ground-Truth Dataset Pipeline  
**Operational Status**: `DEGRADED_SYNOPTIC_ONLY` (Stream A Operational, Stream B Pending Deployment)  
**Authoritative Weights**: `models/pahad_lstm_v3_weights.pt` (`7cb823888646ca2b...`)  
**Test Suite**: `tests/test_v4_8_dual_stream.py`  

---

## 1. Dual-Stream Structural Decoupling

PARVAT NETRA enforces clean structural decoupling between regional meteorological modeling (Stream A) and localized hillslope kinematics (Stream B):

| Operational Stream | Input Sources | Time Horizons | Active Model | Current Status |
| :--- | :--- | :--- | :--- | :--- |
| **Stream A: Synoptic Regional** | IMD Radar, Satellite GPM, Infinite Slope FoS, Sentinel-1 InSAR, CWC Teesta Gauge | 24h, 48h, 72h, 168h | Production V3 (`7cb8...`) | **`AVAILABLE`** |
| **Stream B: In-Situ Kinematic** | Vibrating-Wire Piezometers, MEMS Inclinometers, Biaxial Tiltmeters, Tipping Buckets | 0h, 15m, 1h, 3h, 6h | `NOT_TRAINED_DATA_PENDING` | **`UNAVAILABLE`** |

---

## 2. Fail-Closed Degradation Governance

When in-situ sensor telemetry is missing, offline, or awaiting borehole installation:
1. **Never "Safe" by Omission**: An absence of telemetry from a high-risk slope cannot be interpreted as "Zero Risk" or "Stable". The platform reports:
   $$\text{Stream B Status: } \textbf{UNAVAILABLE} \quad (\text{Reason: } \text{PHYSICAL\_TELEMETRY\_PENDING})$$
2. **Graceful Synoptic Fallback**: Operational decisions rely exclusively on Stream A regional physics and satellite evidence under status `DEGRADED_SYNOPTIC_ONLY`.
3. **Neutral CRI Weighting**: Kinematic terms in the Composite Risk Index (CRI) are mathematically neutralized to prevent distorted risk calculations.

---

## 3. Human Authorization & Multi-Modal Corroboration

- **2-of-3 Rule**: Level 3 (RED) alerts require corroboration from at least two independent physical channels (e.g. IMD precipitation breach + Sentinel-1 deformation, or InSAR + River hydrometry).
- **No Autonomous Emergency Broadcasting**: Public sirens, CAP XML feeds, SMS, and SACHET broadcasts are locked in dry-run mode (`ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`).
- Human authority authorization by District Magistrate or BRO Swastik commander is mandatory before any public warning action.
