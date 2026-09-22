# PARVAT NETRA / PAHAD AI — Phase V4.4 Real Temporal Dataset Report

**Document ID**: `PAHAD-DOC-V4-4-SET-001`  
**Timestamp**: `2026-09-20T13:32:12.263672+00:00`  
**Operational Status**: **RESEARCH / DATA FOUNDATION ONLY**  
**Final Verdict**: `V4_4_DATA_FOUNDATION_READY`  

---

## 1. Dataset Characteristics & Summary
- **Artifact**: `data/processed/lstm_v4_4_real_temporal_sequences.csv`
- **Checksum (SHA-256)**: `89b48d3b8354f8e66a26ccd9dc3b08d8b51a7616b3e983a803aa4d3285c305e3`
- **Sequence Count**: 105 continuous sequences (85 disaster events across 5 lead times + 20 negative controls)
- **Window Length**: **168 continuous hourly steps** (7 antecedent days)
- **Total Data Rows**: **17,640 hourly observations**
- **Feature Channels**: 37 channels with strict provenance
- **Synthetic Data**: **0 synthetic curves (100% empirical reanalysis & physics)**

## 2. Research Utility & Scientific Boundaries
1. **Long-Horizon Utility (24h to 168h)**: The 168-hour continuous window substantially expands synoptic rainfall accumulation tracking (up to 7 days antecedent precipitation).
2. **Short-Horizon Limitation (6h)**: Historical disaster slopes lacked in-situ IoT telemetry; therefore, 6h imminent prediction remains physically and mathematically data-limited until live sensor field deployment.
3. **Production Safety**: `PAHADBiLSTMv3` remains active, locked, and untouched (`7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`). No deployment performed.
