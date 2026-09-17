# PARVAT NETRA • PAHAD AI — Phase 12F Provider Forensic Audit

**Audit Date**: September 16, 2026  
**Auditor**: PARVAT NETRA Core Forensic & Assurance Team  
**Problem Statement**: SIH 26001 (MDoNER)  
**Baseline Git Commit**: `fd1512af4f595e448b43bde0f8420e13514423bf`  

---

## 1. Executive Summary

This forensic audit evaluates the true runtime behavior, authentication state, provenance, and fallback mechanism for all 9 data streams integrated into the PARVAT NETRA / PAHAD AI platform.

### Authoritative Finding: Manifest Inconsistency Detected
In `data/manifests/phase12f_release_manifest.json`, the National Center for Seismology (`ncs_india`) was recorded as:
```json
"status": "LIVE",
"badge": "[LIVE]"
```
**Forensic Investigation Finding**: This entry is **INACCURATE**. The actual runtime service `NCSConnector` (`services/ncs_service.py`) verifies that `NCS_API_BASE_URL` is unconfigured in the environment. At runtime, `NCSConnector.verify_connection()` returns:
```json
{
  "status": "AUTH_REQUIRED",
  "ncs_status": "AUTH_REQUIRED",
  "authenticated": false,
  "fallback_provider": "USGS",
  "fallback_status": "ACTIVE"
}
```
While real-time seismic events are indeed ingested live, they originate from the **USGS Earthquake Hazards API** fallback, not an authenticated NCS stream. Marking NCS as `LIVE` constitutes a provider-level provenance inaccuracy.

---

## 2. Provider-by-Provider Forensic Matrix

| Provider | Runtime Status | Provenance Badge | Authentication State | Fallback Mechanism | Empirical Runtime Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NCS (National Center for Seismology)** | `AUTH_REQUIRED` | `[AUTH_REQUIRED]` | **UNAUTHENTICATED** (`NCS_API_BASE_URL` missing/empty) | Automatic fallback to **USGS FDSNws** | `NCSConnector().verify_connection()` returns `status: AUTH_REQUIRED`, `authenticated: False`, `error: NCS_API_BASE_URL is not configured in .env`. |
| **USGS Earthquake Hazards** | `LIVE` | `[LIVE]` | **PUBLIC / NO AUTH REQUIRED** | Local SQLite / GeoJSON cache | Queried `https://earthquake.usgs.gov/fdsnws/event/1/query`; HTTP `200 OK`, returned real M4.2 seismic event `us7000tgq0` (25 km NW of Sarupathar, India) inside NER bounding box. |
| **IMD (India Met Dept)** | `AUTH_REQUIRED` | `[AUTH_REQUIRED]` | **UNAUTHENTICATED** (`IMD_API_BASE_URL` and `IMD_API_TOKEN` missing) | Automatic fallback to **Open-Meteo GFS/ECMWF** | `IMDConnector().status` returns `AUTH_REQUIRED`; log: `IMD_API_BASE_URL or IMD_API_TOKEN is missing / placeholder. All fetch calls will return AUTH_REQUIRED.` |
| **Open-Meteo Weather** | `LIVE` | `[LIVE]` | **PUBLIC / NO AUTH REQUIRED** | Stored PostGIS / SQLite observation cache | Queried `https://api.open-meteo.com/v1/forecast?latitude=27.33&longitude=88.61`; HTTP `200 OK`, returned live precipitation `0.8 mm` and temperature `20.6 °C`. |
| **Copernicus CDSE (Sentinel-1)** | `HISTORICAL / PROCESSED` (Features) <br> `LIVE` (Metadata Search) <br> `AUTH_REQUIRED` (Raw Tiles) | `[HISTORICAL / PROCESSED]` | **CATALOG PUBLIC / DOWNLOAD AUTH REQUIRED** (`COPERNICUS_CLIENT_ID` missing) | Cached InSAR LOS velocity field in SQLite | CDSE OData catalogue search is publicly accessible. Raw SLC tile download is `AUTH_REQUIRED`. All InSAR displacement rates (-12.4 to +1.2 mm/yr) used by PAHAD AI are derived from processed historical Sentinel-1 interferograms. |
| **NRSC Bhoonidhi** | `HISTORICAL / CATALOG` | `[HISTORICAL]` | **UNAUTHENTICATED** (`BHOONIDHI_API_TOKEN` missing) | Local CartoDEM v3.1 / SRTM 30m cache | `EOCatalogConnector._is_bhoonidhi_configured()` returns `False`. Platform uses pre-processed CartoDEM 30m digital elevation model and historical optical baselines. |
| **In-Situ IoT (Piezometers / Inclinometers)** | `SIMULATED` | `[SIMULATED]` | **LOCAL / EMULATED** | Physics-based hydraulic infiltration model | `PHYSICAL FIELD DEPLOYMENT: NOT VERIFIED`. Pore-water pressure and inclinometer shear displacement are computed via van Genuchten SWCC and Mohr-Coulomb physics, not active hardware in hillsides. |
| **PostGIS Mountain Routing** | `LIVE` | `[LIVE]` | **AUTHENTICATED** (`SUPABASE_DB_URL` connected) | Deterministic in-memory Dijkstra graph | Supabase PostgreSQL 15 / PostGIS 3.6 connected; serves real road network topology and hazard-avoidance routing. |
| **Observation Store (SQLite)** | `LIVE` | `[LIVE]` | **LOCAL OS-LEVEL** | In-memory query buffer | SQLite database `data/observations/pahad_observations.db` connected; contains `117,218` stored observation rows. |

---

## 3. Deep-Dive: NCS vs. USGS Seismology Runtime Truth

### The Architecture
The seismic pipeline in PARVAT NETRA is architected with an explicit failover hierarchy:
```
Seismic Request
      │
      ▼
┌──────────────┐       Credentials Present?
│ NCSConnector ├─────────────────────────────────────────┐
└──────┬───────┘                                         │
       │ No (AUTH_REQUIRED)                              │ Yes
       ▼                                                 ▼
┌──────────────┐                                  ┌──────────────┐
│  USGS FDSNws │                                  │ Official NCS │
│  Public API  │                                  │ MoES Server  │
└──────┬───────┘                                  └──────────────┘
       │ Returns real M2.5+ events
       ▼
┌─────────────────────────────────┐
│ Event tagged:                   │
│ source = 'USGS'                 │
│ provenance = 'LIVE'             │
│ fallback_status = 'ACTIVE'      │
└─────────────────────────────────┘
```

### Forensic Evidence Log
Running `NCSConnector().verify_connection()` in the verified environment outputs:
```json
{
  "status": "AUTH_REQUIRED",
  "ncs_status": "AUTH_REQUIRED",
  "auth_state": "AUTH_REQUIRED",
  "provider": "National Center for Seismology (NCS, MoES)",
  "authenticated": false,
  "endpoint": null,
  "fallback_provider": "USGS",
  "fallback_status": "ACTIVE",
  "error": "NCS_API_BASE_URL is not configured in .env",
  "action_required": "Configure official NCS credentials in .env (NCS_API_BASE_URL and NCS_API_TOKEN)",
  "checked_at": "2026-09-16T08:42:02.502283+00:00"
}
```
**Conclusion**: NCS is legally and technically **`AUTH_REQUIRED`**. The live data stream is provided by USGS. Claiming NCS is `LIVE` in the manifest without credentials violates the platform's core Data Honesty Protocol.

---

## 4. IMD Nowcast vs. Open-Meteo Meteorological Truth

### Forensic Evidence Log
Running `IMDConnector()` in the verified environment produces:
```
[WARNING] IMDConnector: IMD_API_BASE_URL or IMD_API_TOKEN is missing / placeholder. All fetch calls will return AUTH_REQUIRED.
```
- Open-Meteo executes live queries to `https://api.open-meteo.com/v1/forecast` using ECMWF/GFS global models at 0.1° resolution.
- Live query for Gangtok (`27.33°N, 88.61°E`) returned `200 OK` with real-time temperature `20.6°C` and precipitation `0.8 mm`.
- **Conclusion**: The weather telemetry is genuinely **`[LIVE]`** via Open-Meteo, while IMD is accurately declared as **`[AUTH_REQUIRED]`**.

---

## 5. In-Situ IoT Ground Truth

- Physical hardware status: **`NOT VERIFIED / NOT INSTALLED`**
- Piezometers ($u$, pore-water pressure in kPa) and inclinometers ($\Delta x$, displacement in mm) are generated via physics simulation:
  $$u(t) = \gamma_w \cdot h_w(t) = \gamma_w \cdot \min(z, \alpha \cdot R_{24h})$$
- UI Badging: Strictly badged as `[SIMULATED]` across all cards and telemetry headers.
- **Conclusion**: Compliant with scientific honesty rules.

---

## 6. Audit Verdict
- **True LIVE Providers**: USGS Earthquake Hazards, Open-Meteo Weather, PostGIS Mountain Routing, SQLite Observation Store.
- **AUTH_REQUIRED Providers**: National Center for Seismology (NCS), India Meteorological Department (IMD), NRSC Bhoonidhi, Copernicus CDSE raw tile downloads.
- **HISTORICAL / PROCESSED Providers**: Copernicus Sentinel-1 InSAR LOS velocity deformation, ISRO CartoDEM v3.1.
- **SIMULATED Providers**: In-situ borehole geotechnical sensors (piezometers, inclinometers, tiltmeters).
