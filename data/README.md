# PARVAT NETRA / PAHAD AI — Training Data Pipeline & Repository

This directory manages training, validation, and evaluation data for the **PAHAD AI Landslide Event Prediction System** across the eight states of the North Eastern Region (NER):
1. **Arunachal Pradesh**
2. **Assam**
3. **Manipur**
4. **Meghalaya**
5. **Mizoram**
6. **Nagaland**
7. **Sikkim**
8. **Tripura**

---

## 1. Directory Structure

```text
data/
├── raw/            # Authoritative raw incident reports, GSI NLSM catalogs, NRSC landslide atlases
├── processed/      # Cleaned and standardized time-indexed observation records
├── labels/         # Ground truth binary event labels (landslide_event = 0 / 1) with spatio-temporal metadata
├── features/       # Tabular feature matrices (train, validation, test splits)
├── geospatial/     # Existing DEM, roads, satellite, and terrain product layers
└── README.md       # Pipeline specifications and data provenance documentation
```

---

## 2. Event Target Variable & Label Design

The core target variable is:
$$\text{landslide\_event} \in \{0, 1\}$$

- **`1` (Documented Failure Event)**: Verified mass movement failure event recorded in GSI NLSM, State Disaster Management Authority (SDMA) incident logs, or NDRF/SDRF operational reports.
- **`0` (Control / Non-Failure Window)**: Documented stable hillslope periods under diverse conditions:
  - Dry season baseline equilibrium
  - Moderate monsoon rainfall without mass failure
  - Heavy rainfall on stable/competent quartzite/basalt lithologies
  - Seismic ground-motion shaking below liquefaction/trigger thresholds

Each sample contains:
```json
{
  "sector_id": "SK-NH10-KM48",
  "event_timestamp": "2024-10-04T06:00:00Z",
  "latitude": 27.3300,
  "longitude": 88.6100,
  "state": "Sikkim",
  "district": "Pakyong",
  "source": "GSI Post-Disaster Field Survey",
  "source_confidence": 0.96,
  "provenance": "[HISTORICAL]",
  "event_horizon": "6h"
}
```

---

## 3. Temporal & Spatial Splitting Strategy

To prevent spatial and temporal data leakage:
1. **Temporal Holdout (Primary)**:
   - **`TRAIN`**: Historical events up to 2023-12-31.
   - **`VALIDATION`**: Events from 2024-01-01 to 2024-06-30.
   - **`TEST`**: Events from 2024-07-01 onwards.
2. **Spatial Group Cross-Validation**:
   - `GroupKFold` grouping by geographic river basin / highway corridor (e.g. `sikkim_teesta_corridor`, `mizoram_aizawl_basin`, `manipur_tupul_corridor`) ensuring no sector appears in both train and validation folds of any split.

---

## 4. Scientific Honesty & Provenance

When public authoritative landslide records with precise geotechnical and temporal timestamps are sparse, the model tier is formally cataloged as:
`TRAINED_LIMITED_DATA`

Never substitute fabricated observations as `[LIVE]` or `[HISTORICAL]`. Verification sequences created for unit testing are explicitly designated `[DEMO]` or `[SIMULATED]`.
