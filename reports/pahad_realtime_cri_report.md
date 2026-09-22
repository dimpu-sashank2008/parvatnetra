# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-22T09:06:32.434033+00:00  
**Dataset SHA-256:** `a106668176bed0d565ebca362f95f1fc03bd96771e3d233bc9c45e8b84975b54`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 37.01 / 100
- **Average Mohr-Coulomb FoS:** 2.904
- **Peak 24h Rainfall Recorded:** 111.0 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 9
  - `MODERATE`: 9
  - `LOW`: 2

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 14.0 mm | 5.2 M | 0.964 | 35.96 | **35.96** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 61.8 mm | 5.2 M | 2.392 | 55.21 | **55.21** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 81.0 mm | 5.2 M | 4.088 | 39.36 | **39.36** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 94.2 mm | 5.2 M | 2.436 | 42.89 | **42.89** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 53.4 mm | 5.2 M | 2.767 | 37.27 | **37.27** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 60.6 mm | 5.2 M | 3.685 | 29.17 | **29.17** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 111.0 mm | 5.2 M | 2.809 | 49.13 | **49.13** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 61.8 mm | 5.2 M | 1.753 | 44.94 | **44.94** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 60.6 mm | 5.2 M | 2.138 | 42.51 | **42.51** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 69.0 mm | 5.2 M | 2.534 | 45.73 | **45.73** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 84.6 mm | 5.2 M | 2.281 | 35.69 | **35.69** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 63.0 mm | 5.2 M | 2.93 | 42.3 | **42.3** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 77.4 mm | 5.2 M | 4.721 | 43.55 | **43.55** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 73.8 mm | 5.2 M | 0.724 | 57.11 | **57.11** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 1.3 mm | 5.2 M | 4.367 | 5.25 | **5.25** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 30.2 mm | 5.2 M | 3.746 | 20.65 | **20.65** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 3.4 mm | 5.2 M | 2.93 | 6.37 | **6.37** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 109.8 mm | 5.2 M | 2.284 | 37.12 | **37.12** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 89.4 mm | 5.2 M | 4.872 | 32.96 | **32.96** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 55.8 mm | 5.2 M | 3.654 | 36.96 | **36.96** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
