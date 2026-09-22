# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-22T08:52:30.110599+00:00  
**Dataset SHA-256:** `a4bceed89dcaa585da597ea731f861934d10461aae0186a4d82ff8f38e64c071`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 33.95 / 100
- **Average Mohr-Coulomb FoS:** 2.975
- **Peak 24h Rainfall Recorded:** 109.4 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 10
  - `MODERATE`: 5
  - `LOW`: 5

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 21.6 mm | 3.7 M | 0.952 | 39.46 | **39.46** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 58.6 mm | 3.7 M | 2.411 | 43.93 | **43.93** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 77.8 mm | 3.7 M | 4.13 | 32.12 | **32.12** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 20.9 mm | 3.7 M | 2.928 | 13.47 | **13.47** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 11.1 mm | 3.7 M | 3.031 | 12.49 | **12.49** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 59.0 mm | 3.7 M | 3.7 | 28.47 | **28.47** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 109.4 mm | 3.7 M | 2.822 | 48.97 | **48.97** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 60.2 mm | 3.7 M | 1.759 | 44.61 | **44.61** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 59.0 mm | 3.7 M | 2.145 | 42.18 | **42.18** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 67.4 mm | 3.7 M | 2.542 | 45.74 | **45.74** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 83.0 mm | 3.7 M | 2.29 | 37.74 | **37.74** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 61.4 mm | 3.7 M | 2.942 | 41.86 | **41.86** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 75.8 mm | 3.7 M | 4.746 | 45.7 | **45.7** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 72.2 mm | 3.7 M | 0.727 | 57.11 | **57.11** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 67.4 mm | 3.7 M | 3.826 | 43.39 | **43.39** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 91.4 mm | 3.7 M | 3.187 | 46.89 | **46.89** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 103.4 mm | 3.7 M | 2.358 | 36.69 | **36.69** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 3.8 mm | 3.7 M | 2.906 | 7.44 | **7.44** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 2.4 mm | 3.7 M | 6.069 | 4.41 | **4.41** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 1.2 mm | 3.7 M | 4.025 | 6.27 | **6.27** | `LOW` | 0/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
