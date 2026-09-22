# PARVAT NETRA / PAHAD AI — PHASE V5.2
# EXTERNAL DATA SOURCE REGISTRY & METADATA AUDIT

**Document ID:** `PN-DOC-V5.2-SRC-AUDIT`  
**Phase:** `V5.2`  
**Status:** `AUDITED & VERIFIED`

---

## 1. Registry Overview
Phase V5.2 formalizes the twelve (12) external telemetry and archival data providers powering PARVAT NETRA. Every provider is cataloged with organization ownership, access mechanism, licensing terms, and operational status.

| Source ID | Organization | Type | Access Method | Auth State | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SRC-GSI-NLSM` | Geological Survey of India (GSI) | Geological Agency | Curated Archive & Portal | Open Government Data | `CACHED` |
| `SRC-ISRO-NRSC-BHOONIDHI` | National Remote Sensing Centre (ISRO) | Space Agency Geoportal | REST API & WMS | Institutional MOU Required | `AUTH_REQUIRED` |
| `SRC-IMD-NOWCAST` | India Meteorological Department (IMD) | Meteorological Agency | REST API | Token Required | `AUTH_REQUIRED` |
| `SRC-OPEN-METEO` | Open-Meteo Services / ECMWF & DWD | Public Weather API | Public REST API | Public Access | `LIVE` |
| `SRC-NCS-SEISMIC` | National Center for Seismology (NCS) | Seismological Agency | REST API | Token Required | `AUTH_REQUIRED` |
| `SRC-USGS-FDSNWS` | United States Geological Survey (USGS) | Global Seismic API | Public FDSNws API | Public Access | `LIVE` |
| `SRC-ESA-COPERNICUS-CDSE` | European Space Agency (ESA) Copernicus | Earth Observation | OData & STAC API | OAuth2 Required for SLC | `AUTH_REQUIRED` |
| `SRC-SDMA-NER` | State Disaster Management Authorities | State Disaster Agencies | Official Communiques | Verified State Records | `CACHED` |
| `SRC-BRO-PROJECTS` | Border Roads Organisation (BRO) | Infrastructure Agency | Road Dispatch Registers | Verified Defence Records | `CACHED` |
| `SRC-CWC-TEESTA` | Central Water Commission (CWC) | Hydrological Agency | Hydrometry Feed | Open Hydrology Portal | `CONNECTED` |
| `SRC-POSTGIS-NEON` | Core Spatial Database | Internal Vector Store | PostgreSQL Pool | Authenticated Pool | `CONNECTED` |
| `SRC-PHYSICAL-IOT-KM48` | NH-10 KM48 Field Pilot | In-Situ Telemetry | LoRa / RS-485 Daemon | Hardware Pending | `UNAVAILABLE` |

---

## 2. Invariants & Status Rules
1. **LIVE Status:** Only assigned to endpoints with authenticated or open public query responses verified during runtime testing (Open-Meteo, USGS).
2. **AUTH_REQUIRED Status:** Assigned to legitimate institutional providers where local `.env` lacks official API tokens or signed MOUs. Under no circumstances are tokens faked.
3. **UNAVAILABLE Status:** Strictly enforced for physical sensors where boreholes are not yet drilled.
