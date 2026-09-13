# PARVATNETRA / PAHAD AI — Scientific & Operational Limitations

**Document ID**: `PAHAD-REP-04-LIMITATIONS`  
**Classification**: Scientific Transparency & AI Safety Protocol  
**Phase**: Phase 4 — Data-Grounded Research Prototype  
**Current Status**: `DATA-GROUNDED RESEARCH PROTOTYPE`  

---

## 1. Executive Statement

In accordance with SIH-26001 and national emergency safety standards, PARVAT NETRA does not overstate AI capabilities or present laboratory prototypes as infallible early warning tools. This document details the specific boundaries, statistical caveats, and field telemetry dependencies of the **PAHAD AI Landslide Event Prediction Model**.

---

## 2. Dataset & Sample Size Limitations

1. **Total Documented Event Volume**:
   - The current ground-truth dataset consists of **17 documented catastrophic landslide events** and **19 verified non-failure negative controls** ($N = 36$ total observations).
   - While each positive event is authenticated through GSI, NRSC, or SDMA disaster archives, statistical generalization across hundreds of untested micro-catchments cannot be mathematically claimed from 36 samples.

2. **Held-Out Test Sample Size ($N = 8$)**:
   - The operational test split comprises 5 positive landslide events and 3 heavy-rainfall negative controls.
   - Although the calibrated classifier achieves $POD = 1.0$, $FAR = 0.0$, and $CSI = 1.0$ on this test split, these metrics carry wide statistical confidence intervals ($\approx \pm 18\%$).

3. **Geographic Distribution Asymmetry**:
   - Landslide records in the NER catalog are predominantly clustered along major Border Roads Organisation (BRO) transportation corridors (NH-10 Teesta corridor, NH-717A, Tupul railway alignment, Dimapur-Kohima highway).
   - High-altitude wilderness zones and unpopulated ridge slopes in Upper Subansiri or eastern Tuensang have sparse ground-truth event records.

---

## 3. Telemetry & Feature Availability Boundaries

| Modality | Nominal Capability | Operational Limitation |
| :--- | :--- | :--- |
| **In-Situ Piezometers / Inclinometers** | Pore-pressure ($\text{kPa}$) & displacement ($\text{mm}$) at 15-min cadence | Available only at instrumented pilot corridors (e.g. Pakyong, Singtam, Melthum). Uninstrumented slopes fall back to DEM physics and satellite proxies. |
| **Doppler Weather Radar / AWS** | Precipitation accumulation at 1h to 72h windows | Rain-shadow zones in deep Himalayan valleys can experience radar beam blockage; AWS station density in remote hill districts is $\approx 1$ station per $500\text{ km}^2$. |
| **Copernicus Sentinel-1 InSAR** | Line-of-sight ground displacement ($\text{mm/year}$) | 12-day repeat pass cycle means InSAR cannot provide real-time warning for rapid rainfall-triggered debris flows ($< 6\text{ hours}$). |
| **Copernicus GLO-30 DEM** | 30m grid topographic slope, curvature, aspect | Fine micro-relief and localized road-cut over-steepening ($< 15\text{m}$) may be smoothed out by 30-meter pixel resolution. |

---

## 4. Missing-Data & Historical Reconstruction Caveats

- For historical events prior to 2024, real-time in-situ piezometers were not physically installed on the hillside.
- As documented in the feature manifest, historical geotechnical features were reconstructed using verified infinite-slope limit equilibrium mechanics ($FoS$) and hydrometeorological saturation curves.
- In live real-time inference, missing features are explicitly flagged with `[MISSING]` or `[CACHED]` badges and imputed using training-split medians rather than fabricated values.

---

## 5. Early Warning Safety Rules & Human-in-the-Loop Constraint

Under the **PARVAT NETRA Safety Constitution**:
1. The PAHAD AI Event Classifier **NEVER** issues automated public RED evacuation orders on its own.
2. An event alert requires independent **2-of-3 corroboration**:
   - Modality 1: $FoS < 1.10$ (Limit equilibrium physics)
   - Modality 2: $R_{24\text{h}} > I\text{-}D\text{ regional rainfall threshold}$
   - Modality 3: Calibrated Event Probability $> 0.70$
3. Public dispatch requires digital authorization from an on-duty SDMA/DDMA emergency official.
