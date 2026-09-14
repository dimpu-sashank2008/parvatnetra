# PAHAD AI — Model Validation Strategy & Spatiotemporal Protocol
**System**: PARVAT NETRA / PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Standard**: Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform  
**Document**: `reports/pahad_validation_strategy.md`  
**Classification**: `TRAINED_LIMITED_DATA`  

---

## 1. Scientific Rationale: Rejecting Naive Random Cross-Validation

In geotechnical hillslope and geohazard modeling, **naive random $k$-fold cross-validation** or random `train_test_split` is scientifically indefensible. Landslide failure phenomena exhibit severe spatiotemporal autocorrelation:
1. **Temporal Clustering**: Consecutive observation windows within the same storm event share identical antecedent precipitation indices ($API_{30d}$), prolonged pore-water saturation, and localized soil degradation. Randomly assigning records from the same storm to both training and test sets leaks future knowledge into past predictions, producing unrealistically high test metrics that collapse in operational deployment.
2. **Spatial Autocorrelation**: Mountain slopes within the same lithological formation, river basin, or highway cut share slope angles, joint sets, weathering profiles, and vegetative cover. Random splits sample proximate locations, effectively testing spatial memorization rather than geotechnical generalization.

To eliminate data leakage and ensure true operational defensibility, PARVAT NETRA enforces **Strict Temporal Holdout** as its primary validation framework and **Grouped Spatial Cross-Validation** as its secondary transferability audit.

---

## 2. Primary Strategy: Strict Temporal Holdout

The curated operational dataset ($N=36$ samples: 17 documented GSI landslide failure events, 19 verified non-failure control windows) is partitioned chronologically across three non-overlapping historical epochs:

```
                                  TIME AXIS (2022 -> 2024)
  ====================================================================================>
  [        TRAIN PARTITION        ] | [     VALIDATION PARTITION     ] | [ TEST PARTITION ]
  <= 2023-12-31                     | 2024-01-01 to 2024-06-30         | >= 2024-07-01
  N = 16 samples                    | N = 12 samples                   | N = 8 samples
  8 Events / 8 Controls             | 4 Events / 8 Controls            | 5 Events / 3 Controls
  ====================================================================================>
```

### 2.1 Training Partition (`real_train.csv`)
- **Temporal Boundary**: Historical records $\le \text{2023-12-31}$.
- **Composition**: $N=16$ records (8 documented landslide failures, 8 verified stable controls).
- **Physical Regimes**: Encompasses historical monsoon events of 2022 and 2023 across Sikkim, Assam, and Meghalaya, including the catastrophic October 2023 South Lhonak Glacial Lake Outburst Flood (GLOF) sequence along the Teesta River basin.
- **Role**: Base estimator training (`GradientBoostingClassifier`, `RandomForestClassifier`, `XGBoost`).

### 2.2 Validation Partition (`real_val.csv`)
- **Temporal Boundary**: Chronological window from $\text{2024-01-01}$ to $\text{2024-06-30}$.
- **Composition**: $N=12$ records (4 documented landslide failures, 8 verified stable controls).
- **Physical Regimes**: Encompasses dry-season baseline equilibrium, pre-monsoon convective cloudbursts, and the May 2024 Severe Cyclonic Storm *Remal* impact across southern NER states (Mizoram, Manipur, Tripura).
- **Role**: Hyperparameter optimization, decision threshold selection, and out-of-fold Platt sigmoid probability calibration (`CalibratedClassifierCV` with `PredefinedSplit`).

### 2.3 Held-Out Test Partition (`real_test.csv`)
- **Temporal Boundary**: Chronological window from $\text{2024-07-01}$ onwards ($\ge \text{2024-07-01}$ to $\text{2024-10-04}$).
- **Composition**: $N=8$ records (5 documented landslide failures, 3 verified stable controls).
- **Physical Regimes**: Encompasses the peak 2024 monsoon flash floods, July 2024 NH-10 Pakyong washouts, and August/September 2024 Nagaland NH-29 Pagala Pahar failures.
- **Role**: Strictly blinded operational evaluation. Never touched during model fitting, feature scaling, or calibration tuning.

---

## 3. Secondary Strategy: Grouped Spatial Validation

To evaluate whether models trained on one Himalayan river valley generalize to unmonitored sectors in neighboring ranges, the platform implements **Grouped Spatial Cross-Validation** (`GroupKFold`) grouped by administrative corridors and hydrological basins:

| Spatial Group | Strategic Infrastructure Corridor | Dominant Lithology / Basin | Key Monitoring Sectors |
| :--- | :--- | :--- | :--- |
| `sikkim_teesta_corridor` | NH-10 (Sevoke-Gangtok) & NH-717A | Daling Group mica schist & phyllite | `SK-NH10-KM48`, `SK-SINGTAM-01`, `SK-MANGAN-01` |
| `assam_barak_corridor` | Lumding-Badarpur Railway & NH-27 | Surma & Barail group sandstone/shale | `AS-DIMA-01`, `AS-GUWAHATI-01` |
| `meghalaya_khasi_basin` | NH-6 (Shillong-Silchar corridor) | Shillong Plateau quartzite & sandstone | `ML-CHERRA-01`, `ML-SONAPUR-01` |
| `arunachal_kameng_axis` | Bhalukpong-Bomdila-Tawang Axis | High-grade gneiss & metamorphic schists| `AR-BHALUK-01`, `AR-SELA-01` |
| `nagaland_kohima_lifeline` | NH-29 (Dimapur-Kohima) | Disang flysch shale & siltstone | `NL-PIPHEMA-01`, `NL-DZUDZA-01`, `NL-PAGALA-01`|
| `manipur_tupul_basin` | Jiribam-Imphal Railway Corridor | Tertiary sedimentary fold belt | `MN-TUPUL-01`, `MN-NONEY-01`, `MN-JIRIBAM-01` |
| `mizoram_aizawl_basin` | NH-54 / NH-306 Lifeline | Bhuban formation shale/siltstone | `MZ-HUNTHAR-01`, `MZ-SAIRANG-01` |
| `tripura_dhalai_hills` | NH-8 Hill Sections | Tipam sandstone & claystone | `TR-BARAMURA-01` |

**Invariant**: In any spatial fold $k$, all records belonging to a given corridor are isolated exclusively in the validation split, proving that the model is not memorizing sector-specific elevation or slope constants.

---

## 4. Leakage Verification Protocol

The validation architecture is continuously audited by `scripts/check_event_leakage.py`, which executes before every training run and asserts:
1. **Zero Duplicate Keys**: $\text{count}(\text{sector\_id} \times \text{timestamp}) = 1$ everywhere.
2. **Strict Chronological Monotonicity**:
   $$\max(t_{\text{train}}) < \min(t_{\text{val}}) \quad \text{and} \quad \max(t_{\text{val}}) < \min(t_{\text{test}})$$
3. **Antecedent Lookahead Invariant**: Multi-window rainfall accumulation must be monotonically non-decreasing backward from observation timestamp:
   $$R_{1\text{h}} \le R_{3\text{h}} \le R_{6\text{h}} \le R_{12\text{h}} \le R_{24\text{h}} \le R_{48\text{h}} \le R_{72\text{h}}$$
4. **Target Isolation**: Target variable `event_label` is strictly segregated from input feature matrix $\mathbf{X}$.
5. **Complete Synthetic Segregation**: The `[DEMO]` partition (`demo_train.csv`) is cryptographically checked; zero demo records may enter `real_train.csv`, `real_val.csv`, or `real_test.csv`.

---

## 5. Minimum Sample Threshold & Honest Limitation

The operational event dataset currently contains 36 verified ground-truth records across 8 NER states. In accordance with Section 10 of the PARVAT NETRA engineering standards:
- **Mandatory Tier**: `TRAINED_LIMITED_DATA` (`DATA-GROUNDED RESEARCH PROTOTYPE`).
- **No Falsification**: The engineering team strictly refuses to manufacture synthetic "events" to claim artificial sample sizes in the thousands.
- **Operational Integration**: Calibrated event probability $P(\text{event})$ is NEVER used as a single point of failure; it is integrated with physical Factor of Safety ($FoS$) and regional I-D rainfall thresholds under the **2-of-3 Independent Confirmation Rule**.
