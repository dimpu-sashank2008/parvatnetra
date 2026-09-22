# PARVAT NETRA / PAHAD AI — Phase V4.3 Controlled Feature Ablation Report

**Document ID**: `PAHAD-DOC-V4-3-ABLATION-001`  
**Timestamp**: `2026-09-20T12:13:23.116199+00:00`  

---

## Controlled Feature Ablation Results (Subsets A through J)

| Subset | Description | Features | 24h CSI | 24h POD | 48h CSI | 48h POD | Key Finding |
|---|---|---|---|---|---|---|---|
| **A** | Rainfall Only | 11 | 0.429 | 0.75 | 0.833 | 1.00 | Strong synoptic baseline |
| **B** | Rainfall + Soil Moisture | 12 | 0.500 | 1.00 | 0.833 | 1.00 | Improved hydrologic state tracking |
| **C** | Rainfall + FoS | 12 | **0.524** | **0.92** | 0.833 | 1.00 | Best physical signal |
| **D** | Rainfall + Terrain | 15 | 0.522 | 1.00 | 0.833 | 1.00 | Strong structural prior |
| **E** | Rainfall + Seismic | 14 | 0.500 | 1.00 | 0.833 | 1.00 | Consistent with weather |
| **F** | Rainfall + Deformation | 15 | 0.409 | 0.75 | 0.833 | 1.00 | Deformation is unmonitored (zero gain) |
| **G** | All Physically Valid | 25 | 0.429 | 0.75 | 0.833 | 1.00 | Full feature set |
| **H** | Excluding Static DEM | 26 | 0.500 | 1.00 | 0.833 | 1.00 | Preserves dynamic hydromechanics |
| **I** | Excluding Derived | 10 | 0.429 | 0.75 | 0.833 | 1.00 | Raw reanalysis only |
| **J** | Genuinely Temporal Only | 19 | 0.500 | 1.00 | 0.833 | 1.00 | Optimal temporal focus |

### Critical Takeaway:
Adding unmonitored deformation channels (tilt, InSAR) adds zero signal because they were unrecorded historically. Rainfall and FoS provide the primary predictive signal.
