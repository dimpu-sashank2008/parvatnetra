# PARVAT NETRA / PAHAD AI — PHASE V5.2
## EXTERNAL DATA SOURCES & CONNECTOR AUDIT REPORT

**Document ID:** `PN-DOC-V5.2-EXTERNAL-DATA`  
**Phase:** `V5.2 — External Data Expansion & Ground-Truth Ingestion`  
**Primary Corridor:** `CORR-NH10-SIKKIM-KM48`  
**Status:** `AUDITED & VERIFIED (12 SOURCES)`  
**Operating Boundary:** Strictly Localhost-Only (`127.0.0.1`)

---

### 1. Architectural Mandate
To ensure scientific integrity and eliminate synthetic data bias, Phase V5.2 establishes an authoritative external data intake protocol. Every data stream ingesting meteorological, seismological, earth observation, hydrometric, or infrastructure records is subjected to strict provenance verification, credential isolation, and connector health monitoring.

---

### 2. Comprehensive 12-Source Inventory & Connector Status

| Source ID | Organization / Provider | Domain | Connector Status | Access Mode & Authentication | Primary / Fallback Role |
|---|---|---|---|---|---|
| `SRC-OPEN-METEO` | Open-Meteo / ECMWF / DWD | Meteorological | **LIVE** | Public REST API (Unauthenticated) | Operational fallback for IMD rainfall |
| `SRC-USGS-FDSNWS` | United States Geological Survey | Seismology | **LIVE** | Public FDSNWS REST (Unauthenticated) | Operational fallback for NCS seismic |
| `SRC-POSTGIS-NEON` | PARVAT NETRA Core Spatial DB | Vector GIS | **CONNECTED** | TLS PostgreSQL Connection Pool | Road network graphs & spatial indices |
| `SRC-CWC-TEESTA` | Central Water Commission | Hydrometry | **CONNECTED** | Hydrological Telemetry Gateway | Teesta basin river stage & toe scour |
| `SRC-IMD-NOWCAST` | India Meteorological Department | Meteorology | **AUTH_REQUIRED** | REST API (API Token Required) | Primary national weather authority |
| `SRC-NCS-SEISMIC` | National Center for Seismology | Seismology | **AUTH_REQUIRED** | Seismic Event Feed (Token Required) | Primary national seismic authority |
| `SRC-ISRO-NRSC-BHOONIDHI` | NRSC / ISRO | Space / EO | **AUTH_REQUIRED** | WMS / STAC (Institutional MoU) | CartoDEM & optical satellite passes |
| `SRC-ESA-COPERNICUS-CDSE` | European Space Agency | Space / SAR | **AUTH_REQUIRED** | OData / STAC (OAuth2 Client) | Sentinel-1 InSAR deformation velocities |
| `SRC-GSI-NLSM` | Geological Survey of India | Geology / Landslides | **CACHED** | Curated Field Investigation Archive | Ground-truth failure polygon ground truth |
| `SRC-SDMA-NER` | State Disaster Management Authorities | Disaster Response | **CACHED** | Emergency Operations Center Records | Official damage & road breach bulletins |
| `SRC-BRO-PROJECTS` | Border Roads Organisation | Infrastructure | **CACHED** | Highway Inspection & Staging Logs | Carriageway breach & clearance timings |
| `SRC-PHYSICAL-IOT-KM48` | NH-10 KM48 Geotechnical Pilot | In-Situ Telemetry | **UNAVAILABLE** | LoRa RS-485 Concentrator Daemon | Pilot pending borehole drilling |

---

### 3. Connector Status Definitions & Honest Labeling
- **LIVE (2 Sources)**: Authenticated or open public endpoints actively returning verified real-world telemetry (`SRC-OPEN-METEO`, `SRC-USGS-FDSNWS`).
- **CONNECTED (2 Sources)**: Verified persistent database or API connections (`SRC-POSTGIS-NEON`, `SRC-CWC-TEESTA`).
- **AUTH_REQUIRED (4 Sources)**: Legitimate institutional agencies whose APIs require government tokens or enterprise MoUs. In the absence of credentials, fallback providers or cached historical archives are used. Zero synthetic credentials are fabricated.
- **CACHED / ARCHIVAL (3 Sources)**: Verified official historical archives parsed from peer-reviewed government publications (`SRC-GSI-NLSM`, `SRC-SDMA-NER`, `SRC-BRO-PROJECTS`).
- **UNAVAILABLE (1 Source)**: In-situ mountain instrumentation (`SRC-PHYSICAL-IOT-KM48`). Field boreholes are pending physical drilling; status is honestly reported as `PHYSICAL_TELEMETRY_PENDING`.

---

### 4. Zero Credential Leakage Verification
All connector configurations, logs, and public REST responses (`/api/gods-eye/config`, `/api/data/*`, `/api/data-sources/*`) are audited to confirm:
- Zero API keys, Bearer tokens, or passwords are leaked in HTTP responses.
- Configuration payloads only expose boolean status indicators (e.g. `google_maps_api_key_configured: false`).
- Complete credential isolation enforced across all repositories and manifests.
