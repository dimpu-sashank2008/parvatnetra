# Real-Time Multimodal CRI Dataset Directory
`data/realtime/`

**Generated At:** 2026-09-17T07:53:20.142922+00:00  
**Sectors Covered:** 20 corridors across 8 North-Eastern states  
**Dataset SHA-256:** `6f95890bb76d8b771db3e8ec969be7f6e56c8e99bf861100a15d43faaf66fbfa`  

### Available Files:
1. `realtime_cri_dataset.csv`: Standardized tabular dataset with 50+ real-time telemetry, geotechnical, and risk attributes.
2. `realtime_cri_dataset.json`: Structured JSON document containing metadata and sector records.

### Provenance Classification:
- `[LIVE]`: Direct API stream from Open-Meteo Global Forecasting or USGS Real-time Earthquake API.
- `[IN-SITU]`: Direct telemetry from in-situ piezometers, inclinometers, and CWC hydrometric river radar.
- `[HISTORICAL]`: Copernicus GLO-30 / CartoDEM 30m terrain elevations, slopes, and GSI NLSM susceptibility.
- `[HYBRID]`: Multimodal fusion combining live weather and seismic data with physical terrain parameters.
