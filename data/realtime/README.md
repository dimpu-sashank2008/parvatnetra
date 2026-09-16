# Real-Time Multimodal CRI Dataset Directory
`data/realtime/`

**Generated At:** 2026-09-16T08:32:15.105722+00:00  
**Sectors Covered:** 20 corridors across 8 North-Eastern states  
**Dataset SHA-256:** `b119118ecd7153716964c038ba87643418186ab1799b6eb743df441d4b235c22`  

### Available Files:
1. `realtime_cri_dataset.csv`: Standardized tabular dataset with 50+ real-time telemetry, geotechnical, and risk attributes.
2. `realtime_cri_dataset.json`: Structured JSON document containing metadata and sector records.

### Provenance Classification:
- `[LIVE]`: Direct API stream from Open-Meteo Global Forecasting or USGS Real-time Earthquake API.
- `[IN-SITU]`: Direct telemetry from in-situ piezometers, inclinometers, and CWC hydrometric river radar.
- `[HISTORICAL]`: Copernicus GLO-30 / CartoDEM 30m terrain elevations, slopes, and GSI NLSM susceptibility.
- `[HYBRID]`: Multimodal fusion combining live weather and seismic data with physical terrain parameters.
