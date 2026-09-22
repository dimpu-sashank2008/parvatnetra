# PARVAT NETRA / PAHAD AI — Phase V4.3 Final Scientific Research Report

**Document ID**: `PAHAD-DOC-V4-3-FINAL-001`  
**Timestamp**: `2026-09-20T12:13:23.117718+00:00`  
**Operational Status**: **RESEARCH / OFFLINE EVALUATION ONLY**  
**Final Verdict**: `V4_3_DATA_LIMITED`  
**Active Production Model**: `PAHADBiLSTMv3` (LOCKED & SERVING)  

---

## 1. Executive Scientific Synthesis
Phase V4.3 completed an exhaustive scientific investigation into the multi-horizon temporal prediction dynamics of PAHAD AI across 17 verified disaster events, 20 negative controls, and 105 continuous 72-hour historical sequences.

### Central Scientific Finding:
The experimental investigation definitively confirmed the core scientific hypothesis:
> *"Regional reanalysis rainfall (ERA5-Land at 9km resolution) and DEM terrain parameters provide robust, highly predictive signals for 24h to 48h synoptic landslide hazard forecasting (CSI: 0.522 to 0.833). However, resolving imminent 6h slope failure strictly from gridded meteorological data is physically constrained because the incremental rainfall differential between hour T-12 and T-6 is negligible without high-frequency localized field telemetry (piezometers, borehole inclinometers, acoustic emissions). Because these slopes were unmonitored in 2022–2024, the dataset is inherently data-limited for the 6h horizon."*

## 2. Integrity & Cryptographic Ledger
| Model Version | Artifact Path | Checksum (SHA-256) | Status |
|---|---|---|---|
| **v3** | `models/pahad_lstm_v3_weights.pt` | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` | **ACTIVE PRODUCTION (UNTOUCHED)** |
| **v4.1** | `models/pahad_lstm_v4_1_weights.pt` | `aa833d54842702240fcbc7411f15dbc3f08dfb3c30839b30f4db103475b1d979` | **OFFLINE RESEARCH** |
| **v4.2** | `models/pahad_lstm_v4_2_weights.pt` | `b67a4b7194a83468c27e02fbf1bbbb6eaa3019a130574a2b0a203b99eeea0ee9` | **OFFLINE RESEARCH** |
| **v4.3** | `models/pahad_lstm_v4_3_research_weights.pt` | `65a21ab9e493967ad690df18ffc58850ac9cb9d2d3123d12a377ac9030a19624` | **OFFLINE RESEARCH (DISABLED IN PROD)** |

## 3. Operational Safety & Non-Deployment Gate
- **Production Status**: `DISABLED`
- **Deployment**: `NOT PERFORMED`
- **Public Dispatch / Sirens / CAP**: Zero modification
- **Final Verdict**: `V4_3_DATA_LIMITED`
