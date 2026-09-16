# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-16T01:06:55.381987+00:00  
**Dataset SHA-256:** `a23e210b85378577cfa3312fcaabd3ffc377b66ddf44ad642056d4c5b55cca14`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 48.47 / 100
- **Average Mohr-Coulomb FoS:** 1.334
- **Peak 24h Rainfall Recorded:** 135.0 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 2
  - `HIGH`: 15
  - `MODERATE`: 3
  - `LOW`: 0

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 135.0 mm | 5.2 M | 0.767 | 55.83 | **55.83** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 55.4 mm | 5.2 M | 1.765 | 51.93 | **51.93** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 74.6 mm | 5.2 M | 2.019 | 42.25 | **42.25** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 87.8 mm | 5.2 M | 1.098 | 49.37 | **49.37** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 47.0 mm | 5.2 M | 1.055 | 45.64 | **45.64** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 54.2 mm | 5.2 M | 1.503 | 31.78 | **31.78** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 104.6 mm | 5.2 M | 1.339 | 54.96 | **54.96** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 55.4 mm | 5.2 M | 0.767 | 70.79 | **70.79** | `VERY_HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 54.2 mm | 5.2 M | 1.503 | 43.13 | **43.13** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 62.6 mm | 5.2 M | 0.875 | 71.33 | **71.33** | `VERY_HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 78.2 mm | 5.2 M | 1.263 | 39.99 | **39.99** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 56.6 mm | 5.2 M | 1.181 | 48.7 | **48.7** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 71.0 mm | 5.2 M | 2.038 | 47.48 | **47.48** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 67.4 mm | 5.2 M | 1.01 | 42.41 | **42.41** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 62.6 mm | 5.2 M | 1.476 | 48.05 | **48.05** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 86.6 mm | 5.2 M | 1.24 | 55.1 | **55.1** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 98.6 mm | 5.2 M | 1.359 | 40.07 | **40.07** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 103.4 mm | 5.2 M | 0.931 | 54.45 | **54.45** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 83.0 mm | 5.2 M | 1.975 | 35.85 | **35.85** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 49.4 mm | 5.2 M | 1.519 | 40.31 | **40.31** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
