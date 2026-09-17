# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-17T10:05:48.505889+00:00  
**Dataset SHA-256:** `16a6d02369fabf60f30a30446ef7ded195a96443536ab0ce021cbe4526b72dd2`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 22.65 / 100
- **Average Mohr-Coulomb FoS:** 1.496
- **Peak 24h Rainfall Recorded:** 52.1 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 3
  - `MODERATE`: 6
  - `LOW`: 11

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 19.4 mm | 4.2 M | 0.973 | 36.08 | **36.08** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 50.0 mm | 4.2 M | 1.788 | 33.18 | **33.18** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 19.4 mm | 4.2 M | 2.312 | 11.98 | **11.98** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 52.1 mm | 4.2 M | 1.193 | 28.68 | **28.68** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 7.1 mm | 4.2 M | 1.126 | 22.1 | **22.1** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 3.7 mm | 4.2 M | 1.631 | 10.6 | **10.6** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 16.6 mm | 4.2 M | 1.626 | 18.97 | **18.97** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 5.5 mm | 4.2 M | 0.824 | 46.22 | **46.22** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 16.6 mm | 4.2 M | 1.626 | 20.31 | **20.31** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 14.1 mm | 4.2 M | 0.955 | 45.83 | **45.83** | `HIGH` | 2/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 15.4 mm | 4.2 M | 1.432 | 15.02 | **15.02** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 47.3 mm | 4.2 M | 1.206 | 41.83 | **41.83** | `HIGH` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 1.0 mm | 4.2 M | 2.336 | 8.99 | **8.99** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 14.0 mm | 4.2 M | 1.126 | 17.98 | **17.98** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 17.4 mm | 4.2 M | 1.623 | 19.11 | **19.11** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 20.9 mm | 4.2 M | 1.417 | 22.98 | **22.98** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 4.5 mm | 4.2 M | 1.631 | 10.82 | **10.82** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 1.4 mm | 4.2 M | 1.126 | 14.7 | **14.7** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 16.1 mm | 4.2 M | 2.33 | 10.99 | **10.99** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 9.7 mm | 4.2 M | 1.631 | 16.59 | **16.59** | `LOW` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
