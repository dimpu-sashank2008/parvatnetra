# PARVAT NETRA / PAHAD AI — Phase V4.1 Claim Forensic Audit

**Document ID**: `PAHAD-DOC-V4-1-CLAIMS-001`  
**Timestamp**: `2026-09-20T17:00:00+05:30`  
**Status**: **VERIFIED**

---

## Forensic Claim Classification

| Claim Statement | Status | Evidence / Audit Findings |
|---|---|---|
| *"PAHAD BiLSTM V4.1 is trained on genuine historical hourly data"* | **SUPPORTED** | Sequences were constructed exclusively from ECMWF ERA5-Land reanalysis and USGS FDSN catalogs (7,560 hourly steps). `build_33f_sequence()` synthetic linspace code was not used. |
| *"BiLSTM V4.1 achieves zero future leakage across the 72-hour window"* | **SUPPORTED** | For all 105 sequences, observation timestamps strictly terminate at $T_{	ext{origin}}$. No post-origin data enters input tensors. |
| *"CRI is excluded from V4.1 training features to avoid target leakage"* | **SUPPORTED** | Feature count is 32. `composite_risk_index_cri` is completely excluded from feature columns. |
| *"The dataset contains continuous historical IoT piezometer & inclinometer telemetry"* | **UNSUPPORTED** | Piezometers and inclinometers were not deployed at remote mountain slopes in 2022–2024. These channels are preserved as `0.0` (missing/unmonitored) rather than fabricated. |
| *"BiLSTM V4.1 is production-ready for public alerting"* | **REQUIRES_REPHRASING** | V4.1 is a research shadow model. The dataset of 17 events, while authentic, constitutes `TRAINED_LIMITED_DATA`. Production serving remains `PAHADBiLSTMv3`. |
| *"LOEO-CV demonstrates generalization across unseen geographical events"* | **SUPPORTED** | 17-fold LOEO-CV was executed. Held-out events were completely isolated from training, normalization, and calibration. |
