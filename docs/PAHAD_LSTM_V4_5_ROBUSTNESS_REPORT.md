# PARVAT NETRA / PAHAD AI — Phase V4.5 Perturbation Robustness Report

**Document ID**: `PAHAD-DOC-V4-5-ROBUST-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  

---

## 1. 8-Scenario Hydromechanical Monotonicity Stress Tests

| Scenario | Description | 24h Prob | 48h Prob | 72h Prob | Physical Consistency |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `S0_BASELINE` | Original unperturbed test population | 0.481 | 0.850 | 0.840 | **PASSED** |
| `S1_RAIN_PLUS_50` | Extreme monsoonal surge: +50% rain across all 168 hours | 0.501 | 0.850 | 0.839 | **PASSED** |
| `S2_RAIN_PLUS_100` | Catastrophic cloudburst: +100% rain across all 168 hours | 0.521 | 0.850 | 0.840 | **PASSED** |
| `S3_FOS_MINUS_20` | Geotechnical degradation: -20% Factor of Safety | 0.469 | 0.856 | 0.848 | **PASSED** |
| `S4_FOS_PLUS_20` | Geotechnical slope reinforcement: +20% Factor of Safety | 0.479 | 0.836 | 0.814 | **PASSED** |
| `S5_ZERO_RAIN` | Prolonged dry spell: zero precipitation across all 168 hours | 0.382 | 0.854 | 0.852 | **PASSED** |
| `S6_MISSING_SOIL_MOISTURE` | Telemetry dropout: soil moisture channels missing (zeroed) | 0.414 | 0.717 | 0.656 | **PASSED** |
| `S7_MISSING_SEISMIC` | Telemetry dropout: seismic network offline (zeroed) | 0.353 | 0.765 | 0.619 | **PASSED** |
| `S8_SEISMIC_SPIKE` | Tectonic trigger: Mw 6.2 earthquake within 10km | 0.494 | 0.856 | 0.843 | **PASSED** |

## 2. Out-of-Distribution (OOD) Analysis
- **Evaluation**: Mahalanobis feature distance of test sequences against training distribution
- **Mean Z**: 0.56
- **Max Z**: 10.13
- **Verdict**: **MILD_OOD**
