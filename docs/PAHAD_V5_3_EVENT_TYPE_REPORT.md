# PARVAT NETRA • PAHAD AI — PHASE V5.3
# KINEMATIC EVENT TYPE & MECHANISTIC CLASSIFICATION REPORT

**Phase**: V5.3 — External Source Evidence Verification & Canonical Event Forensics  
**Status**: VERIFIED & AUDITED  
**Corridor**: CORR-NH10-SIKKIM-KM48 & NER Regional Network  
**Overall Verdict**: `V5_3_EVIDENCE_VERIFIED`  
**Date**: September 2026  

---

## 1. Executive Summary

This report defines the kinematic failure classification and mechanistic vocabulary enforced across all 42 canonical landslide events in PARVAT NETRA.

Standardizing landslide mechanics is critical because different failure modes exhibit radically distinct antecedent precipitation thresholds, pore-water pressure response times, and shear surface geometries.
- **Controlled Vocabulary Size**: 7 Kinematic Types (Cruden & Varnes / Hungr et al. taxonomy)
- **Vocabulary Conformance**: 100.0% (All 42 events map to valid kinematic types)
- **Dominant Failure Mode**: `DEBRIS_FLOW` (21 events, 50.0%)
- **Rotational Slips**: 7 events (16.7%)
- **Planar Shear Failures**: 5 events (11.9%)
- **Rock Falls**: 4 events (9.5%)
- **GLOF / Complex / Mudflows**: 5 events (11.9%)

---

## 2. Kinematic Failure Mechanics & Distribution

| Kinematic Type | Count | Percentage | Physical Failure Mechanism | Typical Geological Setting in NER | Representative Example |
|:---|:---:|:---:|:---|:---|:---|
| `DEBRIS_FLOW` | 21 | 50.0% | Rapid channeled flow of saturated colluvium and boulders driven by cloudbursts | Steep mountain gullies, Darjeeling Gneiss, weathered phyllite | Pakyong (`EV-01`), Mawsynram (`EV-11`) |
| `ROTATIONAL_SLIDE` | 7 | 16.7% | Deep-seated curved slip surface along weak cohesive clay-shale strata | Disang Formation, Barail group weathered shales | Tupul Yard (`EV-04`), Kohima Pagala Pahar (`EV-20`) |
| `PLANAR_SLIP` | 5 | 11.9% | Translational glide along daylighting bedding planes or joint sets | Dipping quartzites and Daling phyllites | Dikchu Dam Abutment (`EV-19`), 29th Mile (`EV-24`) |
| `ROCK_FALL` | 4 | 9.5% | Free-fall, bouncing, or rolling of fractured rock blocks from vertical bluffs | Vertical jointed gneiss cliffs, Teesta gorge cliffs | Teesta Bazar (`EV-18`), Sohra Rim (`EV-30`) |
| `GLOF_TRIGGERED` | 2 | 4.8% | High-energy toe erosion and bank collapse triggered by glacial lake outburst floods | High-altitude moraine dam breaches, South Lhonak lake | Singtam GLOF Slide (`EV-03`) |
| `COMPLEX_MASS_MOVEMENT` | 2 | 4.8% | Multi-stage combination of rotational slumping transitioning into rapid debris avalanche | Deep weathered relict shear zones | Tindharia Pagla Jhora (`EV-26`), Dima Hasao (`EV-08`) |
| `MUD_FLOW` | 1 | 2.4% | Hyper-concentrated flow of fine-grained saturated silts and clays | Overburden washouts, highway tunnel portals | Sonapur Tunnel South Portal (`EV-31`) |

---

## 3. Physical Mechanics & Sensor Corroboration

The kinematic classification directly guides sensor fusion and physical simulation within PAHAD AI:
1. **Pore-Water Pressure Coupling**: Rotational and planar slides require sustained groundwater build-up ($u > u_{\text{crit}}$) over 48h to 72h.
2. **Kinematic Thresholds**: Rock falls and debris flows are triggered predominantly by short-duration cloudbursts ($I > 50\text{ mm/h}$) overcoming cohesion along existing tension cracks.
3. **InSAR Surface Velocity**: Complex mass movements exhibit multi-month precursory creeping deformation ($\Delta v > 15\text{ mm/year}$) detectable in Sentinel-1 ascending/descending passes.

---

## 4. Automated Verification Results

All classifications are asserted by `tests/test_v5_3_event_type.py`:
- `test_all_event_types_in_controlled_vocabulary`: PASSED
- `test_kinematic_type_distribution`: PASSED
