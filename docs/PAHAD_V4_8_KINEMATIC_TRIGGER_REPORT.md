# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Kinematic Multi-Parameter Trigger Validation & Engineering Default Limits Report

**Document Version**: 1.0.0  
**Phase**: V4.8 Real Telemetry Evidence Audit & First-Data Foundation  
**System Status**: `V4_8_DATA_FOUNDATION_READY`  
**Trigger Engine**: `engine/kinematic_trigger_engine.py`  
**Classification**: `ENGINEERING_DEFAULT` (Not Field Validated)  
**Date**: September 2026  

---

## 1. Trigger Status Classification Policy

In accordance with Section 16 of the V4.8 Master Engineering Prompt:
$$\textbf{Existing V4.6 trigger thresholds are ENGINEERING\_DEFAULT. Do NOT promote them to FIELD\_VALIDATED.}$$

Field validation of kinematic triggers requires empirical observation of real hillslope acceleration under monsoon conditions. Until real in-situ sensors transmit physical deformation data from the NH-10 corridor, all trigger thresholds remain categorized as:
$$\textbf{STATUS: ENGINEERING\_DEFAULT}$$

---

## 2. Multi-Parameter Trigger Specification Matrix

The `KinematicTriggerEngine` enforces multi-parameter deterministic thresholds across four physical instrument modalities:

| Instrument Modality | Monitored Parameter | Watch Threshold | Elevated Threshold | Critical Threshold | Baseline Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vibrating Wire Piezometer** | Pore Pressure ($u$) | $> 80.0 \text{ kPa}$ | $> 120.0 \text{ kPa}$ | $> 180.0 \text{ kPa}$ | Hydrostatic baseline at 12m slip surface |
| **Vibrating Wire Piezometer** | Pressure Rate ($\frac{du}{dt}$) | $> 5.0 \text{ kPa/h}$ | $> 10.0 \text{ kPa/h}$ | $> 20.0 \text{ kPa/h}$ | Rapid transient groundwater rise |
| **In-Place Inclinometer** | Cumulative Shear ($\delta x$) | $> 5.0 \text{ mm}$ | $> 15.0 \text{ mm}$ | $> 30.0 \text{ mm}$ | Progressive shear zone strain |
| **In-Place Inclinometer** | Shear Velocity ($v_{\text{shear}}$) | $> 1.0 \text{ mm/h}$ | $> 3.0 \text{ mm/h}$ | $> 8.0 \text{ mm/h}$ | Tertiary creep acceleration |
| **Surface Tiltmeter** | Tilt Magnitude ($\theta$) | $> 0.50^\circ$ | $> 1.20^\circ$ | $> 2.50^\circ$ | Rotational block displacement |
| **Surface Tiltmeter** | Tilt Rate ($\frac{d\theta}{dt}$) | $> 0.10^\circ/\text{h}$ | $> 0.25^\circ/\text{h}$ | $> 0.60^\circ/\text{h}$ | Surface scarp opening velocity |
| **Rain Gauge** | Rainfall Intensity ($I$) | $> 15.0 \text{ mm/h}$ | $> 35.0 \text{ mm/h}$ | $> 65.0 \text{ mm/h}$ | IMD cloudburst / torrential surge |
| **Rain Gauge** | Cumulative 24h Rain ($R_{24h}$) | $> 50.0 \text{ mm}$ | $> 100.0 \text{ mm}$ | $> 160.0 \text{ mm}$ | Antecedent saturation threshold |

---

## 3. False Alarm Behavior During Stable Periods

In `engine/kinematic_trigger_engine.py`:
- During nominal stable conditions (Pore pressure $\approx 25\text{ kPa}$, Tilt $\approx 0.05^\circ$, Rain $= 0.0\text{ mm/h}$), the trigger engine evaluates to `STATE_KINEMATIC_NORMAL`.
- Zero triggers are tripped during dry control periods.
- Single-parameter spikes (e.g. transient noise without corroborating precipitation or tilt) do not trigger elevated kinematic states, satisfying the multi-parameter corroboration rule.

---

## 4. Field Validation Roadmap (Phase V4.9)

To promote thresholds from `ENGINEERING_DEFAULT` to `FIELD_VALIDATED`:
1. **Receiver Operating Characteristic (ROC) Tuning**: Evaluate false alarm rate (FAR) vs probability of detection (POD) across at least two full monsoon seasons.
2. **Site-Specific Piezocone Penetration Tests (CPTu)**: Refine static hydrostatic baselines ($u_0$) post-installation.
3. **Threshold Calibration Report**: Serialized threshold sensitivity curves with documented 95% confidence intervals.
