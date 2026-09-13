# PARVATNETRA / PAHAD AI — Scientific Data Leakage Audit Report

**Document ID**: `PAHAD-REP-04-LEAKAGE`  
**Standard**: SIH-26001 Scientific Integrity & Operational AI Standard  
**Classification**: Engineering & Verification Audit  
**Audit Tool**: `scripts/check_event_leakage.py`  
**Execution Status**: `PASSED — 0 VIOLATIONS`  

---

## 1. Executive Summary

A comprehensive, zero-tolerance data leakage audit was conducted across the operational training, validation, and testing partitions of the **PAHAD AI Landslide Event Prediction Model**. The audit verified:

1. **Temporal Isolation**: Strict forward-time progression without lookahead.
2. **Partition Independence**: Zero sample or coordinate overlap between train, validation, and test sets.
3. **Feature-Window Integrity**: Monotonicity in cumulative hydrometeorological triggers ($R_{1\text{h}} \le R_{6\text{h}} \le R_{24\text{h}} \le R_{72\text{h}}$).
4. **Target Leakage**: Absolute isolation of ground truth labels from feature vectors.
5. **Data Purity**: Complete separation of synthetic demo records (`[DEMO]`) from real operational sets (`[HISTORICAL]`).

---

## 2. Partition Summary & Date Boundaries

| Partition | File Path | Total Rows | Positives | Negatives | Date Range (UTC) | Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TRAIN** | `data/features/real_train.csv` | 16 | 8 | 8 | 2022-05-16 to 2023-10-04 | Model fitting |
| **VALIDATION** | `data/features/real_val.csv` | 12 | 4 | 8 | 2024-02-14 to 2024-06-25 | Platt calibration & threshold tuning |
| **TEST** | `data/features/real_test.csv` | 8 | 5 | 3 | 2024-07-02 to 2024-10-04 | Held-out operational benchmark |

### Chronological Verification:
$$\max(t_{\text{TRAIN}}) = 2023\text{-}10\text{-}04\text{T}01:30:00\text{Z} < \min(t_{\text{VAL}}) = 2024\text{-}02\text{-}14\text{T}03:00:00\text{Z}$$
$$\max(t_{\text{VAL}}) = 2024\text{-}06\text{-}25\text{T}13:00:00\text{Z} < \min(t_{\text{TEST}}) = 2024\text{-}07\text{-}02\text{T}08:00:00\text{Z}$$

> [!NOTE]
> There is a 4-month temporal buffer between TRAIN and VAL, and a 7-day clean separation between VAL and TEST. No future data leaked backward into historical training.

---

## 3. Cryptographic Provenance Hashes

Each dataset split is cryptographically sealed with SHA-256 to ensure complete reproducibility:

| Partition | SHA-256 Fingerprint |
| :--- | :--- |
| **real_train.csv** | `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e` |
| **real_val.csv** | `ed732e2054f164ce6c64188fa63286f9f6004b9016fe28f09bc1b2d07ae6c83f` |
| **real_test.csv** | `29f84cf97424ea4b16260195c9607f2ef8c7280fe5b9e075c3dbb90ee2b35a64` |

---

## 4. Leakage Audit Check Matrix

| Check ID | Verification Rule | Expected | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **LEAK-01** | Duplicate sector + timestamp records within any partition | 0 | 0 | **PASSED** |
| **LEAK-02** | Cross-partition duplicate records (Train $\cap$ Val, Train $\cap$ Test, Val $\cap$ Test) | 0 | 0 | **PASSED** |
| **LEAK-03** | Temporal boundary sequence ($t_{\text{train}} < t_{\text{val}} < t_{\text{test}}$) | Strictly monotonic | Verified | **PASSED** |
| **LEAK-04** | Cumulative rainfall consistency ($R_{1\text{h}} \le R_{6\text{h}} \le R_{24\text{h}} \le R_{72\text{h}}$) | Monotonic non-decreasing | Monotonic across all 36 samples | **PASSED** |
| **LEAK-05** | Target label `event_label` excluded from input feature vectors | Target excluded | Verified by `to_feature_vector()` | **PASSED** |
| **LEAK-06** | Zero synthetic demo data (`[DEMO]`) present in real training sets | 0 samples | 0 samples detected | **PASSED** |
| **LEAK-07** | Spatial & temporal buffer exclusion ($\ge 5\text{ km}$ / $\ge 7\text{ days}$ from events) | Zero boundary violations | Verified by `EventLabeler` | **PASSED** |

---

## 5. Audit Conclusion

The operational landslide event prediction dataset satisfies all scientific invariants required for **SIH-26001** and academic rigor. The model training pipeline operates strictly on leakage-free, temporally holdout partitions.
