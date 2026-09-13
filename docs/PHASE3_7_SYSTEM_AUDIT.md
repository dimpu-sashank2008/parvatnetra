# PARVATNETRA + PAHAD AI — PHASE 3.7 SYSTEM AUDIT

**Audit Date**: September 2026  
**Document ID**: `PAHAD-AUDIT-PHASE3-7`  
**Classification**: Engineering Diagnostic & Readiness Audit  
**Standard**: SIH-26001 / NDMA National Early Warning Standard  
**Objective**: Comprehensive verification of operational readiness, classifying all subsystems into `REAL`, `CACHED`, `SIMULATED`, `PLACEHOLDER`, or `NOT IMPLEMENTED`.

---

## 1. System Inventory & Classification Matrix

| Subsystem | Primary Implementation | Current Operational Status | Evidence & Runtime Behavior |
| :--- | :--- | :--- | :--- |
| **Data Registry & Provenance** | `services/data_provenance.py` | **REAL** | Provenance tags (`[LIVE]`, `[HISTORICAL]`, `[CACHED]`, `[SIMULATED]`, `[MISSING]`) tracked per feature. |
| **Cache Management Layer** | `services/cache_manager.py` | **REAL / PERSISTENT** | File-backed cache in `data/cache/` with TTL expiry, staleness detection, and background refresh. |
| **Ingestion Manager** | `services/ingestion_manager.py` | **REAL** | Unified multi-source pipeline pulling IMD/AWS, NCS, Copernicus DEM, and IoT telemetry. |
| **Weather / Precipitation** | `services/weather_service.py` | **REAL (LIVE + CACHED)** | IMD API + Open-Meteo live machine-readable feed. Automatic fallback to local cache (`data/cache/weather/`). |
| **Seismic Intelligence** | `services/seismic_service.py` | **REAL (LIVE + CACHED)** | NCS catalog + USGS real-time GeoJSON API within Himalayan bbox ($20.0^\circ\text{–}30.0^\circ\text{N}$, $87.0^\circ\text{–}98.0^\circ\text{E}$). |
| **Terrain / DEM** | `services/dem_service.py` | **REAL (HISTORICAL/CACHED)** | Copernicus GLO-30 and CartoDEM raster processing; computes elevation, slope, aspect, curvature, TRI. |
| **Vegetation Remote Sensing** | `services/vegetation_service.py` | **REAL (HISTORICAL/CACHED)** | Sentinel-2 L2A BOA 10m NDVI and temporal delta calculations; explicit cloud/quality scoring. |
| **Historical Landslide Inventory** | `services/landslide_inventory_service.py` | **REAL (HISTORICAL)** | GSI NLSM official inventory ($N = 17$ positive events, $N = 19$ verified controls) across 8 NER states. |
| **Satellite Radar / InSAR** | `services/satellite_service.py` | **REAL (METADATA + CACHED)** | Sentinel-1 SAR footprint and orbit metadata. When local SAR interferometry is offline, returns `PROCESSING NOT AVAILABLE`. |
| **IoT / Borehole Sensors** | `services/device_gateway.py` | **REAL (DEVICE ABSTRACTION)** | In-situ telemetry for vibrating-wire piezometers, extensometers, inclinometers, and rain gauges. |
| **Device Gateway Protocol** | `services/device_gateway.py` | **REAL** | Standardized packet adapter for HTTP REST, LoRaWAN JSON, and BLE beacon framing. |
| **Geotechnical FoS Engine** | `engine/pahad_models.py` | **REAL (PHYSICS ENGINE)** | Infinite-slope Mohr-Coulomb limit equilibrium model. Categorizes FoS: $> 1.5$ (STABLE), $1.0\text{–}1.5$ (WATCH), $\le 1.0$ (CRITICAL). |
| **Landslide Event ML Model** | `engine/pahad_event_predictor.py` | **REAL (RESEARCH PROTOTYPE)** | Calibrated GradientBoostingClassifier trained on leak-free temporal partitions (`models/pahad_event_model.pkl`). |
| **Multi-Horizon Prediction** | `engine/pahad_event_predictor.py` | **REAL** | Predicts across $6\text{h}$, $12\text{h}$, $24\text{h}$, and $48\text{h}$ with calibrated uncertainty. |
| **PAHAD Fusion Engine** | `engine/pahad_fusion.py` | **REAL** | Multi-signal fusion calculating Composite Risk Index (CRI), combining FoS, rainfall triggers, and ML event probability under the 2-of-3 rule. |
| **Confidence & Evidence Engine** | `engine/pahad_fusion.py` | **REAL** | Confidence is decoupled from risk; evaluated based on data completeness, source freshness, and signal agreement. |
| **Alert Lifecycle Engine** | `engine/pahad_alert_policy.py` | **REAL** | Full 8-state lifecycle: `DETECTED` $\to$ `EVALUATING` $\to$ `VERIFIED` $\to$ `ISSUED` $\to$ `ACKNOWLEDGED` $\to$ `ESCALATED` $\to$ `RESOLVED` $\to$ `EXPIRED`. |
| **15 km Geofenced Targeting** | `engine/pahad_geofence.py` | **REAL** | Circular, corridor, and polygon geofences calculating affected population, roads, bridges, and hospitals. |
| **Notification Orchestrator** | `engine/pahad_notification_orchestrator.py`| **REAL** | Multi-channel dispatch (PUSH, SMS, EMAIL, WEB, CAP, SIREN, LOCAL_GATEWAY) with delivery tracking (`queued`, `sent`, `delivered`, `failed`). |
| **CAP Alert Generation** | `engine/pahad_cap.py` | **REAL** | Generates compliant OASIS CAP v1.2 XML alerts with digital signatures and NDMA SACHET schema compatibility. |
| **Evacuation Routing Engine** | `engine/pahad_routing.py` | **REAL** | Network graph Dijkstra/A* routing penalizing active hazard polygons and road-block incidents across NH-10 and NH-717A. |
| **Offline-First Architecture** | `services/sync_service.py` | **REAL** | Service worker manifests, offline data packages in `data/cache/offline/`, client SQLite sync queue. |
| **Mobile Integration API** | `app.py` (`/api/mobile/*`) | **REAL** | REST endpoints for Flutter mobile field clients: telemetry, offline sync, citizen SOS, and photo dispatch. |
| **Local Last-Mile Siren Gateway** | `engine/pahad_alert_gateway.py` | **REAL** | Local edge gateway protocol with LoRa mesh simulation, hardware siren relay activation, and acknowledgement tracking. |
| **3D Digital Terrain Observatory** | `templates/pahad_ai.html` | **REAL (WebGL/Three.js)** | Interactive 3D hillslope canvas, layer toggles, real DEM mesh elevation, and multimodal evidence streams. |
| **Security & RBAC** | `app.py` & `.env` | **REAL** | Environment-based secrets, token headers, RBAC (`PUBLIC`, `FIELD_OPERATOR`, `AUTHORITY`, `ADMIN`), audit logs. |
| **Observability & Logging** | System-wide Python `logging` | **REAL** | ISO 8601 structured logs with request IDs, component prefixes, and latency measurements. |
| **Database Persistence** | SQLite / PostGIS | **REAL** | Relational schemas for users, alerts, sensor observations, field reports, and model audit records. |

---

## 2. Detailed Gap Analysis & Action Items for Phase 3.7

1. **Unified Data Layer**:
   - Build `services/data_registry.py` to formalize multi-source observation schemas.
   - Build `services/cache_manager.py` with disk persistence in `data/cache/` to guarantee that offline/network failures never crash production inference.
   - Build `services/device_gateway.py` providing hardware-agnostic ingestion for piezometers, inclinometers, and rain gauges.
2. **Dataset Expansion Pipeline**:
   - Implement `scripts/ingest_historical_events.py` and `scripts/build_event_dataset.py` to support programmatic expansion beyond initial pilot corridors.
3. **End-to-End Integration Test**:
   - Implement `tests/test_pahad_end_to_end.py` verifying the complete operational chain:
     $$\text{Sensor / Weather Ingestion} \to \text{FoS} \to \text{Event ML} \to \text{PAHAD Fusion} \to \text{Alert Policy} \to \text{15km Geofence} \to \text{Notification} \to \text{Evacuation Route}$$
4. **Comprehensive Documentation**:
   - Author complete architectural runbooks and manuals in `docs/`.

---

## 3. System Integrity & Safety Assurance

- **Zero Silent Fallback**: When an external provider (IMD, NCS, or Sentinel) is unreachable, the system transparently reports `[CACHED]` (with explicit `last_updated` timestamp and `data_age_seconds`) or `[UNAVAILABLE]`.
- **Demo Mode Isolation**: Synthetic demo records remain strictly restricted to `PAHAD_DEMO_MODE=1` and are never admitted into production models.
- **2-of-3 Safety Corroboration**: No automated public siren or CAP dispatch occurs without independent corroboration between physical mechanics ($FoS$), meteorological triggers ($R_{24\text{h}}$), and ML event probability ($P \ge 0.70$).
