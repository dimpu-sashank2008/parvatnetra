# PARVAT NETRA / PAHAD AI — Project Handoff Document
**Prepared for**: Google Antigravity Agent Migration  
**Problem Statement**: SIH 26001  
**Last Updated**: 2026-09-09  
**Status**: Phase 3.4 Complete — Ready for Phase 4+

---

## 1. Project Identity (Binding — Do Not Rename)

| Attribute | Value |
|---|---|
| **Platform Name** | **PARVAT NETRA** (the web platform, dashboard, and API) |
| **AI Engine Name** | **PAHAD** (the risk analysis & prediction AI inside the platform) |
| **PAHAD Full Form** | Predictive AI for Hillslope Analysis & Disaster-response |
| **Tagline** | "See the risk. Act before the disaster." |
| **Standard** | Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform |
| **Paradigm** | **Predict → Detect → Explain → Warn → Prioritise → Respond → Recover** |

> [!IMPORTANT]
> Never interchange or rename "PARVAT NETRA" and "PAHAD". PARVAT NETRA is the platform. PAHAD is the engine inside it.

---

## 2. Repository Root Layout

The actual project root is `silly-fermi/` inside the workspace:

```
silly-fermi/
├── app.py                            ← 4839-line Flask monolith (primary backend + all API routes)
├── app.py.pre_sih_uiux_20260908.bak  ← Backup before last UI overhaul (do NOT delete)
├── requirements.txt                  ← Flask, psycopg2, gunicorn, shapely, numpy, pandas
├── Dockerfile                        ← Gunicorn production container
├── docker-compose.yml                ← PostGIS db + web (port 8080) services
├── .env / .env.example               ← Secrets (never commit .env)
├── AGENTS.md                         ← Binding constitution for all AI agents
├── SIH_UIUX_RELEASE_NOTES.md         ← Last UI release notes
│
├── engine/                           ← PAHAD scientific modeling core (Python)
│   ├── pahad_models.py               ← Mohr-Coulomb FoS, CRI, alert protocols, thresholds
│   ├── pahad_fusion.py               ← Multimodal fusion engine (FusedPahadPrediction)
│   ├── pahad_inputs.py               ← Feature vector assembly from all modalities
│   ├── pahad_event_predictor.py      ← Landslide event probability (6h/12h/24h/48h horizons)
│   ├── pahad_routing.py              ← BRO corridor routing (NH-10, NH-717A), Dijkstra/A*
│   ├── pahad_history.py              ← Historical landslide catalog + recurrence predictor
│   ├── pahad_sectors.py              ← GSI critical sector registry
│   ├── pahad_prioritization.py       ← Emergency response prioritization
│   ├── pahad_cap.py                  ← OASIS CAP v1.2 XML alert generator
│   ├── pahad_crowd.py                ← Citizen field evidence clustering
│   ├── pahad_multilingual.py         ← NER language synthesis (Nepali, Lepcha, Bhutia, Hindi, EN)
│   ├── pahad_insar.py                ← Sentinel-1 InSAR deformation processor
│   ├── pahad_lstm.py                 ← LSTM temporal predictor
│   ├── pahad_mlops.py                ← MLOps feedback/retrain pipeline
│   ├── terrain_analysis.py           ← DEM slope/aspect/curvature analysis
│   ├── geospatial_registry.py        ← GIS sector geometry registry
│   ├── anthropogenic_slope_service.py ← Anthropogenic cut-slope detection
│   └── __init__.py                   ← Exports all engine symbols
│
├── backend/
│   ├── cv_crack_classifier.py        ← Computer vision crack/mudflow classifier
│   ├── dl_landslide_detector.py      ← Deep learning landslide detector
│   ├── ingestion.py                  ← Data ingestion pipeline
│   ├── institutional_engine.py       ← Institutional/government integration
│   ├── risk_engine.py                ← Core risk evaluation engine (33 KB)
│   ├── routing_engine.py             ← Routing logic (28 KB)
│   ├── scheduler.py                  ← Background task scheduler
│   ├── telemetry_streamer.py         ← SSE telemetry event stream
│   ├── migrate_phase*.py             ← DB migration scripts
│   └── edge/                         ← Phase 3.4: Local Edge Gateway subsystem
│       ├── __init__.py               ← Exports all edge symbols
│       ├── gateway.py                ← EdgeGateway main orchestrator
│       ├── packet.py                 ← 34-byte binary LoRa packet (CRC-16-CCITT)
│       ├── edge_store.py             ← SQLite local persistence (offline buffer)
│       ├── risk_evaluator.py         ← Deterministic edge safety thresholds
│       ├── siren_controller.py       ← Acoustic siren controller (fail-safe dry_run)
│       ├── ble_bridge.py             ← BLE HMAC-signed alert bridge
│       ├── mesh.py                   ← LoRa mesh topology + deduplication
│       ├── sync.py                   ← Cloud sync queue manager
│       ├── routes.py                 ← Edge Flask Blueprint (13 REST endpoints)
│       ├── adapters.py               ← Sensor hardware adapters
│       └── sensor_node.py            ← Sensor node simulation
│
├── services/                         ← External API service adapters
│   ├── weather_service.py            ← IMD/Open-Meteo weather (30 KB)
│   ├── seismic_service.py            ← NCS/USGS seismic data (23 KB)
│   ├── cwc_sync.py                   ← CWC Teesta river hydrometry
│   ├── ai_sitrep.py                  ← AI SitRep synthesis (OmniRoute)
│   ├── ai_triage.py                  ← AI triage engine
│   ├── sar_tracking.py               ← SAR operations tracking
│   ├── dem_service.py                ← DEM elevation tile service
│   ├── satellite_service.py          ← Sentinel satellite service
│   ├── landslide_inventory_service.py ← GSI/ISRO inventory loader
│   ├── sync_service.py               ← Offline sync service
│   └── vegetation_service.py         ← NDVI vegetation change
│
├── templates/                        ← Jinja2 HTML templates (single-page apps)
│   ├── index.html                    ← Main dashboard (543 KB enormous SPA)
│   ├── climate_map.html              ← PAHAD Climate Intelligence workspace
│   ├── seismic.html                  ← Seismic Intelligence workspace
│   ├── terrain_3d.html               ← 3D Terrain workspace
│   ├── edge_network.html             ← Edge Network dashboard (Phase 3.4)
│   ├── console.html                  ← Developer telemetry console
│   ├── login.html                    ← Unified login selector
│   ├── login_authority.html          ← Authority login (gov_id)
│   └── login_citizen.html            ← Citizen login (mobile)
│
├── parvat_netra_mobile/              ← Flutter offline-first mobile app (Phase 3.3)
│   ├── pubspec.yaml                  ← Flutter deps (flutter_map, sqflite, http, geolocator)
│   └── lib/
│       ├── main.dart                 ← App entrypoint, 3-tab navigation, dark theme
│       ├── authority_mode_screen.dart
│       ├── citizen_mode_screen.dart
│       ├── database_helper.dart
│       ├── offline_map_provider.dart
│       ├── sync_service.dart
│       ├── screens/
│       │   ├── field_operations_screen.dart
│       │   ├── edge_test_screen.dart
│       │   └── demo_mode_screen.dart
│       └── services/
│           ├── api_client.dart
│           ├── local_alert_service.dart
│           ├── localization_service.dart
│           ├── location_service.dart
│           └── push_notification_service.dart
│
├── tests/                            ← 86 test files
├── static/uploads/field_reports/     ← Uploaded field report images
├── data/                             ← Static data assets
├── models/                           ← Persisted ML model artifacts
├── reports/                          ← Generated SOP outputs
├── mcp/                              ← MCP integration config
└── docs/PAHAD_PHASE3_3_MOBILE_REPORT.md ← Mobile phase report (25 KB)
```

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Backend Language | Python 3.11+ |
| Web Framework | Flask 3.0.3 (monolith — single `app.py`) |
| WSGI Server | Gunicorn 22.0.0 |
| Spatial Database | PostgreSQL 15 + PostGIS 3.3 (Neon cloud or local Docker) |
| DB Driver | psycopg2-binary 2.9.9 |
| ML/Science | numpy >= 1.26, pandas >= 2.0, shapely 2.0.4 |
| Edge Local DB | SQLite (Python stdlib sqlite3, managed by EdgeStore) |
| Container | Docker + docker-compose |
| Mobile | Flutter 3.16+, Dart SDK >= 3.0 |
| Mobile Map | flutter_map ^6.1.0 (OpenStreetMap tiles) |
| Mobile DB | sqflite ^2.3.0 (offline local storage) |
| Local AI Gateway | OmniRoute at http://localhost:20128 (OpenAI-compatible /v1) |

---

## 4. Database Schema (PostGIS/Neon)

### Tables

```sql
hazard_zones      -- Zone polygons (GEOMETRY Polygon/4326) with susceptibility
landslide_events  -- Historical/live events (GEOMETRY Point/4326) from GSI/ISRO/Citizen
rainfall_obs      -- IMD district rainfall observations (48h cumulative)
field_reports     -- Citizen/field officer hazard reports with images
risk_decisions    -- Authority-approved risk decisions with recommended actions
```

### Initialization

`init_db()` in `app.py` is **idempotent**: creates PostGIS extension, tables, GiST indexes, and seeds 4 hazard zones + 5 landmark events on first run.

### Connection

- **Production**: Neon cloud PostgreSQL — `NEON_DB_URL` in `.env`
- **Local Dev**: Docker Compose → `postgresql://postgres:...@localhost:5432/parvat_netra`
- **Testing**: Set `PARVAT_TESTING=1` → timeout drops to 1s, retries to 1 to prevent hangs

---

## 5. PAHAD Engine: Core Scientific Architecture

### CRI (Composite Risk Index) Fusion Weights

```python
alpha_static  = 0.40  # Static terrain susceptibility (GSI NLSM, slope, lithology)
beta_rainfall = 0.35  # Dynamic hydrometeorology (IMD rainfall, Antecedent API)
gamma_ground  = 0.25  # Ground observation (InSAR, IoT sensors)
```

### Alert Protocol Tiers

| Tier | Color Hex | Threshold | Response |
|---|---|---|---|
| LOW | #10B981 Emerald | CRI < 0.25 | Routine monitoring |
| MODERATE | #F59E0B Amber | CRI 0.25-0.45 | Elevated observation, 5-min polling |
| HIGH | #F97316 Orange | CRI 0.45-0.60 | Watch advisory to DDMA, citizen alerts |
| VERY_HIGH | #EA580C Deep Orange | CRI 0.60-0.75 | Warning to SDMA/NDRF, route diversion |
| EXTREME | #DC2626 Red | CRI >= 0.75 | CAP-XML broadcast, siren, evacuation |

### 2-of-3 Constitutional Invariant

**EXTREME alerts require 2-of-3 independent signal confirmation:**
- Physical FoS breach (Mohr-Coulomb)
- Empirical rainfall threshold exceeded (ID/ED/API)
- Ground sensor anomaly (InSAR/IoT)

Single-source EXTREME is auto-downgraded. Output always includes `downgraded=True` and `downgrade_reason`.

### Key Engine Modules

| Module | Class/Function | Role |
|---|---|---|
| `pahad_models.py` | `calculate_infinite_slope_fs()` | Mohr-Coulomb limit equilibrium FoS |
| `pahad_models.py` | `is_empirical_threshold_exceeded()` | ID/ED/API rainfall threshold checks |
| `pahad_models.py` | `calculate_composite_risk_index()` | CRI computation + 2-of-3 rule |
| `pahad_fusion.py` | `PahadFusionEngine.fuse()` | Full multimodal fusion → FusedPahadPrediction |
| `pahad_event_predictor.py` | `PAHAD_EVENT_PREDICTOR` | Event probability (6h/12h/24h/48h) |
| `pahad_routing.py` | `RoadConnectivityRoutingEngine` | BRO corridors, Dijkstra/A* hazard routing |
| `pahad_cap.py` | `CAPAlertGenerator` | OASIS CAP v1.2 XML broadcasts |
| `pahad_multilingual.py` | `NERMultilingualSynthesizer` | 5 NER languages |
| `pahad_insar.py` | `InSARDeformationProcessor` | Sentinel-1 LOS velocity processing |
| `pahad_crowd.py` | `CrowdVerificationEngine` | Citizen report clustering and verification |

---

## 6. Flask API Surface (app.py — 90+ Routes)

### Page Routes

| Route | Template |
|---|---|
| `GET /` | `index.html` (role-aware: authority/citizen) |
| `GET /login` | `login.html` |
| `GET /login/authority` | `login_authority.html` |
| `GET /login/citizen` | `login_citizen.html` |
| `GET /console` | `console.html` |
| `GET /climate-map` | `climate_map.html` |
| `GET /seismic` | `seismic.html` |
| `GET /terrain-3d` | `terrain_3d.html` |

### Core API (Selected, Grouped by Domain)

**Health & Ingestion**
- `GET /api/health` — PostGIS connectivity + system info
- `POST /api/ingest/imd-rainfall` — Pull IMD rainfall, upsert rainfall_obs

**Field Reports & Sync**
- `POST /api/reports/submit` — Citizen/field report with image
- `GET /api/reports/list` — All field reports
- `GET /api/reports/export-sop` — Export SOP document
- `POST /api/sync/field-reports` — Mobile offline sync endpoint

**Alerts & Sirens**
- `GET /api/alerts/stream` — SSE real-time event stream
- `POST /api/alerts/dispatch-siren` — Authority siren dispatch
- `GET /api/alerts/active` — All active alerts
- `POST /api/alerts/acknowledge` — Acknowledge an alert
- `POST /api/alerts/broadcast-trigger` — Broadcast alert
- `POST /api/alerts/ivr-broadcast` — IVR phone broadcast

**AI & OmniRoute**
- `GET /api/ai/triage-status` — AI triage state
- `GET,POST /api/ai/sitrep` — AI situation report
- `GET /api/omniroute/status` — OmniRoute gateway health
- `POST /api/omniroute/briefing` — Natural language briefing

**PAHAD Risk Engine**
- `POST /api/ml/predict-fos` — Factor of Safety prediction
- `GET /api/ml/latest-risk` — Latest highest-risk sector assessment
- `GET,POST /api/pahad/fused-risk` — Full PAHAD multimodal fusion
- `POST /api/pahad/predict-event` — Event probability prediction
- `GET /api/pahad/evaluate-sector` — Sector hazard evaluation
- `POST /api/pahad/generate-cap` — Generate CAP XML alert
- `POST /api/pahad/multilingual-alert` — Multilingual alert
- `POST /api/pahad/insar-deformation` — Process InSAR data
- `POST /api/pahad/iot-telemetry` — IoT telemetry ingestion
- `POST /api/pahad/corroborate-incidents` — Incident corroboration
- `GET /api/pahad/critical-sectors` — Critical sector registry
- `GET /api/pahad/response-prioritization` — Emergency response priorities
- `GET /api/pahad/regional-overview` — Regional risk overview

**Geospatial & Terrain**
- `GET /api/spatial/live-risk` — Live spatial risk overlay
- `GET /api/geospatial/terrain` — DEM terrain analysis
- `GET /api/geospatial/dem` — DEM elevation tiles
- `GET /api/geospatial/vegetation` — NDVI vegetation data
- `GET /api/geospatial/historical-landslides` — Historical catalog
- `GET /api/geospatial/satellite/status` — Satellite status
- `GET /api/geospatial/offline-manifest` — Mobile offline tile manifest

**Sensors & Telemetry**
- `GET /api/sensors/live` — Live IoT sensor telemetry
- `GET /api/insar/points` — InSAR deformation points
- `POST /api/telemetry/ping` — Sensor/device ping
- `GET /api/telemetry/devices` — Registered devices

**Hydrology & Weather**
- `GET /api/hydro/teesta-status` — CWC Teesta hydrometry
- `GET /api/weather/live` — Live weather data
- `GET /api/weather/climate-map` — Climate map data
- `GET /api/weather/forecast` — Weather forecast

**Seismic**
- `GET /api/seismic/latest` — Latest seismic event
- `GET /api/seismic/recent` — Recent seismic events
- `GET /api/seismic/status` — Seismic service status
- `GET /api/seismic/impact` — Seismic impact assessment

**Routing & Evacuation**
- `GET,POST /api/routing/safe-route` — FASTEST/SHORTEST/SAFEST routes
- `GET /api/routing/evacuation-plan` — Evacuation plan
- `GET /api/shelters` — Emergency shelters
- `POST /api/pahad/routing/calculate-bypass` — Calculate bypass

**Historical Analysis**
- `GET /api/pahad/history/catalog` — Historical landslide catalog
- `GET /api/pahad/history/hotspots` — Historical hotspots
- `POST /api/pahad/history/correlate-nowcast` — Historical vs nowcast

**Authority**
- `POST /api/decisions/<id>/authorize` — Authority decision
- `GET /api/kpis` — Platform KPI dashboard

### Edge Network Blueprint (Phase 3.4)

| Route | Method | Purpose |
|---|---|---|
| `/api/edge/status` | GET | Gateway health (mesh + siren + BLE) |
| `/api/edge/nodes` | GET | Registered sensor nodes |
| `/api/edge/network` | GET | Network topology |
| `/api/edge/readings` | GET | Buffered sensor readings |
| `/api/edge/alerts` | GET | Edge-triggered alerts |
| `/api/edge/siren/status` | GET | Siren controller state |
| `/api/edge/siren/test` | POST | Fire SIREN_TEST_EVENT (no audio) |
| `/api/edge/siren/arm` | POST | Arm siren controller |
| `/api/edge/siren/disarm` | POST | Disarm siren |
| `/api/edge/demo/inject` | POST | Inject demo sensor reading |
| `/api/edge/toggle-cloud` | POST | Simulate cloud disconnect |
| `/api/edge/sync/flush` | POST | Force sync queue flush |
| `/edge-network` | GET | Edge Network dashboard template |

---

## 7. Phase 3.4 — Edge Gateway Architecture

### Signal Flow

```
SENSOR NODE (physical or simulated)
  → Binary Packet (34 bytes, LoRa SF7/SF8 airtime)
    → EdgeGateway.process_raw_packet()
      → CRC-16-CCITT verification
      → LoRaMesh.receive_packet() (deduplication by sequence + node hash)
      → EdgeStore.log_raw_packet() (SQLite)
      → EdgeRiskEvaluator.evaluate_reading() → SAFE/WATCH/WARNING/CRITICAL
        → If WARNING/CRITICAL:
            SirenController.activate() [dry_run by default]
            BLEAlertBridge.send_alert() [if device paired]
            EdgeStore.insert_alert()
      → EdgeStore.insert_reading(buffer_for_cloud=True)
      → EdgeSync.flush_sync_queue() → POST to central cloud (when online)
```

### Binary Packet Format (34 bytes, struct >BBHIIffffBhB)

```
[0]     Version    uint8   — Protocol version (currently 1)
[1]     Flags      uint8   — bit0=DEMO, bit1=RELAY_HOP, bit2=ALERT_TRIGGERED
[2:4]   Node Hash  uint16 BE — CRC-16 of node_id string (for compact LoRa ID)
[4:8]   Sequence   uint32 BE — Monotonic counter (for deduplication)
[8:12]  Timestamp  uint32 BE — Unix epoch seconds
[12:16] Soil Moisture VWC %  float32 IEEE 754
[16:20] Pore Pressure kPa    float32 IEEE 754
[20:24] Borehole Tilt deg    float32 IEEE 754
[24:28] Rainfall mm/h        float32 IEEE 754
[28]    Battery %            uint8 (0-100)
[29:31] Temperature C * 10   int16 BE
[31]    Humidity %           uint8 (0-100)
[32:34] CRC-16-CCITT         uint16 BE (over bytes [0:32])
```

### Edge Safety Thresholds (Eastern Himalaya Regolith Standard)

| Sensor | Watch | Warning | Critical |
|---|---|---|---|
| Rainfall mm/h | 10.0 | 25.0 | 45.0 |
| Soil Moisture % | 40.0 | 48.0 | 55.0 |
| Pore Pressure kPa | 15.0 | 28.0 | 38.0 |
| Borehole Tilt deg | 0.5 | 1.5 | 3.0 |

### Anomaly Score Formula

```
anomaly_score = 0.35*norm_sm + 0.30*norm_pp + 0.20*norm_tilt + 0.15*norm_rain
```
(Normalized: sm/55, pp/40, tilt/3, rain/50)

### Edge State Determination

| Condition | State |
|---|---|
| critical_count >= 1 OR anomaly_score >= 0.80 | CRITICAL |
| warning_count >= 2 OR (warning_count >= 1 AND anomaly_score >= 0.40) | WARNING |
| warning_count >= 1 OR watch_count >= 1 OR anomaly_score >= 0.35 | WATCH |
| otherwise | SAFE |

### Siren Invariants

- Default: `SIREN_HARDWARE_ENABLED=false`, `SIREN_DRY_RUN=true`
- Physical activation requires `SIREN_HARDWARE_ENABLED=true` in env only (never in code)
- Test events (`/api/edge/siren/test`) always produce `SIREN_TEST_EVENT` without audio
- `dry_run=True` is always set in test event output regardless of environment
- All activations recorded in tamper-evident SQLite audit log

---

## 8. Flutter Mobile Application (Phase 3.3)

### Architecture

- Package: `parvat_netra_mobile`, Flutter 3.16+, Dart >= 3.0
- Pattern: Offline-first (SQLite local store + periodic background cloud sync)
- Theme: Dark obsidian (#070B10), Material 3, national navy primary (#1E3A8A), saffron accent (#D97706)

### Navigation (3-Tab Bottom Bar — IndexedStack)

| Tab Index | Screen File | Role |
|---|---|---|
| 0 | `authority_mode_screen.dart` | District command: risk map, dispatch, decisions |
| 1 | `field_operations_screen.dart` | Field officer: GPS, sensor readings, offline reports |
| 2 | `citizen_mode_screen.dart` | Citizen: SOS, hazard report, safe route, alerts |

Default tab on launch: **Tab 1** (Field Operations)

### Supplementary Screens (Drawer Only)

| Screen | Purpose |
|---|---|
| `EdgeTestScreen` | BLE/Edge harness — tests siren pairing and injection |
| `DemoModeScreen` | SIH evaluator narrated demo walkthrough |

### Services

| Service | File | Size |
|---|---|---|
| REST API Client | `api_client.dart` | 11 KB |
| Multilingual (5 NER languages) | `localization_service.dart` | 14 KB |
| GPS/Geofence | `location_service.dart` | 4.5 KB |
| Local Alerts | `local_alert_service.dart` | 4.8 KB |
| Push Notifications | `push_notification_service.dart` | 4.9 KB |
| Background Sync | `sync_service.dart` | 6.5 KB |

### Key Flutter Dependencies

| Package | Version | Role |
|---|---|---|
| flutter_map | ^6.1.0 | OpenStreetMap tile rendering |
| sqflite | ^2.3.0 | SQLite offline storage |
| path_provider | ^2.1.2 | Platform file paths |
| connectivity_plus | ^5.0.2 | Network detection |
| geolocator | ^11.0.0 | GPS/location |
| http | ^1.2.0 | REST API calls |
| cached_network_image | ^3.3.1 | Cached map imagery |
| latlong2 | ^0.9.0 | Lat/lng coordinate types |

---

## 9. OmniRoute Local AI Gateway

- **Base URL**: `http://localhost:20128`
- **API**: OpenAI-compatible at `/v1/chat/completions`
- **Purpose**: Natural language SitRep, multilingual safety broadcasts, tactical decision intelligence
- **Fail-Safe Rule**: If offline, ALL services fall back to deterministic geotechnical formulas and display `[LIVE / DETERMINISTIC]` badge — never blocks platform telemetry
- **Integration**: `app.py` routes `/api/omniroute/status` and `/api/omniroute/briefing`; service layer `services/ai_sitrep.py`

---

## 10. Data Provenance Protocol (Mandatory — All UI)

| Badge | Meaning |
|---|---|
| `[LIVE]` | Authenticated real-time sensor or API feed |
| `[SIMULATED]` | Statistically realistic physics sim based on historical rainfall |
| `[HISTORICAL]` | Archival ground truth from GSI/IMD records |
| `[DEMO]` | Synthetic walkthrough for evaluator inspection |
| `[CACHED]` | Recently fetched, served from local cache |
| `[EDGE / LOCAL THRESHOLD DETERMINISTIC]` | Edge safety evaluation (not cloud PAHAD) |

---

## 11. Geographic Focus

- **Region**: Eastern Himalaya — Sikkim + Darjeeling, West Bengal
- **Corridors**: NH-10 (Siliguri–Gangtok), NH-717A (Melli–Jorethang–Namchi)
- **Districts**: Gangtok, Mangan, Pakyong, Kalimpong, Darjeeling
- **River**: Teesta (CWC gauging stations)
- **Gateway Location**: Singtam Staging Depot (NH-10 Corridor)

### Seeded Hazard Zones

| Zone | Susceptibility |
|---|---|
| NH-10 Corridor (Rangpo-Singtam) | HIGH |
| Gangtok-JN Road (Nathu La access) | HIGH |
| Kalimpong Hill Slopes (Teesta Valley) | MODERATE |
| Mangan-Chungthang Highway | HIGH |

---

## 12. Design System

### Color Tokens

| Token | Hex | Usage |
|---|---|---|
| Obsidian Base | #070B10 | Page background |
| Slate Surface | #0F172A | Card/panel background |
| Slate Border | #1E293B | Component borders |
| National Navy | #1E3A8A | Primary interactive color |
| Saffron Accent | #D97706 | Secondary accent |
| Sky Blue | #38BDF8 | Highlights, active states |
| Slate Text | #94A3B8 | Secondary text |
| Frost White | #E2E8F0 | Primary text on dark |

### Typography
- Primary: Inter (headings, body)
- Monospace: JetBrains Mono (telemetry values, sensor readouts)

### Prohibited Design Patterns
- NO cyberpunk neon glows or grid scans
- NO video-game reticles or decorative HUDs
- NO heavy glassmorphism blurring critical sensor curves
- NO decorative/meaningless AI animation widgets

---

## 13. Environment Variables Reference

```env
# Core
PORT=8000
ENVIRONMENT=development
SECRET_KEY=...

# Database
NEON_DB_URL=postgresql://...@...neon.tech/neondb?sslmode=require
DATABASE_URL=...  # local Docker fallback

# PAHAD
PAHAD_DEMO_MODE=0  # 0=production, 1=demo walkthrough

# Weather
OPENWEATHER_API_KEY=
IMD_API_TOKEN=

# GIS/Routing
MAPBOX_ACCESS_TOKEN=
GOOGLE_MAPS_API_KEY=

# Satellite (Copernicus)
COPERNICUS_CLIENT_ID=
COPERNICUS_CLIENT_SECRET=

# OmniRoute/AI
EXPLABS_API_KEY=
EXPLABS_BASE_URL=https://api.experientiallabs.ai/v1

# Edge
EDGE_GATEWAY_ID=GW-01
EDGE_GATEWAY_LOC=Singtam Staging Depo (NH-10 Corridor)
SIREN_HARDWARE_ENABLED=false   # MUST stay false unless physical hardware present
SIREN_DRY_RUN=true

# Testing
PARVAT_TESTING=1  # Set in test environments to reduce DB timeout to 1s
```

---

## 14. Test Suite

### Overview

86 test files in `tests/` covering every subsystem.

```bash
# Run all tests (from silly-fermi/)
PARVAT_TESTING=1 python -m pytest tests/ -v --tb=short

# Edge subsystem tests (Phase 3.4)
PARVAT_TESTING=1 python -m pytest tests/test_edge_*.py -v

# PAHAD engine tests
PARVAT_TESTING=1 python -m pytest tests/test_pahad_*.py -v
```

### Phase 3.4 Edge Test Coverage

| Test File | Coverage Area |
|---|---|
| `test_edge_packet.py` | CRC, encode/decode, malformed packets |
| `test_edge_store.py` | SQLite CRUD, queue stats, cloud buffering |
| `test_edge_risk.py` | Threshold evaluation, state transitions |
| `test_edge_siren.py` | Dry-run invariants, audit log, test events |
| `test_edge_ble.py` | HMAC signing, pairing, alert dispatch |
| `test_edge_mesh.py` | Deduplication, node health, topology |
| `test_edge_gateway.py` | End-to-end pipeline, malformed rejection |
| `test_edge_api.py` | REST endpoint contract tests |

### Known Test Constraints

- DB-integrated tests skip gracefully if PostGIS is unavailable (requires `PARVAT_TESTING=1`)
- E2E Playwright tests require running server + browser (`e2e_playwright_test.py`)
- `psycopg2` must be installed: `pip install -r requirements.txt`

---

## 15. Deployment

### Local Development

```bash
cd silly-fermi
pip install -r requirements.txt
cp .env.example .env    # Fill credentials
python app.py           # → http://127.0.0.1:8080
```

### Docker Compose

```bash
cd silly-fermi
docker-compose up       # → http://localhost:8080 (web + PostGIS)
```

### Production Target

- Container: `Dockerfile` (Gunicorn, port 8080)
- Cloud: Google Cloud Run (`GCP_PROJECT_ID`, `GCP_REGION=asia-south1`)
- Database: Neon serverless PostgreSQL + PostGIS

---

## 16. Specialized Agent Swarm

Five domain-specialized AI agents registered in `.agents/agents/`:

| Agent | Domain |
|---|---|
| `geotechnical_physics_agent` | Mohr-Coulomb FoS, pore pressure, slope mechanics |
| `gis_hydrology_sentinel_agent` | PostGIS spatial, Sentinel-1 InSAR, CWC Teesta |
| `tactical_evacuation_routing_agent` | BRO corridors, Dijkstra/A* hazard routing, relief staging |
| `multi_source_triage_coordinator` | Citizen clustering, drone/CCTV, SDRF/NDRF dispatch, CAP |
| `omniroute_agent_bridge` | OmniRoute LLM orchestration, multilingual, structured output |

---

## 17. Current Implementation Status

| Component | Status | Notes |
|---|---|---|
| PAHAD Engine Core | Functional | Mohr-Coulomb FoS, CRI fusion, event predictor |
| Weather Intelligence | Functional | IMD + Open-Meteo fallback |
| Seismic Intelligence | Functional | NCS + USGS, real-time stream |
| GIS / InSAR | Functional | Sentinel-1, PostGIS spatial layers |
| 3D Terrain | Functional | DEM slope/aspect/curvature |
| Climate Map | Functional | Dedicated workspace |
| CAP v1.2 Alerts | Functional | XML broadcast generation |
| Multilingual NER | Functional | 5 languages |
| Routing Engine | Functional | FASTEST/SHORTEST/SAFEST |
| OmniRoute AI | Functional (needs local server) | Graceful fallback if offline |
| Citizen Reporting | Functional | With image upload |
| SSE Telemetry Stream | Functional | Real-time event stream |
| Edge Gateway Phase 3.4 | Complete | All subsystems + full test suite |
| Flutter Mobile Phase 3.3 | Functional | 3-tab + offline-first + demo mode |
| Flutter BLE/Edge UI | Functional | EdgeTestScreen |
| JWT Authentication | Partial | Session-based currently; JWT not fully enforced |
| PostGIS Live DB | Requires credentials | Neon credentials needed in .env |
| Physical Siren | Dry-run only | SIREN_HARDWARE_ENABLED=true for real hardware |
| OmniRoute LLM | Requires local server | Must run http://localhost:20128 |

---

## 18. Critical Architectural Invariants (Never Violate)

1. **2-of-3 Confirmation**: EXTREME alerts require independent confirmation from ≥2 signal sources.

2. **Explainability Mandatory**: Every risk score MUST include `top_drivers` with modality contribution percentages.

3. **Provenance Badges Mandatory**: Every data point in UI must carry a provenance badge.

4. **Siren Fail-Safe**: `SIREN_HARDWARE_ENABLED` defaults `false`. Never change default in code — operator env only.

5. **OmniRoute Never Blocks**: If offline, fall back to deterministic formulas. Never throw uncaught exception that halts telemetry.

6. **No Straight-Line Routes**: If routing APIs are unavailable, use PostGIS geometric graph. Never render a straight line.

7. **No Map Remount**: Route selection must update vector layers dynamically. Never reload or remount the map component.

8. **Credentials in .env Only**: Never hardcode API keys. Validate with `python mcp/scripts/validate_config.py`.

---

## 19. Next Development Priorities (Phase 4+)

1. **JWT Auth Hardening**: Replace session-based auth with proper JWT for API endpoints
2. **Flutter Geofence Push Alerts**: Real-time push when user enters HIGH/EXTREME risk zone
3. **PAHAD MLOps Retrain**: Complete `/api/pahad/mlops/feedback-retrain` with actual model retraining
4. **InSAR Live Integration**: Connect to real Copernicus Data Space API
5. **Physical Siren Hardware**: Production wiring to GPIO/relay controller
6. **LoRa Real Hardware**: Replace demo injection with real radio drivers in `backend/edge/adapters.py`
7. **Mobile Offline Tiles**: Pre-bundle NH-10 corridor tiles in Flutter for zero-connectivity operations
8. **Tablet Authority UI**: Optimize authority mode for 10"+ tablet commanders

---

## 20. Quick Start for the Next Agent

```bash
# 1. Enter project root
cd PARVAT_NETRA_PAHAD_AI_FIRST/silly-fermi

# 2. MANDATORY: Read binding rules first
cat AGENTS.md

# 3. Set up environment
pip install -r requirements.txt
cp .env.example .env
# → Edit .env with NEON_DB_URL and API keys

# 4. Start server
python app.py
# → http://localhost:8080

# 5. Run tests
PARVAT_TESTING=1 python -m pytest tests/ -v --tb=short

# 6. Flutter mobile
cd parvat_netra_mobile
flutter pub get
flutter run
```

### Key Files to Read First (in priority order)

1. `AGENTS.md` — Binding constitution for all agents
2. `engine/__init__.py` — All PAHAD engine exports
3. `engine/pahad_fusion.py` — Core multimodal fusion logic
4. `backend/edge/gateway.py` — Edge Gateway orchestration
5. `parvat_netra_mobile/lib/main.dart` — Mobile app entrypoint
6. `app.py` lines 1–170 — Flask init, PostGIS schema, first routes

---

*Generated from complete repository audit on 2026-09-09.*  
*All statements grounded in actual source files. No fabrication.*
