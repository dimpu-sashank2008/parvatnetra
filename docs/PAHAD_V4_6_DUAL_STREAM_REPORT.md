# PARVAT NETRA / PAHAD AI — PHASE V4.6
# Dual-Stream Inference Architecture & Operational Synthesis Report

**Document Version**: 1.0.0  
**Service Implementation**: `engine/dual_stream_fusion.py`  
**API Endpoint**: `GET /api/pahad/dual-stream-status`  
**Test Suite**: `tests/test_v4_6_dual_stream.py`  

---

## 1. The Core Invariant: Decoupled Streams

The central architectural rule of Phase V4.6 is that **Stream A (Regional Synoptic)** and **Stream B (Site Kinematic)** are decoupled and exposed side-by-side as distinct operational intelligence layers.

### Why Blending Streams into a Single Scalar Score is Dangerous

In traditional civil defense systems, engineers often average or multiply regional weather indices and local sensor alarms into a single "risk index" (e.g., $0-100$). In landslide engineering, this creates deadly failure modes:
1. **False Masking (Sensor Blindness)**: If localized pore water pressure spikes violently to critical levels ($42\text{ kPa}$) during a localized convective cloudburst that missed the regional radar/satellite grid, a blended score diluted by a "low regional forecast" would suppress the evacuation alarm.
2. **False Confidence (Absence of Telemetry Fallacy)**: If physical sensors have not yet been installed or are offline, setting the kinematic term to $0$ artificially lowers the overall risk score, misleading district magistrates into believing the slope is secure.

By enforcing the Decoupled Dual-Stream pattern, PARVAT NETRA presents each stream in its native horizon and engineering units:

| Dimension | Stream A: Synoptic / Regional | Stream B: Site-Specific Kinematic |
| :--- | :--- | :--- |
| **Forecasting Horizons** | 24h, 48h, 72h, 168h | 0h, 1h, 3h, 6h |
| **Physical Scope** | Basin / Highway Corridor ($10\text{ km} - 50\text{ km}$) | Localized Hillslope Section ($50\text{ m} - 500\text{ m}$) |
| **Governing Physics** | Precipitation accumulations, FoS, seismicity | Pore water pressure, shear strain, tilt acceleration |
| **Data Sources** | IMD gridded rainfall, ERA5-Land, SRTM, NCS | Vibrating wire piezometers, IPIs, tiltmeters, rain gauges |
| **Model Type** | GBDT / Logistic / V4.5 Research Sentinel | High-frequency kinematic trigger rules |
| **Operational Output**| Corridor Watch / Transit Corridor Advisory | Immediate Traffic Halting / Site Inspection Dispatch |

---

## 2. Synthesis & Composite Assessment Matrix

The `DualStreamFusionEngine` assesses the combined operational picture according to the following decision matrix:

| Stream A State (Regional) | Stream B State (Kinematic) | Platform Assessment Mode | Operational Action | System Confidence |
| :--- | :--- | :--- | :--- | :--- |
| Any Level | `UNAVAILABLE` (`PHYSICAL_TELEMETRY_PENDING`) | `REGIONAL_ONLY_MONITORING` | Follow Stream A advisory; schedule ground patrols | `MEDIUM_DEGRADED` (0.50) |
| `NORMAL` | `KINEMATIC_NORMAL` | `DUAL_STREAM_ACTIVE` | Standard highway traffic; continuous logging | `HIGH` (0.90) |
| `ELEVATED` | `KINEMATIC_NORMAL` | `DUAL_STREAM_ACTIVE` | Heightened regional watch; sensors confirm stability | `HIGH` (0.88) |
| `NORMAL` / `ELEVATED` | `KINEMATIC_WATCH` | `DUAL_STREAM_ACTIVE` | Alert patrol unit; increase sensor polling to 1-min | `HIGH` (0.88) |
| Any Level | `KINEMATIC_ELEVATED` | `DUAL_STREAM_ACTIVE` | Mobilize BRO quick-response; inspect culverts | `HIGH` (0.85) |
| Any Level | `KINEMATIC_CRITICAL` | `DUAL_STREAM_ACTIVE` | Immediate corridor halt advisory at Singtam & Rangpo | `HIGH` (0.92) |

---

## 3. Pilot Corridor Evaluation: `CORR-NH10-SIKKIM-KM48`

Querying `GET /api/pahad/dual-stream-status?corridor_id=CORR-NH10-SIKKIM-KM48` returns the live production contract:
- **Stream A**: `AVAILABLE`
  - 24h Risk: `MODERATE` ($P=0.35$, rain: $42.0\text{ mm}$)
  - 48h Risk: `ELEVATED` ($P=0.58$, rain: $88.5\text{ mm}$)
  - Geotechnical Factor of Safety: $FoS = 1.18$ (Marginally Stable)
- **Stream B**: `UNAVAILABLE`
  - Reason: `PHYSICAL_TELEMETRY_PENDING`
  - ML Model Status: `NOT_TRAINED_DATA_PENDING`
  - Active Sensors: 0 (Hardware bench tested; slope installation pending)
- **Assessment**:
  - Mode: `REGIONAL_ONLY_MONITORING`
  - Composite Hazard: `ELEVATED_WATCH`
  - System Confidence: `MEDIUM_DEGRADED` (0.50)
  - Public Dispatch: `false` (Human EOC authorization strictly enforced)
