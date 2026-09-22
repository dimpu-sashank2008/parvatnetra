# PARVAT NETRA / PAHAD AI — PHASE V5.2 CHARTER
# AUTHORITATIVE EXTERNAL DATA EXPANSION, CREDENTIALED CONNECTOR VALIDATION & GROUND-TRUTH GROWTH

**Document ID:** `PN-DOC-V5.2-CHARTER`  
**Phase:** `V5.2`  
**Status:** `RATIFIED`  
**Classification:** `SCIENTIFIC DATA ENGINEERING SPECIFICATION`  
**Target Authority:** Geological Survey of India (GSI), Border Roads Organisation (BRO), State Disaster Management Authorities (SDMAs)

---

## 1. Executive Mandate
Phase V5.2 expands PARVAT NETRA's scientifically defensible historical dataset and connector infrastructure without violating the canonical truth ledger established in Phase V5.1. 

The primary goals of this phase are:
1. Catalog and audit all twelve (12) external telemetry and archival data providers.
2. Ingest twenty-five (25) authoritative historical landslide events from official government post-disaster surveys, expanding the canonical event registry from seventeen (17) to forty-two (42) verified incidents.
3. Enforce a five-tier event verification hierarchy (`VERIFIED_PRIMARY`, `VERIFIED_MULTI_SOURCE`, `SECONDARY_VERIFIED`, `UNVERIFIED`, `REJECTED`).
4. Validate that fallback meteorological (Open-Meteo) and seismological (USGS) feeds operate with transparent provenance and are never mislabeled as primary national feeds (IMD / NCS).
5. Preserve absolute model weight immutability for Production V3 (`7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`) and Research V4.5 (`31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f`).

---

## 2. Inviolable Governance Boundaries
- **NO FABRICATION:** Under no circumstances are landslide events, coordinates, failure dates, sensor observations, or API credentials manufactured.
- **ZERO LIVE SENSOR CLAIMS:** In-situ physical IoT sensors remain at 0 installed, 0 verified, and status `UNAVAILABLE / PENDING`. Kinematic ML remains `NOT_TRAINED_DATA_PENDING`.
- **PRESERVATION OF PRODUCTION V3:** Production V3 is serving-frozen. No fine-tuning, retraining, or architecture modification is permitted during data expansion.
- **CREDENTIAL ISOLATION:** All API keys, tokens, and credentials belong in `.env`. Manifests and API returns must leak zero sensitive tokens.

---

## 3. Authoritative Scope of Expansion
- **Baseline Events (V5.1):** 17 events across Sikkim, Manipur, Assam, Meghalaya, Mizoram, Nagaland.
- **Expansion Events (V5.2):** 25 documented events across 8 NER states from official GSI bulletins, BRO Project registers, and SDMA disaster communications.
- **Total Canonical Ground-Truth Events:** Exactly 42 events.
- **Negative Control Windows:** 20 verified stable corridors with 0 failure evidence.
- **Connectors Audited:** 12 total (2 LIVE, 2 CONNECTED, 4 AUTH_REQUIRED, 3 CACHED, 1 UNAVAILABLE).
