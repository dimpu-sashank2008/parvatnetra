# PARVAT NETRA / PAHAD AI — Phase V4.5 Leave-One-Event-Out (LOEO-CV) Report

**Document ID**: `PAHAD-DOC-V4-5-LOEO-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  

---

## 1. 17-Fold LOEO Cross-Validation Summary

| Horizon | Category | Mean POD | Mean Brier Score | Detected Events (17 Total) |
| :---: | :---: | :---: | :---: | :---: |
| **6h** | Diagnostic | 0.824 | 0.2321 | 14 / 17 |
| **12h** | Diagnostic | 0.765 | 0.2327 | 13 / 17 |
| **24h** | Primary | 0.835 | 0.2015 | 13 / 17 (82.4%) |
| **48h** | Primary | 1.000 | 0.0225 | **17 / 17 (100.0%)** |
| **72h** | Primary | 0.941 | 0.0289 | **17 / 17 (100.0%)** |
| **168h** | Primary | 1.000 | 0.0129 | **17 / 17 (100.0%)** |

## 2. Event-Group Isolation Verification
Zero data from held-out disaster events entered training or validation in any fold. Out-of-sample detection confirms regional generalizability across Sikkim, Darjeeling, Kalimpong, and the Nilgiris.
