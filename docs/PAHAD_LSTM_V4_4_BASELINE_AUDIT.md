# PARVAT NETRA / PAHAD AI — Phase V4.4 Baseline Audit Report

**Document ID**: `PAHAD-DOC-V4-4-BASE-001`  
**Timestamp**: `2026-09-20T13:32:12.260669+00:00`  
**Phase**: `Phase V4.4 — Real Historical Temporal Data Foundation`  
**Operational Status**: **RESEARCH / OFFLINE ONLY (PRODUCTION DISABLED)**  
**Active Production Model**: `PAHADBiLSTMv3` (LOCKED & SERVING)  

---

## 1. Executive Baseline Summary
Following the Phase V4.3 research verdict of `V4_3_DATA_LIMITED`, Phase V4.4 establishes the empirical, multi-temporal data foundation for PARVAT NETRA. This audit documents the preexisting repository state, dataset inventory, and architectural boundaries prior to data foundation construction.

## 2. Preexisting Artifact Inventory & Cryptographic Ledger
| Component | Artifact Path | SHA-256 Checksum | Operational Role |
|---|---|---|---|
| **Production Model V3** | `models/pahad_lstm_v3_weights.pt` | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` | **ACTIVE PRODUCTION (UNTOUCHED)** |
| **Research Model V4.1** | `models/pahad_lstm_v4_1_weights.pt` | `aa833d54842702240fcbc7411f15dbc3f08dfb3c30839b30f4db103475b1d979` | **OFFLINE RESEARCH** |
| **Research Model V4.2** | `models/pahad_lstm_v4_2_weights.pt` | `b67a4b7194a83468c27e02fbf1bbbb6eaa3019a130574a2b0a203b99eeea0ee9` | **OFFLINE RESEARCH** |
| **Research Model V4.3** | `models/pahad_lstm_v4_3_research_weights.pt` | `65a21ab9e493967ad690df18ffc58850ac9cb9d2d3123d12a377ac9030a19624` | **OFFLINE RESEARCH** |
| **V4.3 Sequences** | `data/processed/lstm_v4_historical_sequences.csv` | `db2293ff752351cd04a4f98589ef4ae6e97d8d71549f36abc9cf960feea8b9b5` | 72-hour sequence dataset |

## 3. Data Source & Processing Infrastructure
1. **Canonical Events**: 17 verified historical landslide disasters from Geological Survey of India (GSI) across 8 North-East states.
2. **Negative Controls**: 20 verified geological/meteorological control locations across 4 environmental regimes.
3. **Atmospheric / Hydrological Connector**: Open-Meteo Historical Archive API querying ECMWF ERA5-Land hourly reanalysis.
4. **Seismicity Connector**: USGS FDSN Earthquake Catalog (rolling 300km radius, magnitude >= 2.0).
5. **Geotechnical Engine**: Mohr-Coulomb Infinite Slope Stability Factor of Safety (`calculate_infinite_slope_fs`).
6. **Production Safety Boundary**: `PAHADBiLSTMv3` remains exclusively serving live inference. Zero production dispatch or UI modifications.
