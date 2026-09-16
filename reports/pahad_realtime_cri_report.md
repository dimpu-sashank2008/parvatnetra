# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-16T08:36:18.988673+00:00  
**Dataset SHA-256:** `e39592794ff9caba681da8ca3b7589b22bbb4eca12f9537ef61af3c4f61b08df`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 23.85 / 100
- **Average Mohr-Coulomb FoS:** 1.477
- **Peak 24h Rainfall Recorded:** 145.2 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 4
  - `MODERATE`: 6
  - `LOW`: 10

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 55.1 mm | 4.2 M | 0.909 | 46.25 | **46.25** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 32.7 mm | 4.2 M | 1.861 | 24.65 | **24.65** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 55.1 mm | 4.2 M | 2.123 | 24.33 | **24.33** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 145.2 mm | 4.2 M | 0.946 | 52.57 | **52.57** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 11.3 mm | 4.2 M | 1.126 | 23.54 | **23.54** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 13.6 mm | 4.2 M | 1.631 | 12.99 | **12.99** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 26.5 mm | 4.2 M | 1.593 | 23.13 | **23.13** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 3.3 mm | 4.2 M | 0.824 | 45.21 | **45.21** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 11.9 mm | 4.2 M | 1.631 | 17.98 | **17.98** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 13.0 mm | 4.2 M | 0.955 | 46.69 | **46.69** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 19.1 mm | 4.2 M | 1.422 | 17.84 | **17.84** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 5.9 mm | 4.2 M | 1.292 | 21.15 | **21.15** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 0.8 mm | 4.2 M | 2.336 | 8.78 | **8.78** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 8.4 mm | 4.2 M | 1.126 | 16.7 | **16.7** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 15.0 mm | 4.2 M | 1.631 | 18.19 | **18.19** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 27.2 mm | 4.2 M | 1.401 | 25.15 | **25.15** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 1.7 mm | 4.2 M | 1.631 | 9.92 | **9.92** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 2.2 mm | 4.2 M | 1.126 | 14.96 | **14.96** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 8.5 mm | 4.2 M | 2.336 | 8.71 | **8.71** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 11.9 mm | 4.2 M | 1.631 | 18.21 | **18.21** | `LOW` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
