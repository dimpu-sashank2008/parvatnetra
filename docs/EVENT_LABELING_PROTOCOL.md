# PARVATNETRA / PAHAD AI — Scientific Event Labeling & Negative Control Protocol

**Document ID**: `PAHAD-PROTO-04-LABELING`  
**Standard**: SIH-26001 Disaster Intelligence & Geotechnical Safety Protocol  
**Classification**: Scientific Engineering Standard  
**Version**: `4.0.0` (Phase 4 Master Specification)  

---

## 1. Executive Summary & Problem Formulation

The **PAHAD AI** Landslide Event Prediction Model is formulated strictly as a binary classification problem:

$$Y \in \{0, 1\}$$

Where:
- $Y = 1$ denotes a **verified catastrophic slope failure, rockfall, debris flow, or rotational slide** occurring within a specified forward forecast horizon $\Delta t \in \{6\text{h}, 12\text{h}, 24\text{h}, 48\text{h}\}$ relative to an observation time $t_0$.
- $Y = 0$ denotes a **verified non-failure negative control window** where a steep, susceptible slope remains in mechanical equilibrium under monitored environmental conditions without failure.
- $Y = \text{UNKNOWN}$ designates ambiguous windows, unverified reports, or samples within exclusion zones, which are **strictly excluded** from supervised model training and evaluation.

> [!IMPORTANT]
> **FoS vs Event Probability Separation**:
> The physical **Factor of Safety ($FoS$)** derived from Mohr-Coulomb limit equilibrium is **NOT** the target label. $FoS$ is an input feature representing instantaneous mechanics. $Y$ represents whether an actual macroscopic mass movement event occurred.

---

## 2. Positive Event Ground-Truth Criteria

A positive sample ($Y = 1$) is admitted into the training or validation corpus **only** if all four of the following criteria are satisfied:

1. **Institutional Ground-Truth Documentation**:
   The failure must be documented in official archives of:
   - Geological Survey of India (GSI) National Landslide Susceptibility Mapping (NLSM) and Post-Disaster Field Reconnaissance.
   - ISRO National Remote Sensing Centre (NRSC) / Bhoonidhi High-Resolution Post-Event InSAR and Optical Assessment.
   - State Disaster Management Authorities (Sikkim SDMA, Assam ASDMA, Mizoram DM&R, etc.).
   - Border Roads Organisation (BRO) Project Swastik / Pushpak Highway Incident Logs.
   - Public Works Department (PWD) Slope Clearance Reports.

2. **Temporal Traceability**:
   The failure timestamp must be documented with temporal uncertainty $\le 24.0\text{ hours}$. If only the month or season is known, the record is discarded from event-horizon classification.

3. **Geospatial Precision**:
   Exact scarp or initiation zone coordinates must fall inside the Northeast Region (NER) operational bounding box:
   - Latitude: $21.5^\circ\text{N}$ to $29.5^\circ\text{N}$
   - Longitude: $88.0^\circ\text{E}$ to $97.5^\circ\text{E}$

4. **Source Confidence Threshold**:
   Source confidence rating must be $\ge 0.70$ (on a $0.0\text{ to }1.0$ scale) based on corroboration from multi-agency reports or satellite validation.

---

## 3. Spatial & Temporal Exclusion Zones

To prevent contamination between actual failure processes and non-failure baseline measurements, **strict exclusion zones** are enforced around every documented landslide:

- **Spatial Buffer**: A circle of radius $R = 5.0\text{ km}$ centered on the event initiation coordinates.
- **Temporal Buffer**: A window of $\Delta T = \pm 7.0\text{ days}$ centered on the event initiation time.

Any candidate observation (positive or negative) falling within both the spatial ($< 5\text{ km}$) and temporal ($< 7\text{ days}$) buffer of a known event is classified as an **aftershock / secondary scarp movement** or **disturbed boundary** and is excluded from binary negative control selection.

---

## 4. Defensible Negative Control Strategy

A negative observation ($Y = 0$) cannot simply be picked at random from flat ground or calm days, as this produces trivial, artificially inflated model accuracy. Negative controls must satisfy:

1. **Topographic Realism**:
   - Slope gradient must be $\theta > 15.0^\circ$.
   - Flat river floodplains, valley basins, or plain surfaces ($\theta \le 15.0^\circ$) are **forbidden** as negative controls.

2. **Mechanical Stability**:
   - Instantaneous physical Factor of Safety must be $FoS \ge 1.10$.
   - Slopes hovering at marginal equilibrium ($1.00 \le FoS < 1.10$) without documented failure are marked `UNKNOWN` rather than stable negatives.

3. **Complete Environmental Coverage**:
   - Complete data coverage is required for primary antecedent rainfall ($R_{24\text{h}}$, $R_{72\text{h}}$), volumetric soil moisture ($VWC$), elevation, and slope.
   - Observations with missing critical weather triggers are excluded.

4. **Documented Non-Failure Verification**:
   - The negative control window must coincide with dry-season baselines or periods where continuous telemetry and satellite InSAR confirm zero slope velocity ($\le 5\text{ mm/year}$).
   - Must be located at least $5.0\text{ km}$ away from any documented landslide occurring within $7\text{ days}$.

---

## 5. Ambiguous & Unknown Data Handling

Observations that meet any of the following conditions are flagged as `UNKNOWN` and **strictly omitted** from supervised loss functions:

- Precipitation telemetry missing or corrupted during the 72h window preceding observation.
- Candidate located inside the $5\text{ km} \times 7\text{ day}$ event exclusion zone.
- Uncorroborated social media or unverified news mentions without official SDMA/GSI confirmation.
- Timing uncertainty $> 24.0\text{ hours}$.

---

## 6. Audit & Traceability Schema

Every labeled record in `data/labels/event_labels.csv` and `data/features/features_all.csv` includes:

| Field | Type | Description |
| :--- | :--- | :--- |
| `event_id` | `str` | Unique institutional identifier (e.g. `GSI-SK-2023-001`) |
| `sector_id` | `str` | Operational micro-catchment sector ID |
| `timestamp` | `str` | ISO 8601 observation timestamp |
| `event_label` | `int` | Binary ground-truth target: `1` = Event, `0` = Negative Control |
| `source` | `str` | Primary documenting agency (GSI, SDMA, BRO, etc.) |
| `source_confidence` | `float` | Verification confidence ($0.00$ to $1.00$) |
| `provenance` | `str` | `[HISTORICAL]` or `[LIVE]` |
| `exclusion_checked` | `bool` | True if verified against buffer exclusion engine |

---

## 7. Implementation & Verification Engine

The protocol is programmatically enforced by `engine/event_labeling.py` via the `EventLabeler` class.
The test suite `tests/test_event_labeling.py` asserts 100% compliance across all labeled observations in the PARVAT NETRA repository.
