# PARVAT NETRA / PAHAD AI — PHASE V5.2
# PRECIPITATION DATA PROVENANCE & ANTI-RELABELING AUDIT

**Document ID:** `PN-DOC-V5.2-PRECIP-PROV`  
**Phase:** `V5.2`  
**Status:** `AUDITED & COMPLIANT`

---

## 1. Context & Invariant Mandate
Rainfall is the dominant trigger for 90%+ of Himalayan landslides. In national emergency response systems, misattributing numerical weather reanalysis as official in-situ India Meteorological Department (IMD) Automatic Weather Station (AWS) telemetry is dangerous and scientifically dishonest.

**Phase V5.2 Anti-Relabeling Directive:**
Under no circumstances may Open-Meteo, ECMWF, or GFS reanalysis be presented with IMD branding, provenance tags, or authority claims.

---

## 2. Provenance Architecture

```
[Rainfall Request]
       |
       v
Check IMD_API_TOKEN in .env
       |
       +---> [Configured] ---> Query IMD Nowcast API ---> Tag: [LIVE / IMD-AWS]
       |
       +---> [Missing/Empty] -> Fallback: Open-Meteo ---> Tag: [LIVE / OPEN-METEO]
```

### 2.1 Audit Verification
- `engine/external_data_engine.py`: IMD connector audit explicitly identifies Open-Meteo as the fallback provider while labeling its own status as `AUTH_REQUIRED`.
- `engine/weather_service.py`: Transparently declares the active provider in payload metadata.
- All historical rainfall context records in `historical_landslides_expansion_v5_2.json` cite their exact source (e.g. `Open-Meteo Historical Reanalysis` or `IMD Gridded Daily Archive`).
