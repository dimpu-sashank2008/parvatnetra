# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-13T11:55:48.853611+00:00  
**Dataset SHA-256:** `6298e9d08451be7d023d1bbfbd434b689b16e10e0e6ff9b98c02834d67a85cd3`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 21.74 / 100
- **Average Mohr-Coulomb FoS:** 1.496
- **Peak 24h Rainfall Recorded:** 61.9 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 2
  - `MODERATE`: 5
  - `LOW`: 13

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 12.3 mm | 4.2 M | 0.981 | 35.18 | **35.18** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 61.9 mm | 4.2 M | 1.737 | 39.34 | **39.34** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 12.3 mm | 4.2 M | 2.336 | 10.71 | **10.71** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 52.3 mm | 4.2 M | 1.193 | 28.63 | **28.63** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 4.3 mm | 4.2 M | 1.126 | 21.41 | **21.41** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 4.4 mm | 4.2 M | 1.631 | 10.67 | **10.67** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 11.0 mm | 4.2 M | 1.631 | 17.71 | **17.71** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 16.3 mm | 4.2 M | 0.822 | 49.53 | **49.53** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 21.7 mm | 4.2 M | 1.609 | 24.04 | **24.04** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 5.9 mm | 4.2 M | 0.955 | 43.11 | **43.11** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 11.1 mm | 4.2 M | 1.433 | 14.48 | **14.48** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 2.3 mm | 4.2 M | 1.292 | 18.81 | **18.81** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 16.8 mm | 4.2 M | 2.326 | 16.24 | **16.24** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 1.7 mm | 4.2 M | 1.126 | 14.83 | **14.83** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 3.6 mm | 4.2 M | 1.631 | 14.3 | **14.3** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 3.7 mm | 4.2 M | 1.433 | 16.23 | **16.23** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 18.0 mm | 4.2 M | 1.621 | 14.68 | **14.68** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 4.3 mm | 4.2 M | 1.126 | 15.69 | **15.69** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 24.7 mm | 4.2 M | 2.284 | 15.23 | **15.23** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 2.8 mm | 4.2 M | 1.631 | 13.89 | **13.89** | `LOW` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
