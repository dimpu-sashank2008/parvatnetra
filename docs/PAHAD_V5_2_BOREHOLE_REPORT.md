# PARVAT NETRA / PAHAD AI — PHASE V5.2
## BOREHOLE & CASING PHYSICAL DRILLING EVIDENCE REPORT

**Corridor**: CORR-NH10-SIKKIM-KM48 (NH-10 Rangpo–Singtam, Sikkim, KM 48.2)  
**Borehole Designation**: `BH-NH10-KM48-01`  
**Date**: September 2026  
**Verdict**: `V5_2_PHYSICAL_DEPLOYMENT_PENDING`  
**Classification**: `OFFICIAL USE ONLY / LOCALHOST AUDIT`  

---

### 1. Borehole Engineering Specification
The planned downhole geotechnical monitoring borehole at NH-10 KM 48.2 is designed to intercept the active shear zone of the Rangpo–Singtam phyllitic slip surface:

- **Target Depth**: 25.0 meters
- **Borehole Diameter**: 115 mm (HQ wireline core drilling)
- **Casing Type**: ABS inclinometer casing with 4-keyway orthogonal tracking grooves (A0 aligned downhill along slip vector)
- **Casing Dimensions**: Outer Diameter 70.0 mm, Inner Diameter 60.0 mm
- **Annular Grouting**: Non-shrink bentonite-cement slurry (1:1 water:cement ratio, 5% sodium bentonite by weight)
- **Target Instruments**:
  - `PIEZO-NH10-KM48-01`: Vibrating wire piezometer placed at 12.0m depth within sand filter pocket (Graded silica sand 20/40 mesh)
  - `INCL-NH10-KM48-01`: In-place inclinometer chain stationed across the shear boundary at 15.0m depth

### 2. Physical Drilling & Casing Audit

| Audit Dimension | Engineering Requirement | Observed Ground Truth Status | Finding |
|---|---|---|---|
| Drilling Operations | Rotary diamond drilling to 25.0m depth | `NOT_DRILLED` | Drilling rig has not mobilized to site |
| Core Box Photographs | Photographic inventory of recovered rock cores | 0 files found | `field_evidence/borehole/` contains 0 core photos |
| Lithology Log | Certified geologist rock quality designation (RQD) log | Theoretical spec only | No certified field lithology log on disk |
| Inclinometer Casing | ABS grooved casing installed and grouted | `NOT_INSTALLED` | No downhole casing placed |
| Slurry Mix Record | Batch grouting log with water-cement ratios | Missing | No slurry inspection records on disk |
| GSI / BRO Field Sign-off | Joint inspection sign-off from Project Swastik | Missing | Pending field drilling campaign |

### 3. Separation of Engineering Design from Field Reality
The detailed geotechnical profile in `engine/physical_deployment_engine.py` (0.0–3.2m Colluvial debris, 3.2–11.8m sheared phyllite, 11.8–25.0m Daling chlorite-sericite schist) serves exclusively as an **engineering pre-drilling baseline design**. It is strictly segregated from field ground truth.

### 4. Authoritative Borehole Verdict
`BOREHOLE_EVIDENCE_MISSING` — Under Phase V5.2, until photographic evidence of core boxes and certified drilling reports are signed and hashed into the ledger, downhole geotechnical telemetry remains classified as uncommissioned.
