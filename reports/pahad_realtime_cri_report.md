# PARVAT NETRA • REAL-TIME MULTIMODAL CRI DATASET REPORT
**Evaluation Engine:** PAHAD AI Multimodal Fusion Engine v3.1  
**Generated UTC:** 2026-09-22T12:48:04.265655+00:00  
**Dataset SHA-256:** `4895c09519a75c933d8271af3d91a986c90ed12f7e7a2b2d8fedac8cfb853c2e`  
**Filed Files:** `data/realtime/realtime_cri_dataset.csv`, `data/realtime/realtime_cri_dataset.json`  

---

## 1. Executive Summary
This dataset files live multi-modal sensor and meteorological observations across all 20 GSI critical monitoring corridors in the 8 North-Eastern Region (NER) states:
- **Total Sectors Evaluated:** 20
- **Average Sector CRI:** 12.98 / 100
- **Average Mohr-Coulomb FoS:** 3.294
- **Peak 24h Rainfall Recorded:** 27.4 mm
- **Alert Band Distribution:**
  - `EXTREME`: 0
  - `VERY_HIGH`: 0
  - `HIGH`: 0
  - `MODERATE`: 3
  - `LOW`: 17

---

## 2. Sector Risk & Telemetry Registry

| Sector ID | Corridor | State | 24h Rain | Seismic Mag | FoS | Raw CRI | Final CRI | Alert Band | Agreement | Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SK-NH10-KM48` | National Highway 10 | Sikkim | 9.5 mm | 5.2 M | 0.964 | 35.27 | **35.27** | `MODERATE` | 2/3 | `[LIVE/HYBRID]` |
| `SK-SINGTAM-01` | NH-10 / Teesta River Gorge | Sikkim | 8.5 mm | 5.2 M | 2.663 | 25.09 | **25.09** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `SK-DIKCHU-01` | North Sikkim Highway | Sikkim | 9.5 mm | 5.2 M | 4.943 | 13.33 | **13.33** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `SK-MANGAN-01` | Mangan-Chungthang Road | Sikkim | 17.1 mm | 5.2 M | 2.953 | 17.64 | **17.64** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-HUNTHAR-01` | NH-06 / Western Arterial | Mizoram | 7.6 mm | 5.2 M | 3.031 | 10.75 | **10.75** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-SAIRANG-01` | Bairabi-Sairang Rail Spur | Mizoram | 6.8 mm | 5.2 M | 4.116 | 6.28 | **6.28** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MZ-KOLASIB-01` | NH-306 Silchar-Aizawl Link | Mizoram | 13.2 mm | 5.2 M | 3.583 | 12.55 | **12.55** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PAGALA-01` | NH-29 Dimapur-Kohima Lifeline | Nagaland | 2.5 mm | 5.2 M | 1.919 | 11.14 | **11.14** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-DZUDZA-01` | NH-29 Km 15 | Nagaland | 8.9 mm | 5.2 M | 2.337 | 12.34 | **12.34** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `NL-PIPHEMA-01` | NH-29 | Nagaland | 27.4 mm | 5.2 M | 2.753 | 18.58 | **18.58** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-BHALUK-01` | Tawang Strategic Highway | Arunachal Pradesh | 2.1 mm | 5.2 M | 2.694 | 6.63 | **6.63** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AR-PASIGHAT-01` | NH-515 / Siang Valley | Arunachal Pradesh | 0.1 mm | 5.2 M | 3.288 | 7.0 | **7.0** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `AR-SELA-01` | NH-13 | Arunachal Pradesh | 2.8 mm | 5.2 M | 5.653 | 5.24 | **5.24** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `MN-TUPUL-01` | Jiribam-Imphal Railway | Manipur | 0.7 mm | 5.2 M | 0.804 | 32.84 | **32.84** | `MODERATE` | 1/3 | `[LIVE/HYBRID]` |
| `MN-JIRIBAM-01` | NH-37 Lifeline | Manipur | 0.0 mm | 5.2 M | 4.367 | 4.68 | **4.68** | `LOW` | 0/3 | `[LIVE/HYBRID]` |
| `ML-SONAPUR-01` | NH-06 Barak Valley Lifeline | Meghalaya | 11.3 mm | 5.2 M | 3.885 | 10.7 | **10.7** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `ML-CHERRA-01` | Sohra-Shella Corridor | Meghalaya | 2.5 mm | 5.2 M | 2.93 | 6.06 | **6.06** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-DIMA-01` | Lumding-Badarpur Hill Section | Assam | 6.8 mm | 5.2 M | 2.906 | 8.03 | **8.03** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `AS-GUWAHATI-01` | Guwahati Urban Rim | Assam | 11.9 mm | 5.2 M | 6.069 | 6.99 | **6.99** | `LOW` | 1/3 | `[LIVE/HYBRID]` |
| `TR-BARAMURA-01` | NH-08 National Corridor | Tripura | 6.2 mm | 5.2 M | 4.025 | 8.47 | **8.47** | `LOW` | 1/3 | `[LIVE/HYBRID]` |

---

## 3. Methodological Invariants
1. **Scientific Decoupling**: Geotechnical Factor of Safety ($FoS$) and Composite Risk Index ($CRI$) are computed as separate physical and multi-modal risk indices.
2. **False Alarm Suppression (2-of-3 Rule)**: Escalation to `EXTREME` alert requires independent agreement between physical stability ($FoS \le 1.0$), empirical rainfall threshold breach, and ML event probability ($>0.80$).
3. **Data Integrity & Traceability**: Each record carries an immutable SHA-256 data hash allowing verification of ground truth without synthetic fabrication.
