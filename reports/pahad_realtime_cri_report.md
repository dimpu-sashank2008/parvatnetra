# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-19T17:18:32.481684+00:00  
**Dataset SHA-256:** `bc3ce881feba83b8c89fbbc3fae6a00deac38ff83e8c0b0c26197dfe17d7be9f`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 44.32 / 100
- **Average Mohr-Coulomb FoS:** 2.759
- **Peak 24h Rainfall Recorded:** 135.0 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 14
  - `MODERATE`: 6
  - `LOW`: 0

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 135.0 mm | 5.2 M | 0.75 | 57.7 | **57.7** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 68.2 mm | 5.2 M | 2.355 | 58.83 | **58.83** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 87.4 mm | 5.2 M | 4.005 | 39.82 | **39.82** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 100.6 mm | 5.2 M | 2.393 | 43.35 | **43.35** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 59.8 mm | 5.2 M | 2.724 | 41.01 | **41.01** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 67.0 mm | 5.2 M | 3.624 | 31.91 | **31.91** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 117.4 mm | 5.2 M | 2.757 | 49.76 | **49.76** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 68.2 mm | 5.2 M | 1.73 | 48.69 | **48.69** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 67.0 mm | 5.2 M | 2.11 | 46.23 | **46.23** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 75.4 mm | 5.2 M | 2.5 | 46.36 | **46.36** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 91.0 mm | 5.2 M | 2.243 | 36.15 | **36.15** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 69.4 mm | 5.2 M | 2.882 | 45.54 | **45.54** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 83.8 mm | 5.2 M | 4.626 | 44.19 | **44.19** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 80.2 mm | 5.2 M | 0.716 | 57.11 | **57.11** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 75.4 mm | 5.2 M | 3.743 | 44.16 | **44.16** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 99.4 mm | 5.2 M | 3.114 | 47.08 | **47.08** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 111.4 mm | 5.2 M | 2.307 | 36.82 | **36.82** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 116.2 mm | 5.2 M | 2.242 | 37.58 | **37.58** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 95.8 mm | 5.2 M | 4.769 | 33.43 | **33.43** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 62.2 mm | 5.2 M | 3.596 | 40.72 | **40.72** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
