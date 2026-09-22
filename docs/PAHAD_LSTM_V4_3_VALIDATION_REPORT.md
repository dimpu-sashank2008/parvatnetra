# PARVAT NETRA / PAHAD AI — Phase V4.3 Validation Report

**Document ID**: `PAHAD-DOC-V4-3-VAL-001`  
**Timestamp**: `2026-09-20T12:13:23.116715+00:00`  

---

## 1. 17-Fold Leave-One-Event-Out (LOEO-CV)
| Horizon | Mean CSI | Mean POD | Mean FAR | Mean Brier |
|---|---|---|---|---|
| **6h**  | 0.0000 | 0.0000 | 0.0000 | 0.1767 |
| **12h** | 0.0765 | 0.1765 | 0.2176 | 0.2794 |
| **24h** | 0.2196 | 0.3529 | 0.1471 | 0.3348 |
| **48h** | **0.6824** | **0.6824** | **0.0000** | **0.2473** |

## 2. Negative Control Audit (20 Verified Controls)
All 20 controls audited:
- 8 Dry Season Quiescent (Max 24h Rain: 60.1 mm, Min FoS: 0.76)
- 4 Heavy Rain Competent Formation (Max 24h Rain: 97.9 mm, Min FoS: 0.75)
- 6 Moderate Monsoon Stable (Max 24h Rain: 35.0 mm, Min FoS: 0.81)
- 2 Post-Seismic Dry Stable (Max 24h Rain: 0.0 mm, Min FoS: 0.99)
