# Real-Time Multimodal CRI Dataset Directory
`data/realtime/`

**Generated At:** 2026-09-16T08:36:18.988673+00:00  
**Sectors Covered:** 20 corridors across 8 North-Eastern states  
**Dataset SHA-256:** `e39592794ff9caba681da8ca3b7589b22bbb4eca12f9537ef61af3c4f61b08df`  

### Available Files:
1. `realtime_cri_dataset.csv`: Standardized tabular dataset with 50+ real-time telemetry, geotechnical, and risk attributes.
2. `realtime_cri_dataset.json`: Structured JSON document containing metadata and sector records.

### Provenance Classification:
- `[LIVE]`: Direct API stream from Open-Meteo Global Forecasting or USGS Real-time Earthquake API.
- `[IN-SITU]`: Direct telemetry from in-situ piezometers, inclinometers, and CWC hydrometric river radar.
- `[HISTORICAL]`: Copernicus GLO-30 / CartoDEM 30m terrain elevations, slopes, and GSI NLSM susceptibility.
- `[HYBRID]`: Multimodal fusion combining live weather and seismic data with physical terrain parameters.
