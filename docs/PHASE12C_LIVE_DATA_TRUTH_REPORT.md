# PARVAT NETRA / PAHAD AI — PHASE 12C
# Live Data Truth, Provider Status & Governance Audit

**Platform:** PARVAT NETRA — NER Sentinel  
**Component:** Multi-Provider Telemetry & Real-World Data Truth  
**Status:** `PHASE12C_LIVE_DATA_AUDITED`  
**Temporal Deep Learning Eligibility:** `DATA_COLLECTION_REQUIRED`  

---

## 1. Objective & Invariants
This document audits the operational status, latency, provenance, and failure behavior of all data providers integrated into PARVAT NETRA. It enforces complete transparency regarding data availability, sensor gaps, and artificial intelligence model capabilities.

---

## 2. Multi-Provider Ingestion Status Matrix
PARVAT NETRA ingests from 9 distinct data providers and services:

| Provider / Feed | Data Type | Latency | Canonical Status | Fallback Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **1. IMD AWS Precipitation** | Automatic Weather Station rainfall | 15 min | `LIVE` | Open-Meteo API / Climatology |
| **2. Open-Meteo ECMWF/GFS** | Numerical Weather Prediction | 1 hr | `LIVE` | Cached grid / Persistence |
| **3. NCS Earthquakes** | National Center for Seismology | Real-time | `LIVE` | USGS Global Hazards Feed |
| **4. USGS Global Hazards** | Worldwide seismic telemetry | Real-time | `LIVE` | Regional seismic attenuation |
| **5. Copernicus Sentinel-1/2** | InSAR deformation & S2 NDVI | 6–12 days | `LIVE` | Persistent baseline deformation |
| **6. ISRO NRSC / Bhoonidhi** | High-res optical & hazard maps | Seasonal | `HISTORICAL` | Static GSI NLSM polygons |
| **7. In-Situ Geotechnical IoT** | Piezometer, Inclinometer, Tilt | 10 sec | `SIMULATED` | Deterministic hydrostatic physics |
| **8. PostGIS Spatial Graph** | Road network, corridors, terrain | Query-time | `LIVE` | SQLite offline spatial cache |
| **9. SQLite Embedded Storage** | Local operational fallback DB | Immediate | `LIVE` | In-memory RAM dictionary |

---

## 3. Active Fallback & Degradation Flags
When upstream APIs experience downtime, network timeouts, or rate limits, the system exposes explicit operational fallback flags:
- `weather_fallback_active`: Set to `True` when IMD AWS telemetry fails and Open-Meteo or climatological reanalysis is substituted.
- `seismic_fallback_active`: Set to `True` when NCS national feed is unreachable and USGS or regional attenuation model is used.
- `sqlite_fallback_active`: Set to `True` when remote PostgreSQL / PostGIS connection drops and local SQLite spatial database takes over.

---

## 4. Honest Disclosure on Temporal Deep Learning
In strict compliance with Phase 12A and Phase 12B findings:
1. **PAHAD LSTM / GRU Status:** `PHYSICS-INFORMED TEMPORAL SURROGATE / NOT TRAINED`
2. **Current Telemetry State:** Continuous real sensor time-series sequences remain at **0**.
3. **Deep Learning Training Eligibility:** `DATA_COLLECTION_REQUIRED`
4. **Current Event Classifier:** Scikit-learn Gradient Boosting Classifier (`TRAINED_LIMITED_DATA`, $N=17$ historical NER landslide events).

Under NO circumstances does the system claim an LSTM or GRU is trained or executing neural inference.
