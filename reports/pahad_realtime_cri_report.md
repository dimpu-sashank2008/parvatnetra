# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-16T08:32:15.105722+00:00  
**Dataset SHA-256:** `b119118ecd7153716964c038ba87643418186ab1799b6eb743df441d4b235c22`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 40.76 / 100
- **Average Mohr-Coulomb FoS:** 1.374
- **Peak 24h Rainfall Recorded:** 110.2 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 1
  - `HIGH`: 12
  - `MODERATE`: 3
  - `LOW`: 4

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 55.1 mm | 5.2 M | 0.909 | 46.25 | **46.25** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 61.0 mm | 5.2 M | 1.741 | 55.21 | **55.21** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 80.2 mm | 5.2 M | 1.99 | 42.65 | **42.65** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 93.4 mm | 5.2 M | 1.083 | 49.77 | **49.77** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 52.6 mm | 5.2 M | 1.043 | 48.91 | **48.91** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 59.8 mm | 5.2 M | 1.485 | 34.19 | **34.19** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 110.2 mm | 5.2 M | 1.321 | 55.52 | **55.52** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 61.0 mm | 5.2 M | 0.759 | 73.51 | **73.51** | `VERY_HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 11.9 mm | 5.2 M | 1.631 | 17.22 | **17.22** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 13.0 mm | 5.2 M | 0.955 | 46.69 | **46.69** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 19.1 mm | 5.2 M | 1.422 | 17.84 | **17.84** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 5.9 mm | 5.2 M | 1.292 | 20.27 | **20.27** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 0.8 mm | 5.2 M | 2.336 | 8.78 | **8.78** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 8.4 mm | 5.2 M | 1.126 | 16.7 | **16.7** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 68.2 mm | 5.2 M | 1.458 | 51.31 | **51.31** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 92.2 mm | 5.2 M | 1.225 | 55.64 | **55.64** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 104.2 mm | 5.2 M | 1.341 | 40.47 | **40.47** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 109.0 mm | 5.2 M | 0.918 | 54.45 | **54.45** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 88.6 mm | 5.2 M | 1.945 | 36.26 | **36.26** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 55.0 mm | 5.2 M | 1.501 | 43.61 | **43.61** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
