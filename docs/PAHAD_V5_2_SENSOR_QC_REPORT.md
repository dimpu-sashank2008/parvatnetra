# PARVAT NETRA / PAHAD AI — PHASE V5.2
## SENSOR DATA QUALITY CONTROL & PHYSICAL PLAUSIBILITY AUDIT

**Corridor**: CORR-NH10-SIKKIM-KM48 (NH-10 Rangpo–Singtam, Sikkim, KM 48.2)  
**Date**: September 2026  
**Verdict**: `V5_2_PHYSICAL_DEPLOYMENT_PENDING`  
**Classification**: `OFFICIAL USE ONLY / LOCALHOST AUDIT`  

---

### 1. Multi-Tier Sensor QC Framework
Before any sensor observation is admitted into the geotechnical Factor of Safety (FoS) or PAHAD AI models, it undergoes automated quality control checks:
1. **Physical Range Bounds**: Strict plausibility limits derived from instrument physics.
2. **Operational Expected Range**: Typical geotechnical baseline expectations for undisturbed slopes.
3. **Flatline Detection**: Identification of frozen analog-to-digital converters (ADC) or stuck floaters ($\ge 24$ hours zero variance).
4. **Rate of Change (RoC) Limit**: Rejection of unphysical transient spikes (e.g. infinite acceleration).

### 2. Instrument Thresholds & Verification Parameters

| Sensor Type | Parameter | Physical Minimum | Physical Maximum | Normal Operating Range | Flatline Threshold | Max RoC Limit |
|---|---|---|---|---|---|---|
| **Piezometer** | Pore-Water Pressure | -50.0 kPa | 500.0 kPa | 0.0 to 50.0 kPa | 24 hours | 100 kPa / hr |
| **Inclinometer** | Shear Displacement | -100.0 mm | 100.0 mm | -5.0 to 5.0 mm | 48 hours | 20 mm / hr |
| **Tiltmeter** | Biaxial Tilt Angle | -45.0 deg | 45.0 deg | -2.0 to 2.0 deg | 48 hours | 5 deg / hr |
| **Rain Gauge** | Precipitation Intensity | 0.0 mm/h | 250.0 mm/h | 0.0 to 30.0 mm/h | 72 hours (Dry Season) | 150 mm / hr |

### 3. Verification Test Suite Status
The dedicated test suite `tests/test_v5_2_sensor_qc.py` validates that:
- Readings outside physical limits (e.g. Piezometer at 850 kPa or -150 kPa) are quarantined.
- Spurious sensor noise is flagged with `QC_FAIL_OUT_OF_BOUNDS`.
- Zero contaminated or out-of-range synthetic points are passed into operational models.
- QC Pass Rate: 100% across all 4 canonical sensor categories.
