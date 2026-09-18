# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-18T14:57:52.618699+00:00  
**Dataset SHA-256:** `f31a9ed1d348dc2b27d3ba52fd24c8724215e0ce22ca77d1381683dba2f06b86`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 12.55 / 100
- **Average Mohr-Coulomb FoS:** 3.272
- **Peak 24h Rainfall Recorded:** 63.3 mm
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
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 20.9 mm | 3.7 M | 0.953 | 37.65 | **37.65** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 32.7 mm | 3.7 M | 2.56 | 25.93 | **25.93** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 20.9 mm | 3.7 M | 4.866 | 8.66 | **8.66** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 63.3 mm | 3.7 M | 2.643 | 26.16 | **26.16** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 1.9 mm | 3.7 M | 3.031 | 8.24 | **8.24** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 1.5 mm | 3.7 M | 4.116 | 4.51 | **4.51** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 0.8 mm | 3.7 M | 3.583 | 6.69 | **6.69** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 6.3 mm | 3.7 M | 1.919 | 13.46 | **13.46** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 4.8 mm | 3.7 M | 2.337 | 11.33 | **11.33** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 5.6 mm | 3.7 M | 2.818 | 10.5 | **10.5** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 3.5 mm | 3.7 M | 2.694 | 9.23 | **9.23** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 1.8 mm | 3.7 M | 3.288 | 7.92 | **7.92** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 6.7 mm | 3.7 M | 5.653 | 8.78 | **8.78** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 0.0 mm | 3.7 M | 0.804 | 32.61 | **32.61** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 1.9 mm | 3.7 M | 4.367 | 6.02 | **6.02** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 1.2 mm | 3.7 M | 3.885 | 6.34 | **6.34** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 2.6 mm | 3.7 M | 2.93 | 6.44 | **6.44** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 1.1 mm | 3.7 M | 2.906 | 6.38 | **6.38** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 13.6 mm | 3.7 M | 6.069 | 8.1 | **8.1** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 0.4 mm | 3.7 M | 4.025 | 6.0 | **6.0** | `LOW` | 0/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
