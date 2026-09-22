# PARVAT NETRA / PAHAD AI — PHASE V4.8
# Geotechnical Physical Chain Validation & Multimodal Evidence Linkage Report

**Document Version**: 1.0.0  
**Phase**: V4.8 Real Telemetry Evidence Audit & First-Data Foundation  
**System Status**: `V4_8_DATA_FOUNDATION_READY`  
**Governing Mechanics**: Mohr-Coulomb Shear Failure & Terzaghi Effective Stress  
**Date**: September 2026  

---

## 1. The Geotechnical Causal Chain

PARVAT NETRA’s multi-modal early-warning architecture is grounded in the foundational physical mechanics of rainfall-induced hillslope failure:

$$\textbf{RAINFALL} \xrightarrow{(1)} \textbf{INFILTRATION} \xrightarrow{(2)} \textbf{PORE PRESSURE} \xrightarrow{(3)} \textbf{EFFECTIVE STRESS} \xrightarrow{(4)} \textbf{DEFORMATION}$$

In accordance with Section 15 of the V4.8 Master Engineering Prompt, this report documents **where empirical evidence exists and where physical telemetry remains pending**. The system strictly forbids inventing synthetic links.

---

## 2. Link-by-Link Evidence Availability Audit

```
[Link 1: RAINFALL]
- Evidence Status: EMPIRICALLY VERIFIED (STREAM A)
- Data Source: IMD Automated Weather Stations (AWS) + ERA5-Land Reanalysis Grids
- Coverage: 100% complete for all 17 canonical GSI historical events and 20 negative controls.
- Parameters: rain_1h to rain_168h, rain_intensity, rain_acceleration, API_3d, API_30d.

        |
        v
[Link 2: INFILTRATION & UNSATURATED SEEPAGE]
- Evidence Status: PHYSICALLY DERIVED (MOHR-COULOMB GREEN-AMPT SEEPAGE)
- Data Source: GLDAS / ERA5 soil moisture + 1D Green-Ampt transient seepage engine.
- Coverage: Deterministic calculation across all monitored grid nodes.
- Parameters: soil_moisture, hydraulic_saturation, transient wetting front depth.

        |
        v
[Link 3: PORE-WATER PRESSURE DYNAMICS]
- Evidence Status: PARTIALLY VERIFIED (MACRO-SCALE MODELED / IN-SITU PENDING)
- Modeled: Groundwater table elevation ($z_w$) and pore-pressure ratio ($r_u = \frac{u}{\gamma z}$).
- In-Situ Measured: DOWNHOLE PIEZOMETER TELEMETRY IS PENDING (Status: PHYSICAL_TELEMETRY_PENDING).
- Real-world Linkage: Laboratory bench HIL tested; physical downhole borehole placement scheduled.

        |
        v
[Link 4: EFFECTIVE STRESS & FACTOR OF SAFETY REDUCTION]
- Evidence Status: PHYSICALLY DERIVED (TERZAGHI EFFECTIVE STRESS PRINCIPLE)
- Formulation: $\sigma' = \sigma - u$; $\tau_f = c' + (\sigma - u) \tan \phi'$
- Target Metric: Infinite Slope Factor of Safety ($FoS$).
- Verification: Validated across all slope angles ($15^\circ$ to $65^\circ$) in `test_pahad_engine.py`.

        |
        v
[Link 5: KINEMATIC DEFORMATION & SHEAR RUPTURE]
- Evidence Status: PARTIALLY VERIFIED (HISTORICAL GSI RECORDS / IN-SITU PENDING)
- Historical Ground Truth: Documented crown scarps, road washouts, and Sentinel-1 InSAR LOS velocities.
- In-Situ Measured: BOREHOLE INCLINOMETER & SURFACE TILTMETER TELEMETRY IS PENDING.
- Real-world Linkage: Kinematic classifier is strictly NOT_TRAINED_DATA_PENDING until real sensor observations arrive.
```

---

## 3. Sensor Correlation & Causation Boundaries

When physical sensor data begins streaming during Phase V4.9:
1. **No Unwarranted Causal Claims**: Correlation between pore-pressure spikes ($\Delta u$) and inclinometer shear velocity ($v_{\text{tilt}}$) will be evaluated via lagged cross-correlation ($R_{xy}(\tau)$). Causation will never be claimed from correlation alone.
2. **Fail-Closed Dual-Stream Fusion**: As long as Link 3 (in-situ pore pressure) and Link 5 (in-situ deformation) remain physically pending, Stream B nowcasting remains `UNAVAILABLE`, and the system relies exclusively on Stream A synoptic physics.
