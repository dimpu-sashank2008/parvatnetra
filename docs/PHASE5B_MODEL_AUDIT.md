# PARVAT NETRA / PAHAD AI — Phase 5B Scientific Model & Leakage Audit

**Document ID**: `PAHAD-AUDIT-5B-01`  
**Classification**: Scientific Methodology & Data Leakage Investigation  
**Phase**: Phase 5B — Real Temporal Prediction + Model Validation  
**Date**: September 2026  
**Auditor**: PARVAT NETRA AI Engineering Team  

---

## 1. Executive Summary

This audit rigorously examines the data pipeline, labeling criteria, feature construction, calibration methodology, and partition schemes currently implemented in `engine/event_labeling.py`, `engine/event_features.py`, `scripts/build_landslide_dataset.py`, `scripts/build_temporal_dataset.py`, and `scripts/train_event_models.py`.

The objective is to identify and resolve every potential source of data leakage, selection bias, and circular reasoning before building the true temporal multi-horizon prediction models.

---

## 2. Mandatory Audit Questionnaire (10 Critical Questions)

### Q1: What exactly constitutes a positive event?
- **Finding**: In the current catalog (`historical_landslides_ner.csv` and `NER_COMPREHENSIVE_EVENTS`), a positive event is a single historical disaster row evaluated at failure timestamp $T$ (e.g., `2024-10-04T06:00:00Z`).
- **Critical Flaw**: Currently, there is only **one observation per event**, taken at the moment of failure. Features like `rainfall_trigger_mm` represent the peak cumulative storm precipitation, and `ground_displacement` represents total post-failure scarp movement.
- **Remediation in Phase 5B**: A true early-warning dataset must construct **antecedent observation windows** prior to failure ($T-48\text{h}, T-36\text{h}, T-24\text{h}, T-12\text{h}, T-6\text{h}$). Each sample reflects environmental conditions known strictly at $T_{obs}$, with binary multi-horizon forecast targets indicating whether failure occurred within the subsequent $6\text{h}, 12\text{h}, 24\text{h}$, or $48\text{h}$.

---

### Q2: What exactly constitutes a negative/control observation?
- **Finding**: Negative controls were constructed from two mechanisms:
  1. Dry-season non-event dates (January–March) where rainfall is near zero and slopes are quiescent.
  2. Hand-crafted scenarios in `scripts/build_landslide_dataset.py` representing moderate monsoon or heavy rainfall on competent rock (`CTRL-*-HEAVY-01`).
- **Critical Flaw**: Many controls are synthetic archetypes rather than natural temporal windows from continuous environmental observations.
- **Remediation in Phase 5B**: Controls must be grounded in defensible observation periods with verified absence of slope failure, adequate temporal separation ($> 7\text{ days}$) and spatial separation ($> 5\text{ km}$) from documented events, with explicit provenance and non-event rationale logged.

---

### Q3: Is FoS used directly or indirectly to define labels?
- **Finding**: **YES. Severe selection bias detected.**
  - In `engine/event_labeling.py` (lines 159–162): candidate negative controls are rejected if $FoS < 1.10$.
  - In `scripts/build_temporal_dataset.py` (line 254): controls are discarded if $FoS < 1.20$.
  - In `scripts/build_landslide_dataset.py`: all positive events were assigned $FoS \in [0.45, 0.85]$, while negative controls were assigned $FoS \in [1.10, 1.90]$.
- **Impact**: Filtering controls by $FoS \ge 1.10$ creates a circular tautology: the machine learning model can trivially separate the classes by learning the FoS threshold, because non-failing slopes with marginal stability ($1.00 \le FoS < 1.10$) were artificially excluded from the negative class.
- **Remediation in Phase 5B**: **FoS must NOT be used as a criterion for label assignment.** Labels must be defined solely by empirical ground failure (landslide documented $= 1$, no landslide documented $= 0$). FoS is strictly an **input physical feature**, not a ground-truth label selector.

---

### Q4: Can any feature contain information from after the prediction timestamp?
- **Finding**: **YES, in current static event rows.**
  - `ground_displacement`: Values such as $48.0\text{ mm}$ (EV-01) or $65.0\text{ mm}$ (EV-03) were measured by geological survey teams during post-disaster field inspections. Using these as inputs for a prediction at or before failure leaks post-event displacement into ante-event features.
  - `rainfall_trigger_mm`: Represents the total precipitation of the triggering deluge, including rainfall that fell during and immediately after slope collapse.
- **Remediation in Phase 5B**: For any prediction window at $T_{obs} = T_{event} - \Delta t$, only rainfall accumulated **strictly up to $T_{obs}$** ($R_{1h}, R_{3h}, R_{6h}, R_{12h}, R_{24h}, R_{48h}, R_{72h}$) and creep deformation recorded **prior to $T_{obs}$** may be present. Post-event survey measurements must never appear in pre-event feature vectors.

---

### Q5: Can rainfall windows accidentally cross into the future?
- **Finding**: In `scripts/build_landslide_dataset.py`, sub-interval rainfalls were computed using heuristic ratio multipliers on total trigger rainfall ($R_{6h} = 0.40 \cdot R_{24h}$, $R_{1h} = 0.35 \cdot R_{6h}$).
- **Risk**: Fixed heuristic multipliers do not reflect actual hyetograph kinematics and risk assuming a uniform rainfall pulse.
- **Remediation in Phase 5B**: Use genuine antecedent precipitation curves where rainfall intensity evolves naturally up to $T_{obs}$, strictly ensuring that $R_{1h} \le R_{3h} \le R_{6h} \le R_{12h} \le R_{24h} \le R_{48h} \le R_{72h} \le API_{3d} \le API_{7d}$.

---

### Q6: Can event information leak into controls?
- **Finding**: Hand-crafted controls assigned identical static sector attributes (e.g., slope $= 42.0^\circ$, elevation $= 890\text{ m}$) as known failure sites.
- **Remediation in Phase 5B**: Negative control windows must be verified to have zero spatial-temporal overlap ($> 5\text{ km}$ and $> 7\text{ days}$) from any documented active landslide. Distance from nearest known event and time from nearest event must be explicitly recorded in metadata.

---

### Q7: Can spatially adjacent observations leak between train and test?
- **Finding**: The Phase 4 split was chronological by date (`train` $\le 2023$, `val` H1 2024, `test` H2 2024). However, certain high-activity corridors (e.g., NH-10 Teesta corridor, Sikkim) had events in 2023 (Singtam GLOF) in `train` and events in 2024 (Km 48 Pakyong) in `test`.
- **Risk**: While temporal holdout was maintained, spatial correlation exists for geographically recurring corridors.
- **Remediation in Phase 5B**: In addition to chronological partitioning, implement **Event-Grouped Spatial-Temporal validation** ensuring that specific micro-catchments/corridors are evaluated on genuinely held-out sectors where data volume permits.

---

### Q8: Can repeated observations from the same event leak across partitions?
- **Finding**: Currently, each event had only 1 observation, so cross-partition window leakage was not possible.
- **Risk in Phase 5B**: As we generate multiple antecedent prediction windows ($T-48\text{h}, T-36\text{h}, T-24\text{h}, T-12\text{h}, T-6\text{h}$) for each of the 17 verified events, **ALL windows derived from event $E_i$ must be assigned to the EXACT SAME partition.**
- **Enforcement**: Grouping by `event_id` is mandatory during dataset splitting. A sample from Event 01 must never appear in both train and validation or test.

---

### Q9: Is Platt calibration trained only on appropriate data?
- **Finding**: In `scripts/train_event_models.py`, `PredefinedSplit` was used:
  - Fold -1: Training data
  - Fold 0: Validation data
  - Held-out: Test data
- **Assessment**: This design correctly isolates the test partition from the sigmoid fitting. However, with validation sample size $N_{val} = 12$ ($4$ positives, $8$ controls), Platt calibration parameters ($A, B$) carry high variance.
- **Remediation in Phase 5B**: Evaluate both uncalibrated probabilities, Platt scaling, and isotonic regression, comparing Brier score and Expected Calibration Error (ECE) across validation and held-out test splits.

---

### Q10: Are normalization/imputation statistics learned only from training data?
- **Finding**:
  - In `engine/event_features.py`, `TRAINING_SPLIT_MEDIANS` was hardcoded from `real_train.csv`.
  - In `models/pahad_event_model.metadata.json`, `CRI` was listed as an input feature driver (`top_drivers: {"CRI": 0.0505}`).
- **Critical Flaw**: **CRI (Composite Risk Index) is an output of the PAHAD Fusion Engine.** Using CRI as an input feature into the event classifier introduces circular target leakage!
- **Remediation in Phase 5B**:
  1. **Immediately remove `CRI` from the feature matrix.**
  2. Imputation statistics (medians) and scaling parameters must be fitted **strictly on `train_df`** and applied downstream to `val_df` and `test_df`.

---

## 3. Summary of Mandatory Fixes for Phase 5B

| # | Flaw Identified | Action Required |
|---|----------------|-----------------|
| 1 | Positive events are single-row post-event snapshots | Construct antecedent observation windows ($T-48h$ to $T-6h$) |
| 2 | FoS used to filter negative controls ($FoS \ge 1.10$) | Remove FoS filtering from label definition; FoS is strictly an input feature |
| 3 | Post-event ground displacement and peak trigger rain in features | Restrict features to information strictly known at $T_{obs}$ |
| 4 | CRI present in input feature vector | Completely eliminate CRI from feature schema |
| 5 | Single 24h horizon model masquerading as multi-horizon | Build dedicated targets (`target_6h`, `target_12h`, `target_24h`, `target_48h`) |
| 6 | Potential window leakage across partitions | Enforce strict `event_id` grouping during temporal partitioning |
| 7 | Threshold 0.70 hardcoded without validation tuning | Perform systematic validation sweep ($0.30 - 0.90$) per horizon |

---

## 4. Audit Conclusion

The baseline Phase 4/5A system established an operational pipeline, but its evaluation suffered from:
1. Single-row co-incident event sampling rather than true antecedent early-warning windows.
2. Selection bias via FoS filtering in negative controls.
3. Target leakage via inclusion of the composite CRI score in training features.

Phase 5B will rebuild the dataset with **strict temporal antecedent windows**, **independent negative controls**, and **leakage-free multi-horizon targets**.
