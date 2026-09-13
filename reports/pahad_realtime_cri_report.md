# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-13T12:06:37.586959+00:00  
**Dataset SHA-256:** `89697a6d4cf14fd74ac7c3d5893bd938b45a62dd98a1b9d27bb1801a1c1f9e16`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 47.36 / 100
- **Average Mohr-Coulomb FoS:** 1.337
- **Peak 24h Rainfall Recorded:** 135.0 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 2
  - `HIGH`: 14
  - `MODERATE`: 2
  - `LOW`: 2

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 135.0 mm | 5.2 M | 0.767 | 55.83 | **55.83** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 63.4 mm | 5.2 M | 1.73 | 56.6 | **56.6** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 82.6 mm | 5.2 M | 1.977 | 42.83 | **42.83** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 95.8 mm | 5.2 M | 1.077 | 49.95 | **49.95** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 55.0 mm | 5.2 M | 1.038 | 50.33 | **50.33** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 62.2 mm | 5.2 M | 1.477 | 35.24 | **35.24** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 11.0 mm | 5.2 M | 1.631 | 17.71 | **17.71** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 63.4 mm | 5.2 M | 0.756 | 74.67 | **74.67** | `VERY_HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 62.2 mm | 5.2 M | 1.477 | 47.82 | **47.82** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 70.6 mm | 5.2 M | 0.861 | 74.12 | **74.12** | `VERY_HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 86.2 mm | 5.2 M | 1.241 | 40.57 | **40.57** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 64.6 mm | 5.2 M | 1.16 | 53.39 | **53.39** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 79.0 mm | 5.2 M | 1.996 | 48.27 | **48.27** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 75.4 mm | 5.2 M | 0.993 | 54.45 | **54.45** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 70.6 mm | 5.2 M | 1.45 | 51.63 | **51.63** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 94.6 mm | 5.2 M | 1.218 | 55.89 | **55.89** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 107.4 mm | 5.2 M | 1.33 | 40.7 | **40.7** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 4.3 mm | 5.2 M | 1.126 | 15.69 | **15.69** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 91.0 mm | 5.2 M | 1.932 | 36.43 | **36.43** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 57.4 mm | 5.2 M | 1.493 | 45.0 | **45.0** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
