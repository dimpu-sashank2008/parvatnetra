# PAHAD AI — Data Quality & Provenance Audit Report

**Classification**: `TRAINED_LIMITED_DATA`  
**Audit Status**: `OPERATIONAL`  
**Timestamp**: `2026-09-14T13:30:35.656535+00:00`

---

## 1. Summary Metrics

- **Total Operational Training Samples**: 36 (100% Real/Historical)
- **Documented Failure Events (Class 1)**: 17 (47.2%)
- **Negative Control Windows (Class 0)**: 19 (52.8%)
- **Isolated Synthetic Demo Samples**: 25 ([DEMO] isolated in `demo_train.csv`)
- **Feature Completeness**: 100.0%
- **Date Range**: `2022-05-16 09:00:00+00:00` to `2024-10-04 06:00:00+00:00`
- **Duplicated Records**: 0
- **Missing Coordinates / Timestamps**: 0

## 2. Spatiotemporal & Administrative Coverage

- **States Covered (8/8 NER states)**: Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura
- **Districts Covered (15)**: Aizawl, Cachar, Dima Hasao, East Khasi Hills, Gangtok, Kohima, Lunglei, Mangan, Noney, North Tripura, Pakyong, Papum Pare, Phek, Tamenglong, Tawang
- **Geographic Mountain Corridors**: 31 distinct basins/corridors

## 3. Data Provenance & Category Separation

| Category | Count | Storage Path | Provenance Badge | Operational Status |
| :--- | :--- | :--- | :--- | :--- |
| **DOCUMENTED EVENT** | 17 | `data/raw/historical_landslides_ner.csv` | `[HISTORICAL]` | OPERATIONAL |
| **ENGINEERED FEATURE** | 36 | `data/features/features_all.csv` | `[HISTORICAL]` | OPERATIONAL |
| **SYNTHETIC DEMO SAMPLE** | 25 | `data/features/demo_train.csv` | `[DEMO]` | DEMO ONLY (`PAHAD_DEMO_MODE=1`) |

## 4. Temporal Holdout Integrity

- **`real_train.csv`** (<= 2023-12-31): 16 samples
- **`real_val.csv`** (2024-01-01 to 2024-06-30): 12 samples
- **`real_test.csv`** (>= 2024-07-01): 8 samples

## 5. Scientific Limitation Disclosure

> [!IMPORTANT]
> The real historical dataset comprises 36 ground-truth event & control observations across 8 NER states. Because the real dataset is small, the model is designated **TRAINED_LIMITED_DATA**. Synthetic demo samples are strictly barred from operational models to maintain complete scientific integrity.
