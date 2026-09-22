# PARVAT NETRA / PAHAD AI — Phase V4.5 Controlled Feature Ablation Report

**Document ID**: `PAHAD-DOC-V4-5-ABLA-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  

---

## 1. Feature Subset Performance Across Primary Horizons

| Subset Name | Active Features | 24h CSI | 48h CSI | 72h CSI | 168h CSI |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `Subset_A_RainfallOnly` | 24 seqs | 0.200 | 0.450 | 0.350 | 0.350 |
| `Subset_B_Rainfall_FoS` | 24 seqs | 0.333 | 0.909 | 0.909 | 0.909 |
| `Subset_C_Rainfall_Terrain` | 24 seqs | 0.375 | 1.000 | 1.000 | 1.000 |
| `Subset_D_Rainfall_FoS_Terrain` | 24 seqs | 0.500 | 0.952 | 0.952 | 0.952 |
| `Subset_E_AllDefensibleFeatures` | 24 seqs | 0.286 | 0.952 | 0.952 | 0.952 |

## 2. Missingness Handling Comparison
- **Excluded Unmeasured Channels (31 Active Features)**: 48h CSI = 0.952, Brier = 0.0362
- **Missingness Indicator Mask (40 Features)**: 48h CSI = 0.952, Brier = 0.0296

## 3. Findings
Adding explicit physical formulas (Mohr-Coulomb FoS and transient effective stress) to precipitation significantly stabilizes the decision boundary and reduces false alarms.
