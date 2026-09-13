# PARVAT NETRA — NER Sentinel

> **"See the risk. Act before the disaster."**  
> *Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform*  
> *Operational Paradigm: **Predict -> Detect -> Explain -> Warn -> Prioritise -> Respond -> Recover***

---

## Overview

**PARVAT NETRA** is an autonomous, multimodal disaster intelligence and early warning platform engineered specifically for the fragile hillslopes and highway corridors of Northeast India (North East Region - NER). 

At the platform's core is **PAHAD AI** (*Predictive AI for Hillslope Analysis & Disaster-response*), a geotechnical and hydrological modeling engine that corroborates multi-tiered telemetry to eliminate single-threshold false alarms and provide defensible, explainable landslide forecasts.

---

## Key Capabilities & Architecture

### 1. Multimodal Evidence Fusion
PARVAT NETRA never triggers alerts based on unexplainable black-box heuristics. Every warning requires corroboration across six core modalities:
1. **Physical Mechanics**: Infinite Slope Factor of Safety (FoS) computed via Mohr-Coulomb shear strength criteria.
2. **In-Situ Geotechnical Telemetry**: Piezometric pore-water pressure, borehole inclinometer tilt, displacement, and seismic vibration.
3. **Precipitation Dynamics**: Real-time rainfall intensity + 24h/72h Antecedent Precipitation Index (API).
4. **Satellite Earth Observation**: Sentinel-1 InSAR line-of-sight ground deformation and Sentinel-2 NDVI canopy loss.
5. **Computer Vision**: CCTV and UAV aerial imagery detecting tension crack aperture expansions and mudflow signatures.
6. **Community Ground Truth**: Geo-verified citizen reports clustered through spatial-temporal deduplication.

### 2. Tactical Mountain Evacuation Routing
Integrates Border Roads Organisation (BRO) mountain highway corridors (NH-10, NH-717A) with hazard-aware Dijkstra/A* graphs:
- **Fastest Route**: Time-optimized corridor.
- **Shortest Route**: Distance-optimized corridor.
- **Safest Route**: Dynamic risk-penalized corridor actively circumventing active landslide sectors and swollen river crossings.

### 3. Edge Gateway & LoRa Mesh (Offline-First)
Designed for cloud-severed mountain valley operations:
- 34-byte compact binary LoRa packets with CRC-16-CCITT validation.
- Autonomous acoustic siren triggering with fail-safe dry-run modes.
- Local SQLite edge buffer synchronizing seamlessly with cloud PostGIS upon reconnection.

### 4. Multilingual & Standardized CAP Broadcasts
- Automated OASIS Common Alerting Protocol (CAP v1.2) XML payload dispatch.
- Multi-dialect warning engine supporting indigenous Himalayan languages: **Nepali, Lepcha, Bhutia, Hindi, and English**.
- Multi-channel failover: Dual-channel SMS, Voice alerts, Email, Web Push, and Acoustic Sirens with retry backoff and idempotency protection.

---

## Repository Structure

```
.
├── app.py                            # Core Flask application & REST API routes
├── backend/                          # Backend services, engines, routes, & edge subsystem
│   ├── edge/                         # Phase 3.4 Edge Gateway, LoRa mesh, siren controller
│   ├── notifications_routes.py       # Notification dispatch & audit endpoints
│   ├── realtime_routes.py            # Real-time CRI telemetry stream routes
│   ├── risk_engine.py                # Core risk engine and hazard evaluators
│   └── scheduler.py                  # Telemetry ingestion and background jobs
├── engine/                           # PAHAD scientific modeling core
│   ├── pahad_models.py               # Mohr-Coulomb FoS and CRI calculations
│   ├── pahad_fusion.py               # Multimodal fusion & evidence aggregation
│   ├── pahad_event_predictor.py      # Multi-horizon landslide probability models
│   ├── pahad_routing.py              # Mountain corridor routing algorithms
│   └── ...
├── services/                         # External integrations & notification adapters
│   ├── channel_failover_orchestrator.py # SMS / Email failover manager
│   ├── weather_service.py            # IMD & Open-Meteo meteorological pipeline
│   ├── seismic_service.py            # NCS & USGS seismic event monitor
│   └── unified_notification_service.py  # Unified alert dispatcher
├── templates/                        # Jinja2 Single Page Applications & GIS Dashboards
│   ├── index.html                    # Unified tactical operations console
│   ├── climate_map.html              # Weather & precipitation workspace
│   ├── seismic.html                  # Seismic monitor workspace
│   └── terrain_3d.html               # 3D DEM digital twin workspace
├── static/                           # Styles, vector maps, Leaflet / MapLibre assets
├── data/                             # Ground-truth catalogues, features, & observation DB
├── docs/                             # Engineering documentation, architectural dossiers, & reports
├── models/                           # Serialized ML artifacts & model metadata
├── parvat_netra_mobile/              # Flutter offline-first field agent application
├── tests/                            # Pytest test suite covering physics, security, & failover
├── Dockerfile                        # Production container specification
├── docker-compose.yml                # Multi-service stack (Flask + PostGIS)
└── requirements.txt                  # Python dependencies
```

---

## Getting Started

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git
- (Optional) Docker & Docker Compose
- (Optional) Flutter SDK for mobile application

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dimpu-sashank2008/parvatnetra.git
   cd parvatnetra
   ```

2. **Set up Python Virtual Environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your local credentials and API keys
   ```

5. **Run the Application:**
   ```bash
   python app.py
   ```
   Open your browser at `http://localhost:8080`.

### Docker Deployment

```bash
docker-compose up --build
```

---

## Testing & Verification

Run the automated test suite:

```bash
# Run all tests
pytest

# Run core geotechnical physics tests
pytest tests/test_pahad_engine.py

# Run alert notification & failover tests
pytest tests/test_phase10j_failover.py tests/test_phase10j_dual_channel.py
```

---

## Security & Integrity Protocol

- **Zero Hardcoded Credentials**: Strictly verified via `python mcp/scripts/validate_config.py`.
- **Data Provenance**: Every metric displays an explicit provenance badge (`[LIVE]`, `[SIMULATED]`, `[HISTORICAL]`, or `[DEMO]`).
- **2-of-3 Safety Consensus**: Public RED alerts strictly require affirmative confirmation across at least two independent telemetry modalities before dispatch.

---

## License & Compliance

Developed under the Smart India Hackathon (SIH) framework for National Disaster Management and Border Road Resiliency.
