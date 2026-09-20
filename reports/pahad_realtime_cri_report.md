# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-20T08:37:51.527077+00:00  
**Dataset SHA-256:** `f45b890b5a52154770ff697aea5202be3362db84458dcd17ff5231898420bc6b`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 42.6 / 100
- **Average Mohr-Coulomb FoS:** 2.813
- **Peak 24h Rainfall Recorded:** 135.0 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 12
  - `MODERATE`: 8
  - `LOW`: 0

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 135.0 mm | 5.2 M | 0.75 | 57.7 | **57.7** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 61.0 mm | 5.2 M | 2.397 | 54.77 | **54.77** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 80.2 mm | 5.2 M | 4.098 | 39.29 | **39.29** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 93.4 mm | 5.2 M | 2.441 | 42.82 | **42.82** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 52.6 mm | 5.2 M | 2.773 | 36.79 | **36.79** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 59.8 mm | 5.2 M | 3.692 | 28.81 | **28.81** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 110.2 mm | 5.2 M | 2.816 | 49.06 | **49.06** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 61.0 mm | 5.2 M | 1.756 | 44.49 | **44.49** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 59.8 mm | 5.2 M | 2.142 | 42.03 | **42.03** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 68.2 mm | 5.2 M | 2.538 | 45.58 | **45.58** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 83.8 mm | 5.2 M | 2.285 | 35.64 | **35.64** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 62.2 mm | 5.2 M | 2.936 | 41.86 | **41.86** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 76.6 mm | 5.2 M | 4.734 | 43.47 | **43.47** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 73.0 mm | 5.2 M | 0.725 | 57.11 | **57.11** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 68.2 mm | 5.2 M | 3.818 | 43.37 | **43.37** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 92.2 mm | 5.2 M | 3.18 | 46.37 | **46.37** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 104.2 mm | 5.2 M | 2.353 | 36.3 | **36.3** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 109.0 mm | 5.2 M | 2.289 | 37.07 | **37.07** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 88.6 mm | 5.2 M | 4.885 | 32.9 | **32.9** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 55.0 mm | 5.2 M | 3.661 | 36.5 | **36.5** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
