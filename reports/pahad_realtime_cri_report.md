# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-22T12:26:59.543999+00:00  
**Dataset SHA-256:** `5b288cb2aa227716a7875ccdb11ca2c7ea233c10bfe47f0f28257f089d2c7342`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 14.98 / 100
- **Average Mohr-Coulomb FoS:** 3.277
- **Peak 24h Rainfall Recorded:** 42.2 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 0
  - `MODERATE`: 4
  - `LOW`: 16

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 14.0 mm | 5.2 M | 0.964 | 38.41 | **38.41** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 18.4 mm | 5.2 M | 2.643 | 34.53 | **34.53** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 14.0 mm | 5.2 M | 4.943 | 16.46 | **16.46** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 23.2 mm | 5.2 M | 2.912 | 19.77 | **19.77** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 10.7 mm | 5.2 M | 3.031 | 12.98 | **12.98** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 9.5 mm | 5.2 M | 4.116 | 8.12 | **8.12** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 24.2 mm | 5.2 M | 3.509 | 15.71 | **15.71** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 2.9 mm | 5.2 M | 1.919 | 11.33 | **11.33** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 9.2 mm | 5.2 M | 2.337 | 12.52 | **12.52** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 42.2 mm | 5.2 M | 2.675 | 25.17 | **25.17** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 0.5 mm | 5.2 M | 2.694 | 6.1 | **6.1** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 0.0 mm | 5.2 M | 3.288 | 7.0 | **7.0** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 3.3 mm | 5.2 M | 5.653 | 5.43 | **5.43** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 0.5 mm | 5.2 M | 0.804 | 32.77 | **32.77** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 1.3 mm | 5.2 M | 4.367 | 5.25 | **5.25** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 30.2 mm | 5.2 M | 3.746 | 18.55 | **18.55** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 3.4 mm | 5.2 M | 2.93 | 6.37 | **6.37** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 7.5 mm | 5.2 M | 2.906 | 8.23 | **8.23** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 9.9 mm | 5.2 M | 6.069 | 6.37 | **6.37** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 7.1 mm | 5.2 M | 4.025 | 8.51 | **8.51** | `LOW` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
