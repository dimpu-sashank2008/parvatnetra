# PARVAT NETRA • Public Live-Risk GIS Release Report
**Document ID:** `reports/PUBLIC_LIVE_RISK_GIS_RELEASE_REPORT.md`  
**System:** PARVAT NETRA (NER Sentinel) — Live Risk GIS Operational Surface  
**Engine:** PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Target Environment:** Vercel Edge (`https://silly-fermi.vercel.app/`)  
**Evaluation Standard:** Strict Data Provenance, Non-Fabrication Protocol, SIH 26001  

---

## GIT
- **Local Branch:** `main`
- **Local SHA:** `c5964d8a19e97af6bc96470014ed344bfd1b36f2`
- **Remote SHA:** `c5964d8a19e97af6bc96470014ed344bfd1b36f2` (`origin/main`)
- **Match:** `YES (Exact 1:1 Parity)`
- **Commit Message:** `Enable verified live risk GIS`
- **Intended Files in Commit:**
  1. `backend/realtime_routes.py` (GeoJSON endpoint & serializer)
  2. `templates/index.html` (Map status strip, data status panel, 45s silent refresh, tactical markers, popups)
  3. `app.py` (Local submitted reports registry fallback)
  4. `tests/test_live_risk_map.py` (13/13 automated test suite)
  5. `reports/LIVE_RISK_GIS_IMPLEMENTATION_REPORT.md` (Implementation documentation)

---

## LOCAL TESTS
Comprehensive targeted test suite executed across all operational subsystems:
- **Total:** 56
- **Passed:** 56
- **Failed:** 0
- **Skipped:** 0
- **Errors:** 0
- **Pass Rate:** 100.0%
- **Execution Time:** 8.20s

### Breakdown of Test Modules:
- `tests/test_live_risk_map.py`: **13 / 13 PASSED** (GeoJSON structure, risk bands, Open-Meteo provenance, USGS provenance, simulated sensor disclaimer, derived CRI, viewport preservation, stale data handling, non-fake labels, zero layer duplication, safe fallback, citizen reporting, safety gates)
- `tests/test_map_viewport.py`: **6 / 6 PASSED** (Viewport sizing modes, full-screen toggle, scroll-wheel trap prevention, strict GIGW 3.0 vector icons)
- `tests/test_runtime_data_truth.py`: **7 / 7 PASSED** (Data classes validity, critical telemetry classification, Mohr-Coulomb physics, 2-of-3 false alarm suppression)
- `tests/test_authoritative_audit.py`: **5 / 5 PASSED** (47-row ledger parity, single authoritative data class per metric, CRI component tracing)
- `tests/test_pahad_engine.py`: **11 / 11 PASSED** (Infinite slope stability mechanics, NE Himalaya empirical rainfall thresholds, CRI band categorization, API endpoints)
- `tests/test_weather_service.py`: **7 / 7 PASSED** (Open-Meteo REST ingestion, fallback handling, rainfall intensity parsing)
- `tests/test_seismic_service.py`: **7 / 7 PASSED** (USGS GeoJSON parsing, NCS AUTH_REQUIRED state, hypocentral distance calculation)

---

## PUBLIC ENDPOINTS
Audit performed via live HTTPS requests against `https://silly-fermi.vercel.app/`:

| Endpoint | HTTP Status | Content-Type | Size (Bytes) | Runtime Source & Provenance | Public State |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | `200 OK` | `text/html; charset=utf-8` | 836,473 | Flask SSR Template | **STALE DEPLOYMENT** (Missing `#gis-map-status-strip`, `#gis-data-status-panel`, `currentRiskZonesLayerGroup`) |
| `/api/health` | `200 OK` | `application/json` | 302 | Live Flask Health Check | **CONNECTED** (Database: `CONNECTED`, PostGIS: `3.6 USE_GEOS=1`) |
| `/api/ml/latest-risk` | `200 OK` | `application/json` | 3,287 | Pretrained Geotech Model | **ACTIVE** (Evaluations: Gangtok Corridor, Teesta Valley) |
| `/api/pahad/realtime-cri` | `200 OK` | `application/json` | 40,038 | Realtime CRI Service | **ACTIVE** (20 sectors filed, lacks `?format=geojson` handler) |
| `/api/pahad/realtime-cri/geojson` | `404 Not Found` | `text/html` | — | Target GeoJSON Endpoint | **MISSING ON VERCEL** (Commit `c5964d8` not yet deployed) |
| `/api/seismic/latest` | `200 OK` | `application/json` | 307 | Seismic Service | **ACTIVE** (USGS Fallback feed) |
| `/api/weather/current` | `200 OK` | `application/json` | 256 | Weather Service | **ACTIVE** (Cached/live precipitation feed) |

---

## GIS
- **Current Risk Zones:** Locally fully operational across all 20 canonical corridors in the 8 NER states.
- **GeoJSON Structure:** Standard WGS84 GeoJSON `FeatureCollection` with zero invented coordinates (`21.0 <= lat <= 30.5`, `88.0 <= lon <= 97.5`).
- **Refresh Interval:** 45 seconds (`setInterval(..., 45000)`).
- **Viewport Preservation:** Strictly preserved. `loadCurrentRiskZones(isPeriodicRefresh=true)` updates markers and popups silently without calling `map.setView()` or `map.fitBounds()`.

---

## LIVE SOURCES
- **Weather / Precipitation:** Open-Meteo REST API (`LIVE_EXTERNAL`). Hourly rainfall intensity, 24h/72h antecedent rainfall, API 3d/7d.
- **Seismic Shaking:** USGS Earthquake Hazards Program GeoJSON (`LIVE_EXTERNAL`). Real-time $M \ge 2.5$ seismic events with hypocentral distances.
- **Citizen Reports:** Citizen field observation pipeline (`VERIFIED_FIELD`). PostGIS entry with DBSCAN clustering and CV distress classification.

---

## NON-LIVE SOURCES
- **Historical:** Copernicus Sentinel-1 InSAR LOS deformation velocities (`HISTORICAL`), GSI NLSM macro-zonation (`HISTORICAL`).
- **Static:** CartoDEM / Copernicus GLO-30 30m topographic slopes and curvatures (`STATIC_PREDEFINED`), Border Roads Organisation (BRO) highway network geometries (`STATIC_PREDEFINED`).
- **Simulated:** In-situ piezometer pore-water pressure and soil moisture content (`SIMULATED`, van Genuchten SWCC model). Mandatory disclaimer: *"Physical deployment not verified"*.
- **Pretrained:** GradientBoostingClassifier event probability classifier (`MODEL_PRETRAINED`). Metadata status: `TRAINED_LIMITED_DATA`.

---

## SAFETY
All statutory safety interlocks remain strictly locked and verified:
- **Public Alert Dispatch:** `ENABLE_PUBLIC_DISPATCH = 0`
- **Emergency Siren:** `SIREN_DRY_RUN = 1`
- **CAP Warning Dispatch:** `CAP_PRODUCTION_DISPATCH = 0`
- **NDMA Sachet Dispatch:** `SACHET_PRODUCTION_DISPATCH = 0`
- **Cell Broadcast Service:** `CELL_BROADCAST_PRODUCTION = 0`
- **Demo / Evaluation Mode:** `PUBLIC_DEMO_TEST_ONLY = 1`
- **Statutory Authority Requirement:** In strict adherence to the Disaster Management Act 2005 (Sections 30 & 34), mass public sirens and cellular notifications cannot be triggered autonomously; they mandate authenticated dual-key sign-off from the District Magistrate / SEOC Magistrate.

---

## DEPLOYMENT
- **Target Git Commit:** `c5964d8a19e97af6bc96470014ed344bfd1b36f2`
- **Vercel Deployment Status:** `VERCEL_VERIFICATION_PENDING`
- **Public URL:** `https://silly-fermi.vercel.app/`
- **Deployment Smoke Test:** **FAILED (Edge Out-of-Sync)**.
  - The public URL responds with HTTP 200, but is serving an older serverless build (`836KB` HTML).
  - The new GeoJSON endpoint `/api/pahad/realtime-cri/geojson` returns HTTP 404 on Vercel.
  - The deployed HTML does not yet contain `#gis-map-status-strip`, `#gis-data-status-panel`, or `currentRiskZonesLayerGroup`.

---

## LIMITATIONS
1. **Vercel Propagation Lag:** While commit `c5964d8` is confirmed on `origin/main` (GitHub API check: `c5964d8a19e97af6bc96470014ed344bfd1b36f2`), Vercel has not yet deployed this build to production.
2. **In-Situ Sensor Hardware:** In-situ slope sensors (pore pressure, borehole inclinometers) remain simulated via unsaturated soil mechanics due to lack of physical slope deployments.
3. **National Seismology Gateway:** NCS national gateway remains `AUTH_REQUIRED`; service falls back safely to the global USGS stream.
4. **Event Classifier Volume:** Event probability model is trained on limited NER historical ground-truth records (`TRAINED_LIMITED_DATA`).

---

## FINAL VERDICT
$$\mathbf{PUBLIC\_DEPLOYMENT\_NOT\_VERIFIED}$$

*While local execution is 100% verified (56/56 tests passing, GeoJSON functioning, and Git repository in exact parity with origin/main), forensic testing against `https://silly-fermi.vercel.app/` proves that Vercel has not yet finished building and deploying commit `c5964d8`. In strict adherence to data honesty protocols, deployment success cannot be claimed until the public edge actively serves the live risk GIS surface.*
