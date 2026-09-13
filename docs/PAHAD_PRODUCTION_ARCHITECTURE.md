# PAHAD AI — Production Architecture

**Document**: `PAHAD_PRODUCTION_ARCHITECTURE.md`  
**Classification**: Engineering Reference  
**Status**: Phase 5 — Real-Data Predictive Research System  

---

## 1. System Identity

| Property | Value |
|----------|-------|
| **Platform** | PARVATNETRA — NER Sentinel |
| **AI Engine** | PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response) |
| **Problem Statement** | SIH 26001 |
| **Geographic Scope** | Northeast India (8 states — Sikkim, Assam, Meghalaya, Manipur, Mizoram, Nagaland, Arunachal Pradesh, Tripura) |
| **Primary Paradigm** | Predict → Detect → Explain → Warn → Prioritise → Respond → Recover |

---

## 2. Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL DATA SOURCES                       │
│  IMD Weather AWS │ USGS/NCS Seismic │ GLO-30 DEM │ Sentinel-1 InSAR│
│  LoRaWAN IoT     │ CWC Hydrometric  │ GSI NLSM   │ Citizen Reports │
└──────────┬────────────────┬──────────────────────────────┬──────────┘
           │                │                              │
           ▼                ▼                              ▼
┌──────────────────┐ ┌──────────────────┐ ┌───────────────────────────┐
│  services/       │ │  services/       │ │  services/                │
│  weather_service │ │  seismic_service │ │  device_gateway.py        │
│  .py             │ │  .py             │ │  (IoT / LoRaWAN / MQTT)   │
└────────┬─────────┘ └───────┬──────────┘ └─────────────┬─────────────┘
         │                   │                           │
         └─────────┬─────────┘                           │
                   ▼                                     │
        ┌──────────────────────┐                         │
        │  services/           │                         │
        │  cache_manager.py    │◄────────────────────────┘
        │  data_provenance.py  │
        │  ingestion_manager.py│
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────────────────────────────────────┐
        │                  PAHAD AI ENGINE                     │
        │                                                      │
        │  engine/pahad_models.py     (Infinite Slope FoS)    │
        │  engine/pahad_event_predictor.py (ML classifier)    │
        │  engine/pahad_lstm.py       (surrogate — NOT TRAINED)│
        │  engine/pahad_fusion.py     (CRI multi-signal fusion)│
        │  engine/pahad_live_inference.py  (Phase 5 pipeline) │
        │  engine/event_labeling.py   (label validation)      │
        └──────────────────────────┬───────────────────────────┘
                                   │
                   ┌───────────────┼───────────────┐
                   ▼               ▼               ▼
        ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │ engine/          │ │ engine/      │ │ engine/          │
        │ pahad_alert_     │ │ pahad_geo-   │ │ pahad_notific-   │
        │ policy.py        │ │ fence.py     │ │ ation_           │
        │ (8-state FSM)    │ │ (15km zone)  │ │ orchestrator.py  │
        └────────┬────────┘ └──────────────┘ └────────┬─────────┘
                 │                                     │
                 ▼                                     ▼
        ┌─────────────────────────────────────────────────────┐
        │               Flask Web Application                  │
        │                     app.py                           │
        │  ~200 API routes including:                          │
        │  GET/POST /api/pahad/live-inference                  │
        │  GET/POST /api/pahad/forecast                        │
        │  GET      /api/pahad/data-status                     │
        │  GET      /api/pahad/event-model/status              │
        │  GET      /api/pahad/event-model/data-quality        │
        │  GET      /api/system/provenance                     │
        │  POST     /api/iot/telemetry                         │
        │  GET      /api/iot/devices                           │
        └─────────────────────────────────────────────────────┘
                              │
               ┌──────────────┼───────────────────┐
               ▼              ▼                   ▼
    ┌──────────────┐  ┌────────────────┐  ┌──────────────────────┐
    │ Flutter Mobile│  │ Web Dashboard  │  │ Edge Nodes           │
    │ app/         │  │ static/ +      │  │ (BLE Mesh / LoRaWAN) │
    │ (Android/iOS)│  │ templates/     │  │ engine/pahad_edge_*.py│
    └──────────────┘  └────────────────┘  └──────────────────────┘
```

---

## 3. Key Components

### 3.1 PAHAD AI Engine (`engine/`)

| Module | Purpose | Status |
|--------|---------|--------|
| `pahad_models.py` | Infinite Slope FoS (Mohr-Coulomb) | ✅ ACTIVE |
| `pahad_event_predictor.py` | ML event classifier (GBM+Platt) | ✅ TRAINED_LIMITED_DATA |
| `pahad_fusion.py` | Multi-signal CRI fusion | ✅ ACTIVE |
| `pahad_live_inference.py` | Phase 5 live pipeline | ✅ ACTIVE |
| `pahad_alert_policy.py` | 8-state alert lifecycle | ✅ ACTIVE |
| `pahad_notification_orchestrator.py` | Alert dispatch | ✅ ACTIVE |
| `pahad_geofence.py` | 15km geofence + infra impact | ✅ ACTIVE |
| `pahad_lstm.py` | Temporal deep learning surrogate | ⚠️ NOT_TRAINED (mathematical surrogate) |
| `event_labeling.py` | Event label validation | ✅ ACTIVE |

### 3.2 Services (`services/`)

| Module | Purpose |
|--------|---------|
| `weather_service.py` | IMD AWS / Open-Meteo with fallback |
| `seismic_service.py` | USGS / NCS with fallback |
| `device_gateway.py` | IoT LoRaWAN/MQTT packet ingestion |
| `cache_manager.py` | Multi-namespace disk-backed cache |
| `data_provenance.py` | Provenance badge tracking |
| `dem_service.py` | GLO-30 terrain attributes |
| `push_service.py` | FCM push notifications |
| `sms_service.py` | Multilingual SMS dispatch |

### 3.3 Data Layers (`data/`)

```
data/
├── raw/
│   └── historical_landslides_ner.csv   (17 documented events)
├── features/
│   ├── real_train.csv   (16 samples — temporal split train)
│   ├── real_val.csv     (12 samples — temporal split val)
│   └── real_test.csv    (8 samples — held-out test)
├── processed/
│   ├── temporal_events.csv    (Phase 5 build)
│   ├── temporal_controls.csv  (Phase 5 dry-season controls)
│   └── temporal_full.csv      (combined)
├── labels/
│   └── event_labels.csv
└── manifests/
    └── temporal_dataset_manifest.json
```

---

## 4. Alert Safety Architecture

```
PAHAD AI Event Classifier
          │
          │ P(event) > 0.70?
          ▼
    ┌─────────────────────────────────────────────┐
    │  2-OF-3 CORROBORATION GATE                  │
    │  Signal 1: FoS < 1.10 (physics)             │
    │  Signal 2: Rainfall > 150mm/24h             │
    │  Signal 3: P(event) > 0.70 (ML)             │
    │                                             │
    │  Minimum 2 of 3 must be TRUE                │
    └─────────────────────┬───────────────────────┘
                          │
                          ▼
            PahadAlertPolicyEngine.evaluate()
                          │
              8-STATE LIFECYCLE FSM:
              DETECTED → EVALUATING → VERIFIED
              → ISSUED → ACKNOWLEDGED
              → ESCALATED → RESOLVED / EXPIRED
                          │
                          ▼
          ┌──────────────────────────────────┐
          │ HIGH+ alerts require SDMA auth   │
          │ authorization_required = True    │
          └──────────────────────────────────┘
                          │
                          ▼
          PahadNotificationOrchestrator.dispatch_alert()
          │                    │              │
          ▼                    ▼              ▼
    Push (FCM)          SMS (multilingual)  CAP XML
    PushService.py      SMSService.py       (OASIS CAP v1.2)
```

---

## 5. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PAHAD_DEMO_MODE` | `0` | Set to `1` for demo/training mode — provenance = SIMULATED |
| `PARVAT_TESTING` | `0` | Set to `1` for test mode — reduces timeouts |
| `DRY_RUN` | `true` | When true, suppresses real SMS/siren dispatch |
| `FLASK_ENV` | `development` | Flask environment |
| `FLASK_PORT` | `5000` | Server port |
| `WEATHER_CACHE_TTL` | `900` | Weather cache TTL in seconds (15 min) |
| `SEISMIC_CACHE_TTL` | `300` | Seismic cache TTL in seconds (5 min) |
| `IOT_FRESHNESS_S` | `120` | Max IoT data age before DEGRADED label |
| `DB_URL` | (none) | PostgreSQL/PostGIS connection string |
| `IMD_API_KEY` | (none) | IMD weather API key (optional — falls back to Open-Meteo) |
| `NCS_API_KEY` | (none) | NCS seismic API key (optional — falls back to USGS) |
| `OMNIROUTE_BASE_URL` | `http://localhost:20128/v1` | Local OmniRoute LLM gateway |

---

## 6. Starting the System

### Production
```powershell
# Set environment
$env:PAHAD_DEMO_MODE = "0"
$env:DRY_RUN = "false"
$env:FLASK_ENV = "production"

# Start server
cd c:\Users\dimpu\Downloads\PARVAT_NETRA_PAHAD_AI_FIRST\silly-fermi
python app.py
```

### Demo / Development
```powershell
$env:PAHAD_DEMO_MODE = "1"
$env:DRY_RUN = "true"
$env:PARVAT_TESTING = "1"
python app.py
```

### Test Suite
```powershell
python -m pytest tests/ -v --tb=short
```

---

## 7. Model Registry

| File | Contents |
|------|---------|
| `models/pahad_event_model.pkl` | Trained GBM + Platt calibration pipeline |
| `models/pahad_event_model.metadata.json` | Version, hash, metrics, status |
| `models/pahad_event_metrics.json` | Full benchmark results |
| `models/fos_predictor.pkl` | FoS ML predictor (Phase 3 geotechnical) |

**Current model status**: `DATA-GROUNDED RESEARCH PROTOTYPE`  
**Training samples**: N=16 real events, N=36 total (16 train + 12 val + 8 test)

---

## 8. Provenance States

| Badge | Meaning |
|-------|---------|
| `[LIVE]` | Authenticated real-time API feed |
| `[CACHED]` | Local cache within freshness window |
| `[MODELLED]` | Derived from physics model or DEM |
| `[HISTORICAL]` | Archival GSI/NRSC/SDMA record |
| `[MISSING]` | Not available — training median imputed |
| `[SIMULATED]` | Demo mode only — synthetic calibrated value |
| `[UNAVAILABLE]` | Service unreachable — no fallback |
