# PHASE 6B — INSTITUTIONAL DATA COMMISSIONING AUDIT

**Project**: PARVAT NETRA / PAHAD AI  
**Milestone**: Phase 6B — Institutional Data Commissioning & Real Sensor Acceptance  
**Status**: IN_PROGRESS  
**Generated At**: 2026-09-10T19:58:00Z  

---

## 1. Executive Summary

This audit establishes the rigorous operational and data reality for all external institutional and physical sensor feeds integrated into the PARVAT NETRA platform.

In compliance with core project rules:
- **Zero Fabrication**: No credentials, API tokens, simulated sensor nodes, or fake government connectivity are claimed as `LIVE`.
- **Explicit Auth State**: Connectors lacking production API keys explicitly report `status = AUTH_REQUIRED` without fabricating data or claiming live status.
- **Provider Segregation**: Fallback data sources (e.g. USGS public seismic feeds, Open-Meteo precipitation) are strictly segregated from sovereign Indian institutional nodes (IMD, NCS, ISRO/NRSC, CWC) and retain explicit source attribution.
- **Physical Sensor Pre-Conditions**: Physical field sensors must pass an 8-stage verification workflow (`REGISTER` $\to$ `INSTALL` $\to$ `CALIBRATE` $\to$ `CONNECT` $\to$ `HEARTBEAT` $\to$ `TELEMETRY` $\to$ `VALIDATE` $\to$ `ACCEPT`) before transitioning from `NOT_DEPLOYED` to `ACTIVE`.

---

## 2. Institutional Data Source Matrix

| SOURCE | CURRENT STATUS | AUTH REQUIRED | CONNECTOR | TESTED | BLOCKER | NEXT ACTION |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IMD (Nowcast / AWS / ARG)** | `AUTH_REQUIRED` | Yes (`IMD_API_BASE_URL`, `IMD_API_TOKEN`) | `services/imd_service.py` (`IMDConnector`) | Yes (mocked + unit) | Official MoES/IMD API access credentials not yet provisioned | Obtain official API endpoint and bearer token from IMD; keep `AUTH_REQUIRED` state honest |
| **IMD District Warnings** | `AUTH_REQUIRED` | Yes (`IMD_API_BASE_URL`, `IMD_API_TOKEN`) | `services/imd_service.py` (`fetch_warnings`) | Yes (mocked + unit) | MoES credentials absent | Request institutional API clearance; use deterministic thresholding fallback |
| **Open-Meteo Weather** | `LIVE` (Public Fallback) | No | `services/weather_service.py` (`OpenMeteoProvider`) | Yes (automated) | None (Public API, non-sovereign) | Maintain as secondary fallback with explicit `source="Open-Meteo"` attribution |
| **NCS (National Center for Seismology)** | `AUTH_REQUIRED` | Yes (`NCS_API_BASE_URL`, `NCS_API_TOKEN`) | `services/ncs_service.py` (`NCSConnector`) | Yes (mocked + unit) | MoES NCS real-time API endpoint unconfigured in `.env` | Provision official NCS access; never mislabel USGS records as NCS |
| **USGS Seismic FDSNws** | `LIVE` (Public Fallback) | No | `services/ncs_service.py` (`_fetch_from_usgs`) | Yes (automated) | Secondary non-Indian catalog; NER Himalayan bbox filter | Continue auto-fallback with strict `source="USGS"` and `provenance="LIVE"` |
| **Copernicus Sentinel-1 SAR** | `CATALOGUE_DISCOVERY` | Yes for download (`COPERNICUS_CLIENT_ID/SECRET`) | `services/satellite_service.py` | Yes (static catalog) | Copernicus CDSE API credentials unconfigured | Segregate 4-stage pipeline; mark download as `AUTH_REQUIRED` |
| **Copernicus Sentinel-2 MSI** | `CATALOGUE_DISCOVERY` | Yes for download (`COPERNICUS_CLIENT_ID/SECRET`) | `services/satellite_service.py`, `services/vegetation_service.py` | Yes (catalog + baseline) | Raw tile download requires CDSE token | Ingest static 10m L2A products until CDSE credentials provisioned |
| **ISRO NISAR / Bhoonidhi** | `CATALOGUE_DISCOVERY` | Yes (`ISRO_BHOONIDHI_API_KEY`) | `services/satellite_service.py` | Yes (catalog) | Bhoonidhi API credentials absent | Maintain footprint discovery; mark raw processing as `PENDING_UNWRAP` |
| **CartoDEM / Copernicus GLO-30** | `CACHED` | No (local raster cache) | `services/dem_service.py` (`DEMService`) | Yes (automated) | None (Local 30m GeoTIFF cache present) | Support dynamic slope/aspect extraction from GLO-30 tiles |
| **CWC Teesta River Hydro** | `SIMULATED_PHYSICS` | Yes for real-time SCADA (`CWC_SCADA_URL`) | `services/cwc_sync.py` (`CWCTeestaHydroService`) | Yes (automated) | Physical telemetry link to Teesta-V Dam gauge pending | Run hydrodynamic basal shear stress physics model; flag as `[SIMULATED]` |
| **In-Situ Geotechnical IoT** | `FIELD_INFRASTRUCTURE_READY` | Yes (Node tokens / LoRa AppKey) | `services/telemetry_contract.py`, `engine/sensor_registry.py` | Yes (52 tests passed) | Physical sensors pending on-site installation at NH-10 Km 48 | Enforce 8-stage sensor acceptance CLI; preserve `NOT_DEPLOYED` status |

---

## 3. Credential Reality Audit

The current deployment environment (`.env`) was verified:

```env
DATABASE_URL=postgresql://neondb_owner:***@44.206.211.72/neondb (CONFIGURED)
NEON_DB_URL=postgresql://neondb_owner:***@44.206.211.72/neondb (CONFIGURED)
FLASK_PORT=8080 (CONFIGURED)
OMNIROUTE_BASE_URL=http://localhost:20128/v1 (CONFIGURED)
OMNIROUTE_ENABLED=true (CONFIGURED)
OMNIROUTE_MODEL=default (CONFIGURED)

# GAPS IDENTIFIED:
IMD_API_BASE_URL=NOT_SET
IMD_API_TOKEN=NOT_SET
NCS_API_BASE_URL=NOT_SET
NCS_API_TOKEN=NOT_SET
COPERNICUS_CLIENT_ID=NOT_SET
COPERNICUS_CLIENT_SECRET=NOT_SET
ISRO_BHOONIDHI_API_KEY=NOT_SET
CWC_SCADA_URL=NOT_SET
IOT_GATEWAY_AUTH_KEY=NOT_SET
```

### Action Plan for Missing Credentials
1. **IMD**: System operates in `AUTH_REQUIRED` mode. When `IMD_CONNECTOR.fetch_observations()` is invoked, it yields structured `IMDObservation` objects with `provenance="AUTH_REQUIRED"`, `quality="AUTH_REQUIRED"`, and `value=None`. Weather fallback transparently switches to Open-Meteo with explicit provenance `[LIVE / OPEN_METEO]`.
2. **NCS**: Connector reports `status="AUTH_REQUIRED"` for NCS primary, while activating USGS public API fallback with `source="USGS"`.
3. **Copernicus/ESA**: Satellite service strictly separates `CATALOGUE_DISCOVERY` from `DOWNLOAD`. Footprints and metadata are visible; raw scene download reports `status="AUTH_REQUIRED"`.
4. **Physical IoT**: Sensor registry defaults all physical sensor records to `NOT_DEPLOYED` or `SIMULATED` until authenticated field commissioning succeeds.

---

## 4. Operational Safety & Shadow Mode Verification

In pre-commissioning pilot environments, unverified AI models or experimental sensor nodes must **never** trigger panic through false alarms:
- `PAHAD_SHADOW_MODE=1` enforces strict public alert suppression.
- The platform computes all machine learning inference, Infinite Slope Factor of Safety ($FoS$), Composite Risk Index ($CRI$), and evacuation routes.
- If thresholds are exceeded, the recommendation is recorded in `shadow_alert_log` with `status = "SUPPRESSED_SHADOW_OPERATIONS"`, while external sirens, SMS, and CAP broadcasts are bypassed.

---

## 5. Acceptance Criteria Checklist

- [x] Pre-implementation audit completed with exact credential reality.
- [ ] IMD connector enhanced with HTTPAdapter retry/backoff, station/district mapping, and `verify_connection()`.
- [ ] NCS connector explicitly segregating `AUTH_REQUIRED` NCS from `LIVE` USGS.
- [ ] Satellite service upgraded to 4-tier pipeline (`CATALOGUE_DISCOVERY`, `DOWNLOAD`, `PROCESSING`, `FEATURE_READY`).
- [ ] Physical sensor acceptance CLI (`scripts/commission_sensor.py`) enforcing 8-stage verification.
- [ ] Telemetry validator rejecting unknown devices and expired calibrations.
- [ ] `GET /api/institutional/data-health` endpoint returning comprehensive multi-source status.
- [ ] `POST /api/alerts/broadcast-trigger` and shadow inference enforcing `SUPPRESSED_SHADOW_OPERATIONS`.
- [ ] 5 required test suites passing with zero regression.
