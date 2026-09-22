# PARVAT NETRA / PAHAD AI — PHASE V5.2
## SPATIAL LEAKAGE AUDIT & CORRIDOR ISOLATION REPORT

**Document ID:** `PN-DOC-V5.2-SPATIAL-LEAKAGE`  
**Phase:** `V5.2 — External Data Expansion & Ground-Truth Ingestion`  
**Primary Corridor:** `CORR-NH10-SIKKIM-KM48`  
**Status:** `AUDITED & CORRIDOR-ISOLATED`  
**Operating Boundary:** Strictly Localhost-Only (`127.0.0.1`)

---

### 1. Spatial Leakage & Autocorrelation Challenge
Mountain slope failures cluster along specific highway corridors and geological fault lines. If training and test sets share identical GPS coordinates or overlapping hillslope segments, models memorize local lithology rather than learning generalized physical failure mechanics.

---

### 2. Spatial Verification Invariants

#### 2.1 Multi-State Geographic Diversity
The canonical dataset covers all 7 mountainous states in the North-Eastern Region (NER):
- Sikkim (16 events, 38.1%)
- Assam (7 events, 16.7%)
- Manipur (6 events, 14.3%)
- Mizoram (4 events, 9.5%)
- Nagaland (3 events, 7.1%)
- Meghalaya (3 events, 7.1%)
- Arunachal Pradesh (3 events, 7.1%)

#### 2.2 Coordinate Deduplication & Separation
- **Zero Identical Coordinates Across Distinct Events**: All distinct canonical events have separated spatial coordinates unless explicitly linked via `merged_sources`.
- Events occurring on the same highway axis (e.g. NH-10) are mapped to their specific kilometer markers (Km 29, Km 42, Km 48.2), with distinct slope aspects, elevations, and geotechnical profiles.

#### 2.3 Corridor-Level Spatial Holdout
Where spatial validation is conducted, events within a contiguous catchment basin or highway sector (e.g. Pakyong / Teesta Gorge basin) are held out together to evaluate cross-basin model transferability without spatial proximity leakage.

---

### 3. Automated Test Verification
Verified under `tests/test_v5_2_spatial_leakage.py`:
- `test_multi_state_representation`: PASSED
- `test_no_identical_duplicate_coordinates_without_merge`: PASSED
- `test_corridor_clustering_isolation`: PASSED
