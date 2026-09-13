# PAHAD AI — Phase 5C Integration Audit
# Data Sources: CONNECTION STATUS & CREDENTIAL AUDIT

**Document**: `PHASE5C_INTEGRATION_AUDIT.md`
**Phase**: Phase 5C — Real Data Connectors & Continuous Live Operations
**Audit Date**: 2026-09-10
**Status**: PARTIALLY_OPERATIONAL

---

## 1. Overall System Status

```
PAHAD AI LIVE DATA STATUS
═══════════════════════════════════════════════════════════════

  Open-Meteo (Weather)  ................ LIVE (public API, no auth)
  USGS Earthquake API   ................ LIVE (public API, no auth)
  IMD Nowcast API       ................ AUTH_REQUIRED
  NCS Seismology API    ................ AUTH_REQUIRED (USGS fallback active)
  Copernicus CDSE       ................ CATALOGUE_ACCESSIBLE / DOWNLOAD_AUTH_REQUIRED
  NRSC Bhoonidhi        ................ AUTH_REQUIRED (MOU needed)
  IoT Gateway (MQTT)    ................ NOT_CONNECTED (no endpoint configured)
  Neon PostgreSQL       ................ CONNECTED (DATABASE_URL set)
  OmniRoute LLM         ................ CONFIGURED (localhost:20128)
  CWC River Telemetry   ................ NOT_CONNECTED

  Overall verdict: PARTIALLY_OPERATIONAL
  Real-time data: DEGRADED → relies on public APIs + cache
```

---

## 2. Source Audit Table

| SOURCE | STATUS | AUTH | CACHE | MOCK | BLOCKER | ACTION |
|--------|--------|------|-------|------|---------|--------|
| **Open-Meteo (Current Weather)** | `LIVE` | None (public) | YES | NO | None | Operational via weather_service.py |
| **Open-Meteo (Forecast)** | `LIVE` | None (public) | YES | NO | None | Operational via weather_service.py |
| **USGS FDSNws (Seismic)** | `LIVE` | None (public) | YES | NO | None | Operational via ncs_service.py & seismic_service.py |
| **IMD Nowcast / AWS** | `AUTH_REQUIRED` | Token required | YES (disk) | NO | Missing `IMD_API_TOKEN` & `IMD_API_BASE_URL` | Register at mausam.imd.gov.in, set credentials in `.env` |
| **NCS Seismology** | `AUTH_REQUIRED` | Token required | YES (disk) | NO | Missing `NCS_API_BASE_URL` | Request access from MoES NCS portal; USGS fallback active |
| **Copernicus CDSE (Catalogue)** | `LIVE` | None (public metadata) | YES | NO | None | OData search operational via eo_catalog_service.py |
| **Copernicus CDSE (Download)** | `AUTH_REQUIRED` | OAuth2 Credentials | NO | NO | Missing `COPERNICUS_CLIENT_ID` / `SECRET` | Register at dataspace.copernicus.eu for download access |
| **NRSC Bhoonidhi** | `AUTH_REQUIRED` | Institutional MOU | NO | NO | Missing `BHOONIDHI_API_URL` & `TOKEN` | Apply for institutional MOU at bhoonidhi.nrsc.gov.in |
| **IoT Telemetry Gateway (MQTT)** | `UNAVAILABLE` | Gateway Token | NO | NO | Missing deployed physical hardware & broker URL | Deploy LoRaWAN gateway and configure MQTT broker |
| **CWC River Hydrometry** | `UNAVAILABLE` | Dept API access | YES (historic) | NO | Official CWC REST endpoint unreleased | Request API access from CWC Teesta Basin Division |
| **Neon PostgreSQL** | `LIVE` | Connection URI | YES | NO | None | Operational via `DATABASE_URL` |
| **OmniRoute Local LLM** | `LIVE` | Local Port 20128 | YES | NO | None | Operational via `http://localhost:20128/v1` |

---

## 3. Credential Gaps (`.env` audit as of 2026-09-10)

The following credentials are **present**:
```
DATABASE_URL      ← Neon PostgreSQL (connected)
FLASK_PORT        ← 8080
OMNIROUTE_BASE_URL← http://localhost:20128/v1
OMNIROUTE_ENABLED ← true
```

The following credentials are **absent** (AUTH_REQUIRED):
```
IMD_API_BASE_URL  ← NOT SET
IMD_API_TOKEN     ← NOT SET
NCS_API_BASE_URL  ← NOT SET
NCS_API_TOKEN     ← NOT SET (optional; USGS fallback works without)
COPERNICUS_CLIENT_ID     ← NOT SET
COPERNICUS_CLIENT_SECRET ← NOT SET
IOT_GATEWAY_URL   ← NOT SET (default dummy value only)
IOT_GATEWAY_TOKEN ← NOT SET
BHOONIDHI_API_URL ← NOT SET
BHOONIDHI_API_TOKEN← NOT SET
```

---

## 4. Publicly Accessible APIs (No Auth Required)

These APIs are operational NOW with zero additional configuration:

| API | URL | What it provides |
|-----|-----|-----------------|
| **Open-Meteo** | `https://api.open-meteo.com/v1/forecast` | Hourly precipitation, temperature, wind; 7-day forecast |
| **USGS FDSNws** | `https://earthquake.usgs.gov/fdsnws/event/1/query` | Real-time earthquake events, NER bbox filter |
| **Copernicus CDSE Catalogue** | `https://catalogue.dataspace.copernicus.eu/odata/v1` | Sentinel-1/2 acquisition metadata search |

---

## 5. Auth-Gated APIs (Registration/MOU Required)

| API | How to Apply | Expected Timeline |
|-----|-------------|------------------|
| **IMD Nowcast API** | Contact IMD Director General at mausam.imd.gov.in/data-services | 4–8 weeks (GOI research/disaster MoU) |
| **NCS Earthquake API** | Ministry of Earth Sciences NCS portal: seismo.gov.in | 2–4 weeks |
| **Copernicus Download** | Register at dataspace.copernicus.eu (free account) | 1–2 days |
| **NRSC Bhoonidhi** | Apply via bhoonidhi.nrsc.gov.in (institutional registration) | 4–12 weeks |
| **CWC Hydrological** | Central Water Commission: cwc.gov.in/data-services | 6–12 weeks |

---

## 6. MCP Server Assessment

The following MCP servers are available in the development environment. **They are development tools, not live sensor data sources.**

| MCP Server | Purpose | PAHAD Use Case | Data Provided |
|-----------|---------|----------------|--------------|
| `neon-mcp-server` | Neon PostgreSQL management | Schema migrations, DB inspection | NONE (dev tool) |
| `firebase-mcp-server` | Firebase project management | Auth, Firestore rules | NONE for sensors |
| `chrome-devtools-mcp` | Browser testing/debugging | Frontend E2E tests | NONE |
| `github-mcp-server` | Repository management | CI/CD, PR management | NONE |
| `sequential-thinking` | Structured reasoning | Planning | NONE |
| `gemini-api-docs` | Gemini documentation | AI SDK integration | NONE |

**Critical note**: MCP servers do NOT provide real-time landslide, weather, or seismic sensor data. Real environmental data must come from IMD, NCS, USGS, Open-Meteo, or deployed IoT hardware.

---

## 7. Recommended Immediate Next Actions

**Priority 1 (can be done today — free):**
- [ ] Register at `dataspace.copernicus.eu` for Sentinel download access
- [ ] Verify USGS fallback works: `curl "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=2.5&minlatitude=20&maxlatitude=30&minlongitude=87&maxlongitude=98&limit=5"`

**Priority 2 (1–2 weeks):**
- [ ] Apply for NCS API access (seismo.gov.in)
- [ ] Apply for IMD Nowcast API (mausam.imd.gov.in/data-services)

**Priority 3 (institutional — 1–3 months):**
- [ ] Deploy LoRaWAN IoT gateway for piezometric sensors on NH-10 corridor
- [ ] Apply for NRSC Bhoonidhi institutional access
- [ ] Contact CWC for Teesta basin hydrological data

---

## 8. Functional Pipeline Status

```
PAHAD LIVE INFERENCE PIPELINE (current)

  Open-Meteo [LIVE]  ──→ weather_service.py ──→ rain_1h, rain_6h, rain_24h
  USGS [LIVE]        ──→ ncs_service.py     ──→ seismic_count_24h, max_magnitude
  GLO-30 DEM [CACHE] ──→ dem_service.py     ──→ slope, elevation, curvature
  IoT [MISSING]      ──→ device_gateway.py  ──→ pore_pressure, tilt (IMPUTED)
  Satellite [CACHE]  ──→ satellite_service  ──→ ndvi, ndvi_anomaly (IMPUTED)

  ↓
  PAHAD FoS Engine  (Mohr-Coulomb Infinite Slope)
  ↓
  Event Classifier  (Phase 5B GBDT, 4 horizons)
  ↓
  PAHAD Fusion      (CRI 0–100)
  ↓
  Alert Safety Gate (2-of-3 confirmation rule)
```
