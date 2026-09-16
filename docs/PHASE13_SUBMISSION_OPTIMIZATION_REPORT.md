# PARVAT NETRA — Phase 13: Submission Optimization Report
**Smart India Hackathon 2026 | Problem Statement ID: 26001**
*Ministry of Development of North Eastern Region (MDoNER)*

---

## Executive Summary
PARVAT NETRA has been optimized specifically for evaluator assessment in the SIH 2026 Top-500 to Top-5 finalist selection. Live-demo theatrics and rehearsal scripts have been eliminated in favor of prototype clarity, scientific defensibility, technical depth, operational realism, and 100% consistency between the operational runtime prototype and the submission slide deck.

---

## 1. Prototype First Impression (Section A)
- **Regional Default**: Upon initial access, the Leaflet GIS canvas initializes to the full North Eastern Region (NER) bounding box `[[21.8, 88.0], [29.5, 97.5]]` displaying all 8 North Eastern states:
  1. Arunachal Pradesh
  2. Assam
  3. Manipur
  4. Meghalaya
  5. Mizoram
  6. Nagaland
  7. Sikkim
  8. Tripura
- **Auto-Zoom Suppression**: Background polling and initial sector binding explicitly invoke `onCorridorSelectionChanged(sectorId, false)` preventing disorienting automated camera movements or snapping to a single corridor. Evaluators maintain full spatial awareness of the entire Himalayan frontier.
- **Brand Title & Subtitle**: Clearly displays `PARVAT NETRA — AI-Assisted Landslide Risk Intelligence for the Northeast` in GIGW 3.0 compliant high-contrast typography.

---

## 2. Information Hierarchy (Section B & C)
The user interface adheres to a strict, non-overwhelming five-tier cognitive hierarchy:
1. **GIS MAP (Primary)**: 8-column wide interactive spatial canvas displaying road networks, real-time rainfall contours, InSAR deformation vectors, and in-situ monitoring pins.
2. **CURRENT RISK (Secondary)**: Fast KPI summary header displaying multi-modal Composite Risk Index ($CRI$), Limit Equilibrium Factor of Safety ($FoS$), and Event Probability ($P_{event}$).
3. **RISK EVOLUTION (Third)**: Integrated directly on the map via the temporal scrubber controller ($T_{-48h}$ to $T_{+48h}$ forecast), demonstrating slope saturation progression without page remounts.
4. **WHY THIS RISK? (Fourth)**: Tri-partite explainability breakdown in the Decision Intelligence Card attributing the physical and meteorological drivers ($Lf$ infiltration, matric suction loss, basal shear scour).
5. **DATA & PROVENANCE (Fifth)**: Explicit provenance tagging distinguishing live external feeds from physics simulations and historical datasets.

> [!NOTE]
> **Risk Evolution vs. Risk Evaluation**:
> - **Risk Evolution**: The on-map 48h temporal progression visualization.
> - **Risk Evaluation**: The former duplicate right-hand slide drawer, which has been cleanly removed to eliminate visual clutter and avoid conflicting layout columns.

---

## 3. PAHAD AI at a Glance (Section D)
The Decision Intelligence Card synthesizes the complete predictive state in a single compact glance:
- **Factor of Safety ($FoS$)**: Mohr-Coulomb physical limit equilibrium (e.g. `1.040` Conditionally Stable, or `0.745` Critical).
- **Event Probability ($P_{event}$)**: Calibrated GBDT landslide classifier output for 24h forecast window (e.g. `72.0%`).
- **Composite Risk Index ($CRI$)**: Multimodal fusion index combining physical mechanics, precipitation, deformation, and exposed assets (e.g. `68.0 / 100` ORANGE / RED).
- **Risk Band & Confidence**: High-contrast categorical indicator (`RED ALERT`, `ORANGE ALERT`, `YELLOW WATCH`, `GREEN NORMAL`) paired with feature completeness confidence (`HIGH`, `MED`, `LOW`).
- **Tri-Partite Evidence Breakdown**:
  - *Supporting Evidence*: IMD precipitation exceedance, steep slope cut $>35^\circ$, InSAR line-of-sight displacement, tension crack apertures.
  - *Contradicting Evidence*: Gentle plains $<3^\circ$ planar failure unviable, stable vegetative cover ($NDVI > 0.65$).
  - *Missing Telemetry*: Uninstrumented pore pressure channels or off-line rain gauges transparently flagged.

---

## 4. Scientific Story & Mechanical Grounding (Section E)
The prototype communicates a cohesive, causal-free physical-to-statistical narrative:
$$\text{Precipitation (IMD/Radar)} \longrightarrow \text{Hydrological Vadose Infiltration (Green-Ampt)} \longrightarrow \text{Suction Degradation (van Genuchten SWCC)}$$
$$\longrightarrow \text{Basal Shear & Toe Scour (Teesta Hydrodynamics)} \longrightarrow \text{Factor of Safety } FoS \longrightarrow \text{ML Event Probability } P_{event}$$
$$\longrightarrow \text{Multimodal Corroboration (2-of-3 Rule)} \longrightarrow \text{Human-in-the-Loop EOC Decision Support}$$

No false causal claims are made; ML features are described as "contributing model drivers" rather than proven root causes.

---

## 5. Model Honesty & Data Truth (Sections F & G)
PARVAT NETRA strictly rejects inflated AI claims:
- **Event Classifier**: `TRAINED_LIMITED_DATA / RESEARCH PROTOTYPE` (Trained on verified NER historical landslides with explicit temporal holdout; not marketed as an overfitted production oracle).
- **Temporal Sequence Model**: `NOT_TRAINED / PHYSICS-INFORMED SURROGATE` (The LSTM module in `engine/pahad_lstm.py` is explicitly audited and documented as a mathematical physics surrogate; no fabricated deep learning weights are claimed).
- **Data Truth Provenance Matrix**:
  | Stream / Modality | Provenance Badge | Runtime Source |
  | :--- | :--- | :--- |
  | **Precipitation** | `[LIVE]` | IMD GFS/WRF Numerical Weather Prediction API |
  | **Vector Base Layers** | `[CACHED]` | Local PostGIS GeoJSON & OpenStreetMap Tile Cache |
  | **Historical Landslides** | `[HISTORICAL]` | GSI National Landslide Susceptibility Mapping (NLSM) |
  | **Digital Elevation Model** | `[MODELLED]` | ISRO CartoDEM 30m & Copernicus GLO-30 DEM |
  | **In-Situ Piezometers / Tilt** | `[SIMULATED]` | Synthetic Mohr-Coulomb vadose zone simulation |
  | **Civil Defense Sirens** | `[AUTH_REQUIRED]` | Dual-key EOC human authorization protocol |
  | **Unmonitored Sectors** | `[UNAVAILABLE]` | Missing telemetry marked missing; never hallucinated |

---

## 6. Role Realism & Zero-Trust RBAC (Section H)
The platform enforces role separation via authoritative backend server-side session authentication:
- **Public / Citizen**: Real-time road status, detour navigation, safety advisories, and crowdsource hazard reporting. All siren controls and authority review drawers are completely absent from the DOM.
- **Field Operator (BRO / SDRF)**: Mobile-optimized inspection queue, offline sync queue, GPS distress tag verification, and aperture measurement inputs. No siren arming privileges.
- **District / State Authority (DDMA / SDMA)**: Full Emergency Operations Centre (EOC) console, multi-modal risk triage, BRO Swastik plant deployment, and dual-key siren dispatch.
- **Query Parameter Tampering Immune**: Direct navigation to `/?mode=authority` by unauthenticated sessions strictly defaults to the public experience.

---

## 7. Top-1 Differentiator (Section I)
Unlike conventional hackathon entries that present isolated black-box predictors or disconnected maps, PARVAT NETRA delivers an end-to-end mission-critical architecture:
$$\mathbf{Physics} + \mathbf{Machine\ Learning} + \mathbf{Multi\text{-}Source\ Evidence} + \mathbf{Explainability} + \mathbf{Provenance} + \mathbf{Human\ Authorization}$$

---

## 8. PPT Consistency Reconciled (Section J)
All 8 slides in `docs/PARVAT_NETRA_SIH_Winning_Deck.pptx` have been rebuilt and programmatically synchronized with the codebase:
- Telemetry explicitly designates in-situ geotechnical sensors as `[SIMULATED]`.
- Models explicitly designate the GBDT classifier as `TRAINED_LIMITED_DATA` and the LSTM as `NOT_TRAINED / SURROGATE`.
- Physical equations for $FoS$ and $CRI$ exactly match backend implementations in `engine/pahad_geotech.py` and `engine/pahad_fusion.py`.
- Slide deck passes 100% of unit assertions in `tests/test_sih_deck.py`.

---

## 9. Safety Architecture Verified (Section N)
All operational safety environment variables are permanently locked to their fail-safe defaults in `app.py`:
- `ENABLE_PUBLIC_DISPATCH = 0` (Public cannot broadcast emergency sirens)
- `SIREN_DRY_RUN = 1` (Hardware siren actuators fire simulated test pulses)
- `CAP_PRODUCTION_DISPATCH = 0` (NDMA Sachet alerts remain in sandboxed test harness)
- `SACHET_PRODUCTION_DISPATCH = 0` (No inadvertent external push broadcasts)
- `CELL_BROADCAST_PRODUCTION = 0` (C-DOT CBS channel CH-4370 restricted to test logging)
- `PUBLIC_DEMO_TEST_ONLY = 1` (Strict verification sandbox active)
