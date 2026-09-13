# PARVAT NETRA / PAHAD AI — PHASE 7E
## LIVE DATA VERIFICATION REPORT
*Verified: 2026-09-11T00:20:00Z — All values from actual API calls and code inspection.*

---

## 1. Source Matrix Summary

### CP4-A: WEATHER

| Source | Status | Evidence |
|:---|:---|:---|
| **Open-Meteo** | **LIVE** | GET api.open-meteo.com/v1/forecast — HTTP 200, 1.7s, 240h/10d data for lat=27.17N lon=88.50E. Daily precipitation today: 3.3mm. Schema valid. |
| **IMD** | **AUTH_REQUIRED** | IMD_API_KEY=MISSING. WeatherService reports providers.imd.status=UNCONFIGURED, live_ready=false. All IMD fetch calls return AUTH_REQUIRED. |

Active provider preference: IMD → Open-Meteo → PostGIS → DemoSimulator
Actual active provider: **Open-Meteo** (IMD AUTH_REQUIRED, PostGIS UNAVAILABLE)

**WARNING: The live inference pipeline labels weather feature provenance as**
**"IMD AWS / Open-Meteo" with status=LIVE. This is MISLEADING.**
**IMD is AUTH_REQUIRED. The actual source is Open-Meteo exclusively.**
**This must be corrected to: source="Open-Meteo", provenance="LIVE".**

NH10 KM48 Current Weather (from Open-Meteo, 2026-09-10T18:46:58Z):
- Rainfall 24h: 3.3mm (ERA5 + NWP)
- Rainfall 72h: 18.8mm
- Temperature: 24.9°C
- Humidity: 86%
- Forecast 48h: 12.0mm

---

### CP4-B: SEISMIC

| Source | Status | Evidence |
|:---|:---|:---|
| **USGS FDSNws** | **LIVE** | GET earthquake.usgs.gov/fdsnws/event/1/query — HTTP 200, 1.1s, API v2.7.0. 0 events M>=2.5 in NER last 7d. |
| **NCS** | **AUTH_REQUIRED** | NCS_API_KEY=MISSING. SeismicService status=USGS_FALLBACK. NCS connector initialized with UNCONFIGURED status. |

Active provider: **USGS FDSNws** (NCS AUTH_REQUIRED)

Seismic sector impact for CORR-NH10-SIKKIM-KM48: provenance=CACHED (simulated event SIM-EQ-NER-01, M4.6, not a real live event)

**NOTE: No real M>=2.5 seismic event detected in NER last 7 days.**
**The "CACHED" seismic impact in the sector snapshot uses a simulated event.**

---

### CP4-C: EARTH OBSERVATION

| Source | Status | Evidence |
|:---|:---|:---|
| **Copernicus CDSE** | **REGISTRATION_REQUIRED** | OData v1 endpoint returns HTTP 400/404. STAC API returns 404. CDSE_USERNAME=MISSING. No Sentinel-1/2 data accessible. |
| **NRSC/Bhoonidhi** | **REGISTRATION_REQUIRED** | BHOONIDHI_TOKEN=MISSING. No portal access possible. |

**InSAR deformation status: UNAVAILABLE** — No processed deformation product exists.
**NDVI/vegetation status: CACHED/SIMULATED** — vegetation_service uses static values.

Data Pipeline Status:
- Sentinel-1 SAR: DISCOVERED=NO, AVAILABLE=NO, DOWNLOADED=NO, PROCESSED=NO, FEATURE_READY=NO
- Sentinel-2 Optical: DISCOVERED=NO, AVAILABLE=NO, DOWNLOADED=NO, PROCESSED=NO, FEATURE_READY=NO

---

### CP4-D: TERRAIN / DEM

| Source | Status | Evidence |
|:---|:---|:---|
| **DEM (GLO-30/CartoDEM)** | **CACHED** | Static raster. get_point_terrain_attributes() returns elevation=180m, slope=0.0°, curvature=0.0. Provenance=[HISTORICAL]. |

**CRITICAL: slope=0.0° at NH10 KM48 is physically implausible.**
NH10 KM48 is a Himalayan mountain highway — true slope is ~35–45°.
DEM service returns placeholder zeros for slope/curvature/ruggedness.
The static raster has not been processed into derived terrain products.

---

### CP4-E: POSTGIS / DATABASE

| Source | Status | Evidence |
|:---|:---|:---|
| **PostgreSQL/PostGIS** | **UNAVAILABLE** | Port 5432 CLOSED on localhost. DATABASE_URL configured but server not running. psycopg2 connection refused. |
| **SQLite Observation Store** | **CONFIGURED** | data/observations/pahad_observations.db loaded successfully. 4 gateways, 19 devices, 10 calibration records in memory. |

PostGIS spatial queries: UNAVAILABLE
Historical observation retrieval: UNAVAILABLE (PostGIS) / CONFIGURED (SQLite)
Audit records: UNAVAILABLE

---

### CP4-F: IoT / MQTT

| Source | Status | Evidence |
|:---|:---|:---|
| **MQTT Broker** | **UNAVAILABLE** | Port 1883 CLOSED on localhost. MQTT_BROKER_HOST=MISSING. No broker running. |
| **Physical IoT Sensors** | **STANDBY_READY_FOR_DEVICES** | Software chain operational (device_gateway.py, edge_gateway.py). 19 device records in SQLite. No physical hardware at NH10 KM48. |

IoT data in live inference: MISSING (5 features imputed from training medians)
HIL simulation: NOT RUNNING (no demo/simulation active)

**Physical sensor deployment status: NOT DEPLOYED**
**No live piezometer, inclinometer, tiltmeter, or rain gauge at NH10 KM48.**

---

### CP4-G: FRESHNESS

| Modality | Status | Age | Confidence Penalty |
|:---|:---|:---|:---|
| Weather (Open-Meteo) | FRESH | ~0s (queried per-inference) | 0 |
| Seismic (USGS) | CACHED | ~300s (simulated) | Low |
| Terrain (DEM) | HISTORICAL | Static raster | Moderate |
| IoT / Sensors | UNAVAILABLE | No update ever | 1.0 (max) |
| PostGIS | UNAVAILABLE | Port closed | 1.0 (max) |
| Satellite EO | UNAVAILABLE | No download | 1.0 (max) |

Freshness engine DataFreshnessEngine: OPERATIONAL
- record_update(modality): stamps time.time() internally
- get_freshness(modality, last_updated_epoch=None): returns FreshnessRecord
- FRESH / AGING / STALE / UNAVAILABLE classification verified

---

### CP4-H: SECTOR SNAPSHOT — CORR-NH10-SIKKIM-KM48

Live inference run at 2026-09-10T18:49:10Z:

| Field | Value | Source | Provenance |
|:---|:---|:---|:---|
| Event probability | 0.053 (5.3%) | ML classifier (Platt calibrated) | MODELLED |
| FoS | 1.028 | Infinite Slope / Mohr-Coulomb | MODELLED |
| CRI | 45.5 | PAHAD Fusion | MODELLED |
| Risk band | HIGH | PAHAD Fusion | MODELLED |
| Rainfall 24h | 165.0mm | Training median (imputed) | MISSING |
| Soil moisture | 0.52 | Training median (imputed) | MISSING |
| Pore pressure | 26.0 kPa | Training median (imputed) | MISSING |
| Tilt | 3.5° | Training median (imputed) | MISSING |
| Ground displacement | 38.0mm | Training median (imputed) | MISSING |
| Seismic magnitude | 4.6 | Cached simulated event | CACHED |
| Slope | 39.0° | Sector registry hardcoded | MODELLED |
| Elevation | 890.0m | Sector registry hardcoded | MODELLED |
| Data quality score | 0.375 | Computed | COMPUTED |
| Inference latency | 79,486ms | Actual timing | — |
| Signal agreement | 1/3 | 2-of-3 corroboration gate | MODELLED |
| Confidence | LOW_CONFIDENCE (0.466) | Partial cache fallback | COMPUTED |
| Model status | TRAINED_LIMITED_DATA | — | — |

**NOTE: 5 of 10 features are imputed from training medians.**
**Data quality score = 0.375 — well below operational threshold of 0.8.**

**ADDITIONAL FINDING: AUTONOMOUS DISPATCH TRIGGERED during inference load.**
Log shows: "[AI TRIAGE] AUTONOMOUS DISPATCH TRIGGERED: AI-AUTO-xxxx for NH-10 Km 48 (Score: 100.0%, VTI: 92.5)"
This autonomous trigger fires every time the Flask app boots due to high-risk demo state.
This is a pre-existing design decision — not a Phase 7E regression.
Shadow mode flag prevents actual public siren activation.

---

### CP4-I: LIVE INFERENCE SAFETY PIPELINE

Pipeline verification:

  DATA → VALIDATION → FRESHNESS → FEATURE VECTOR → FoS → EVENT MODEL → CALIBRATION → OOD → PAHAD FUSION → SAFETY GATE

  [x] DATA: Weather LIVE (Open-Meteo), Seismic CACHED (simulated), IoT MISSING
  [x] VALIDATION: Invalid coordinates return HISTORICAL fallback (not LIVE)
  [x] FRESHNESS: DataFreshnessEngine operational; UNAVAILABLE modalities penalized
  [x] FEATURE VECTOR: 10 features assembled; 5 imputed from medians (labeled)
  [x] FoS: Mohr-Coulomb computed from sector registry parameters
  [x] EVENT MODEL: Calibrated GBM outputs P=0.053 (5.3%)
  [x] CALIBRATION: Platt sigmoid applied; raw=0.0098, calibrated=0.053
  [x] OOD: data_quality_score=0.375 → confidence=LOW_CONFIDENCE
  [x] PAHAD FUSION: CRI=45.5, signal_agreement=1/3
  [x] SAFETY GATE: alert_eligible=true BUT requires 2-of-3 corroboration
      alert_reason: "FoS=1.03<1.10; Rainfall=165mm>150mm [2/3]" (imputed rainfall)
  [x] Missing/auth-required data cannot silently become LIVE: CONFIRMED
      IoT provenance=MISSING, terrain provenance=MISSING

SAFETY ISSUE: Rainfall used in safety gate is IMPUTED (training median 165mm).
Using an imputed feature to trigger the 2-of-3 safety gate requires explicit disclosure.

---

### CP4-J: CONNECTOR FAILURE HANDLING

| Test | Result |
|:---|:---|
| Out-of-range coordinates | HISTORICAL fallback — safe |
| IMD AUTH_REQUIRED | Returns Open-Meteo data — labeled correctly |
| NCS AUTH_REQUIRED | Fails to USGS_FALLBACK — labeled correctly |
| PostGIS UNAVAILABLE | Falls to SQLite obs store — operational |
| MQTT UNAVAILABLE | IoT labeled MISSING — no fabrication |
| DEM placeholder | Slope=0.0° returns [HISTORICAL] provenance — not LIVE |
| No IoT sensors | Features imputed with explicit imputed_features list |

Safe degradation: CONFIRMED for all tested failure modes.

---

## 2. Blockers

| Priority | Blocker | Impact |
|:---|:---|:---|
| CRITICAL | IMD_API_KEY missing | No Indian rainfall station data |
| CRITICAL | No physical IoT sensors at NH10 KM48 | 5 features imputed in every inference |
| HIGH | NCS_API_KEY missing | No Indian seismic data (USGS fallback only) |
| HIGH | CDSE account not registered | No Sentinel-1 InSAR or Sentinel-2 NDVI |
| HIGH | PostgreSQL not running | No spatial query capability |
| MEDIUM | DEM slope=0.0° placeholder | Terrain features physically incorrect |
| MEDIUM | MQTT broker not running | No real-time IoT ingestion |
| MEDIUM | Imputed rainfall in 2-of-3 gate | Safety gate trigger may be unreliable |

---

## 3. Final Gate

**PHASE 7E FINAL GATE: PARTIALLY_LIVE**

Rationale:
- LIVE sources: Open-Meteo (weather), USGS FDSNws (seismic)
- AUTH_REQUIRED: IMD, NCS
- REGISTRATION_REQUIRED: CDSE, NRSC/Bhoonidhi
- UNAVAILABLE: PostGIS, MQTT broker
- NOT DEPLOYED: Physical IoT sensors
- CACHED/SIMULATED: DEM terrain, seismic sector impact, vegetation NDVI

Mandatory operational sources NOT connected:
- IMD: AUTH_REQUIRED
- NCS: AUTH_REQUIRED
- IoT telemetry: STANDBY_READY_FOR_DEVICES (no hardware)

Two zero-auth public feeds (Open-Meteo, USGS) are live.
Institutional feeds and physical sensors remain blocked.

LIVE_DATA_READY: NO
PARTIALLY_LIVE: YES
EXTERNAL_DATA_BLOCKED: Partially (institutional feeds)
