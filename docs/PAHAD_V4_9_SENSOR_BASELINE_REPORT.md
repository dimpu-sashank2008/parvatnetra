# PARVAT NETRA / PAHAD AI — PHASE V4.9
# SENSOR BASELINE & OPERATIONAL BOUNDS REPORT

**Phase**: V4.9 — Geotechnical Baseline Statistics & Parameter Bounds  
**Target Corridor**: CORR-NH10-SIKKIM-KM48  
**Evaluated At**: 2026-09-20T16:15:00Z  

---

## 1. Executive Summary

This report defines the mathematical framework for computing descriptive baseline telemetry statistics (mean, median, standard deviation, minimum, maximum, temporal span, and missingness) and sets operational range bounds without making premature or unwarranted failure interpretations (Section 18 & 21).

---

## 2. Sensor Operational Ranges & Parameter Limits

| Sensor Type | Monitored Parameter | Unit | Physical Measurement Range | Expected Normal Stable Range | Engineering Default Trigger |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Piezometer** | Pore-water pressure ($u$) | $\text{kPa}$ | $[-50.0, 500.0]$ | $[0.0, 50.0]$ | $\ge 80.0\text{ kPa}$ |
| **Inclinometer** | Shear displacement ($\delta$) | $\text{mm}$ | $[-100.0, 100.0]$ | $[-5.0, 5.0]$ | $\ge 15.0\text{ mm}$ |
| **Tiltmeter** | Angular tilt magnitude ($\theta$) | $\text{deg}$ | $[-45.0, 45.0]$ | $[-2.0, 2.0]$ | $\ge 5.0^{\circ}$ |
| **Rain Gauge** | Precipitation intensity ($I$) | $\text{mm/h}$ | $[0.0, 250.0]$ | $[0.0, 30.0]$ | $\ge 40.0\text{ mm/h}$ |
| **Edge Gateway** | Battery DC voltage ($V$) | $\text{V}$ | $[9.0, 15.0]$ | $[11.5, 14.2]$ | $\le 10.8\text{ V}$ (Low Batt) |

---

## 3. Baseline Computation Protocol

1. When authentic live measurements begin, `FieldEvidenceManager.compute_baseline_statistics()` will process incoming observations to establish the site-specific undisturbed geological baseline.
2. Baseline statistics must **never** be conflated with failure thresholds. Thresholds remain anchored in Mohr-Coulomb geotechnical mechanics and laboratory shear testing.
