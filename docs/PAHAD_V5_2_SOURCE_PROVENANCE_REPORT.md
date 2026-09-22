# PARVAT NETRA / PAHAD AI — PHASE V5.2
## SOURCE PROVENANCE & CITATION AUDIT REPORT

**Document ID:** `PN-DOC-V5.2-SOURCE-PROVENANCE`  
**Phase:** `V5.2 — External Data Expansion & Ground-Truth Ingestion`  
**Primary Corridor:** `CORR-NH10-SIKKIM-KM48`  
**Status:** `VERIFIED AUTHORITATIVE`  
**Operating Boundary:** Strictly Localhost-Only (`127.0.0.1`)

---

### 1. Provenance Badge Invariant
In strict accordance with the PARVAT NETRA Core Constitution, every metric, map layer, and incident record is assigned a binding provenance indicator:

- `[LIVE]`: Authenticated real-time sensor stream or verified open API feed.
- `[HISTORICAL]`: Archival ground truth from official Geological Survey of India (GSI), State Disaster Management Authority (SDMA), or Border Roads Organisation (BRO) field investigations.
- `[SIMULATED]`: Statistically realistic physics simulation based on empirical rainfall or bench hardware-in-the-loop (HIL) fixtures.
- `[DEMO]`: Synthetic walkthrough sequences strictly quarantined for evaluator inspection (`PAHAD_DEMO_MODE=1`).

---

### 2. Provenance Audit of Canonical Ground Truth
The Phase V5.2 dataset expansion evaluated 45 candidate landslide records. Following deduplication and multi-source corroboration, exactly **42 canonical landslide events** were admitted:

- **100% of canonical events** bear the `[HISTORICAL]` provenance badge.
- **Zero synthetic or simulated records** are admitted into canonical operational sets (`data/processed/canonical_event_inventory_v5_2.json`).
- All 42 canonical events feature primary institutional source citations:
  - GSI Special Disaster Investigation Reports (e.g., `GSI-NER-SK-2023-014`, `GSI-NER-MN-2022-004`)
  - SDMA Emergency Operations Bulletins (e.g., `SSDMA-SITREP-2023-10-04`, `ASDMA-FR-2024-071`)
  - BRO Road Clearance & Carriageway Breach Registers (e.g., `BRO-SWASTIK-NH10-LOG-2023`)

---

### 3. Institutional Licensing & Compliance
- **GSI / Ministry of Mines**: National Landslide Susceptibility Mapping (NLSM) open government data access.
- **Open-Meteo**: Open Data Commons Open Database License (ODbL) / CC BY 4.0.
- **USGS**: US Government Public Domain Open Access.
- **ISRO / NRSC Bhoonidhi**: Academic & Institutional Data Sharing Agreement.
- **ESA Copernicus**: Free, full, and open data policy under Regulation (EU) No 377/2014.
- **CWC / Ministry of Jal Shakti**: National Hydrology Project Open Hydrometric Telemetry.
