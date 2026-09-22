# PARVAT NETRA / PAHAD AI — PHASE V5.2
# CONNECTOR AUTHENTICATION & CREDENTIAL AUDIT REPORT

**Document ID:** `PN-DOC-V5.2-CONN-AUTH`  
**Phase:** `V5.2`  
**Status:** `AUDITED`

---

## 1. Executive Summary
This report audits the authentication, authorization, and connectivity mechanisms for national and international institutional connectors. 

## 2. Institutional Provider Authentication States

### 2.1 India Meteorological Department (IMD)
- **Source ID:** `SRC-IMD-NOWCAST`
- **Authentication State:** `AUTH_REQUIRED`
- **Audit Findings:** `IMD_API_BASE_URL` and `IMD_API_TOKEN` are not populated in the development/staging environment.
- **Operational Policy:** Under the Zero-Fabrication Directive, PARVAT NETRA engages the operational fallback pipeline (`SRC-OPEN-METEO`). In accordance with the Anti-Relabeling Invariant, Open-Meteo data is transparently tagged `[LIVE / OPEN-METEO]` and is never presented to operators as IMD AWS data.

### 2.2 National Center for Seismology (NCS)
- **Source ID:** `SRC-NCS-SEISMIC`
- **Authentication State:** `AUTH_REQUIRED`
- **Audit Findings:** `NCS_API_BASE_URL` is unconfigured.
- **Operational Policy:** Fallback pipeline (`SRC-USGS-FDSNWS`) handles regional earthquake catalog queries within the NER bounding box ($20.0^\circ\text{--}30.5^\circ\text{N}, 87.0^\circ\text{--}98.0^\circ\text{E}$). All seismic events carry explicit USGS provenance tags.

### 2.3 ISRO NRSC Bhoonidhi Geoportal
- **Source ID:** `SRC-ISRO-NRSC-BHOONIDHI`
- **Authentication State:** `AUTH_REQUIRED`
- **Audit Findings:** Requires institutional MOU execution with NRSC Balanagar, Hyderabad.
- **Operational Policy:** Offline high-resolution CartoDEM and GSI NLSM morphological vectors serve as cached baseline layers.

### 2.4 ESA Copernicus Data Space Ecosystem (CDSE)
- **Source ID:** `SRC-ESA-COPERNICUS-CDSE`
- **Authentication State:** `AUTH_REQUIRED` (for raw SLC downloads) / `METADATA_DISCOVERY_CAPABLE`
- **Audit Findings:** Public OData and STAC catalog discovery is active; automated product downloads require registered OAuth2 client credentials.
- **Operational Policy:** Cached Copernicus GLO-30 Digital Elevation Models provide terrain curvature, slope, and aspect.

---

## 3. Physical In-Situ IoT Isolation
- **Source ID:** `SRC-PHYSICAL-IOT-KM48`
- **Status:** `UNAVAILABLE`
- **Physical Sensors Verified:** 0
- **Borehole Casings Installed:** 0
- **Live Field Telemetry Observations:** 0
- **Strict Boundary:** Bench HIL simulated records are completely quarantined. In-situ ML status remains `NOT_TRAINED_DATA_PENDING`.
