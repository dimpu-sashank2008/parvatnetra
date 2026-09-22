# PARVAT NETRA • PAHAD AI — PHASE V5.3
# GEODETIC COORDINATE VALIDATION REPORT

**Phase**: V5.3 — External Source Evidence Verification & Canonical Event Forensics  
**Status**: VERIFIED & AUDITED  
**Corridor**: CORR-NH10-SIKKIM-KM48 & NER Regional Network  
**Overall Verdict**: `V5_3_EVIDENCE_VERIFIED`  
**Date**: September 2026  

---

## 1. Executive Summary

This report establishes the geodetic validity, spatial completeness, and precision classifications of the spatial coordinates recorded for all 42 canonical landslide events in PARVAT NETRA.

Accurate georeferencing is essential for coupling events with DEM slope angles, InSAR displacement tracks, and IMD precipitation grids.
- **Coordinate Completeness**: 100.0% (42 of 42 events possess valid, non-null numeric coordinates)
- **Bounding Box Conformance**: 100.0% within the Eastern Himalayan / NER geographic envelope
- **Geographic Envelope**: Latitude $[21.5^\circ \text{N}, 30.0^\circ \text{N}]$, Longitude $[88.0^\circ \text{E}, 97.5^\circ \text{E}]$
- **Out-of-Bounds Coordinates**: Exactly ZERO (0)
- **Zero Inverted Coordinates** (Lat/Lon swap checked and eliminated)

---

## 2. Spatial Bounding Box & Territorial Distribution

All 42 canonical events map strictly inside the North Eastern Region of India:

| State | Event Count | Latitude Range ($^\circ\text{N}$) | Longitude Range ($^\circ\text{E}$) | Strategic Corridors Covered |
|:---|:---:|:---:|:---:|:---|
| Sikkim | 8 | 27.15 – 27.65 | 88.45 – 88.62 | NH-10, North Sikkim Highway, Dikchu |
| West Bengal (Kalimpong/Darjeeling) | 3 | 26.85 – 27.05 | 88.25 – 88.55 | NH-10 (KM 29 to KM 48), Hill Cart Road |
| Assam | 5 | 25.10 – 26.20 | 91.70 – 93.10 | Lumding-Badarpur Railway, NH-37 |
| Meghalaya | 5 | 25.15 – 25.55 | 91.50 – 92.40 | NH-06 Lifeline, Sohra Plateau, Jowai |
| Manipur | 5 | 24.75 – 25.00 | 93.50 – 93.75 | NH-37 Imphal-Jiribam, Tupul NFR Yard |
| Mizoram | 6 | 22.85 – 24.25 | 92.65 – 92.85 | NH-54, Aizawl Arterial Connectors |
| Nagaland | 4 | 25.60 – 25.75 | 94.00 – 94.45 | NH-29 Lifeline, Pagala Pahar, Phek |
| Arunachal Pradesh | 4 | 27.15 – 27.60 | 92.40 – 93.70 | Balipara-Charduar-Tawang (BCT), NH-415 |
| Tripura | 3 | 23.80 – 24.00 | 92.20 – 92.30 | Jampui Hills Ridgeline, Kanchanpur |

---

## 3. Coordinate Precision Tiers

Each event record explicitly documents its coordinate source methodology:

1. **`SURVEY_DGPS` (Differential GPS / Total Station)**:
   - Precision: $\pm 1 \text{ to } 5 \text{ meters}$
   - Applied to major surveyed disasters, e.g., Tupul Railway Yard (`24.7865°N, 93.6394°E`) and Salem Veng Quarry (`23.7271°N, 92.7176°E`).
2. **`HIGH_RES_DEM` (Ortho-rectified Cartographic Mapping)**:
   - Precision: $\pm 10 \text{ to } 25 \text{ meters}$
   - Derived from GSI post-disaster maps and Cartosat-1 10m DEM overlay.
3. **`CORRIDOR_CHAINAGE` (Highway Chainage Centroid)**:
   - Precision: $\pm 50 \text{ to } 100 \text{ meters}$
   - Derived from official BRO / NHIDCL kilometer stones (e.g., NH-10 KM 29, KM 48).
4. **`VILLAGE_CENTROID` (District Administrative Anchor)**:
   - Precision: $\pm 500 \text{ meters}$
   - Applied only to secondary candidate events (`EV-07`, `EV-25`, `EV-29`, `EV-32`, `EV-35`) which are quarantined from operational ML training.

---

## 4. Verification Assertion Summary

Automated tests in `tests/test_v5_3_coordinate_validation.py` confirm:
- `test_ner_and_himalayan_bounding_box`: PASSED
- `test_coordinate_precision_classifications`: PASSED
- `test_coordinate_completeness_100_percent`: PASSED
