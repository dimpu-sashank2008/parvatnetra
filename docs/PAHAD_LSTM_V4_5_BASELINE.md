# PARVAT NETRA / PAHAD AI — Phase V4.5 Baseline Audit & Chronological Ledger

**Document ID**: `PAHAD-DOC-V4-5-BASE-001`  
**Timestamp**: `2026-09-20T19:56:00Z`  
**Phase**: `Phase V4.5 — Long-Range Multi-Horizon Temporal Modeling`  
**Author**: `PARVAT NETRA / PAHAD AI ML Research Sentinel`  
**Target Problem Statement**: `SIH 26001 (Predictive AI for Hillslope Analysis & Disaster-response)`  

---

## 1. Cryptographic Baseline & Integrity Ledger

Before executing any research training or diagnostics in Phase V4.5, all model artifacts and dataset checksums were verified against the repository truth:

| Model / Dataset | Artifact Path | SHA-256 Checksum | Operational Role |
|---|---|---|---|
| **V3 Production Model** | `models/pahad_lstm_v3_weights.pt` | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` | **ACTIVE PRODUCTION (LOCKED)** |
| **V4 Dataset Audit** | `data/observations/pahad_observations.db` | Pre-existing SQLite database | Historical Inventory Only |
| **V4.1 Research Weights** | `models/pahad_lstm_v4_1_weights.pt` | `aa833d54842702240fcbc7411f15dbc3f08dfb3c30839b30f4db103475b1d979` | Offline Research (Over-parameterized) |
| **V4.2 Research Weights** | `models/pahad_lstm_v4_2_weights.pt` | `b67a4b7194a83468c27e02fbf1bbbb6eaa3019a130574a2b0a203b99eeea0ee9` | Offline Research (Capacity-Matched) |
| **V4.3 Research Weights** | `models/pahad_lstm_v4_3_research_weights.pt` | `65a21ab9e493967ad690df18ffc58850ac9cb9d2d3123d12a377ac9030a19624` | Offline Research (Diagnostic Baseline) |
| **V4.4 Data Foundation** | `data/processed/lstm_v4_4_real_temporal_sequences.csv` | `89b48d3b8354f8e66a26ccd9dc3b08d8b51a7616b3e983a803aa4d3285c305e3` | **168h Historical Temporal Foundation** |

---

## 2. Chronological Research Evolution: V3 to V4.4

### Phase V3 (Active Production Primary)
- Deployed as the operational model for live inference on the PARVAT NETRA platform.
- Evaluated on composite physics and regional empirical curves.
- Cryptographically frozen to prevent accidental production regression or weight contamination.

### Phase V4 (Database Inventory & Forensics)
- Audited `pahad_observations.db` and live operational tables.
- Revealed that live telemetry buffers only stored 48h–72h rolling windows for recent sensors, lacking the genuine multi-day antecedent records needed for historical 2022–2024 disaster events.
- Audit verdict: `V4_DATASET_REQUIRES_REWORK`.

### Phase V4.1 (Historical Backfill & Initial Training)
- Backfilled genuine historical meteorological forcing via ECMWF ERA5-Land reanalysis and USGS FDSN seismicity for 17 GSI events and 20 negative controls.
- Replaced synthetic polynomial curves with genuine 72-hour trajectories.
- Architecture suffered from capacity mismatch (1.29M parameters), leading to premature training termination at Epoch 1.

### Phase V4.2 (Capacity Matching & Optimization Fix)
- Rescaled network architecture to a capacity-matched 1-layer BiLSTM (~110k parameters).
- Resolved optimizer dynamics using AdamW, Cosine Annealing, and balanced loss.
- Demonstrated strong synoptic skill: 24h CSI = 0.429 (POD 0.750), 48h CSI = 0.833.

### Phase V4.3 (Forensic Multi-Horizon Diagnostic)
- Benchmarked performance across 6h, 12h, 24h, 48h horizons.
- Established the fundamental physical distinction:
  - Regional 9km gridded precipitation reliably drives 24h–48h slope saturation.
  - Imminent 6h detachment requires localized micro-kinetics (tilt rate, borehole shear strain, acoustic emissions), which were not monitored on uninstrumented historical slopes in 2022–2024.
- Authoritative verdict: `V4_3_DATA_LIMITED`.

### Phase V4.4 (Real Historical Temporal Data Foundation)
- Evaluated 17 canonical GSI disaster events and 20 verified negative controls across expanded temporal windows: 72h, 96h, 120h, and 168h.
- Confirmed **100% complete hourly data up to 168 continuous hours (7 days)** for all 37 events/controls (17,640 total observations across 37 channels).
- Strictly verified zero future leakage, zero synthetic curves, and strict exclusion of `composite_risk_index_cri`.
- Authoritative verdict: `V4_4_DATA_FOUNDATION_READY`.

---

## 3. Known Physical & Operational Boundaries for V4.5

1. **Regional Gridded Data vs Localized Imminent Failure**:
   - ERA5-Land reanalysis (9km spatial resolution) cannot capture localized sub-kilometer convective microbursts or slope-scale shear strain between $T-12\text{h}$ and $T-6\text{h}$.
   - Consequently, **6h and 12h horizons are treated strictly as diagnostic comparisons**.
2. **Primary Research Horizons**:
   - **24h, 48h, 72h, 168h** are the primary targets, assessing whether the 168-hour antecedent wetting front improves medium-to-long-range prediction.
3. **Data Scarcity & Generalization**:
   - The verified dataset contains 17 high-confidence GSI disaster events across Northeast India.
   - Out-of-sample generalization must be evaluated via **17-Fold Leave-One-Event-Out Cross-Validation (LOEO-CV)** rather than random train-test splitting.
4. **Production Isolation**:
   - V4.5 is strictly an offline research investigation. No production routing, alerting, or UI behavior will be altered.
