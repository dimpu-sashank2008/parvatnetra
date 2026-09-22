# PARVAT NETRA • PAHAD AI — PHASE V5.3
# DUAL 2D/3D MAP STACK TECHNICAL & RENDERING REPORT

**Document ID**: `PN-DOC-V5_3-002`  
**Classification**: GIS Stack & Client Rendering Report  
**Version**: `5.3.0`  
**Date**: `2026-09-21`  

---

## 1. Map Engine Dual Stack Architecture

PARVAT NETRA maintains a resilient dual-engine architecture:
- **2D Engine (Leaflet 1.9.4)**: Ultra-fast, responsive operational triage and low-bandwidth fallback with zero WebGL prerequisites.
- **3D Engine (CesiumJS 1.119)**: Photorealistic, cinematic God's Eye 3D presentation layer loaded strictly on demand.

---

## 2. Basemap Switcher Options & Specifications

| Basemap Option | Engine | Source | Resolution / Coverage | Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Dark** | Leaflet 2D | CartoDB Dark Matter | Global $(z=0\text{ to }19)$ | Online & Offline Vector |
| **Terrain** | Leaflet 2D | Google Maps Terrain / Stamen | Topographic contours | Online |
| **Street** | Leaflet 2D | CartoDB Voyager / OSM | Highway & urban grid | Online |
| **Satellite** | Leaflet 2D | Esri World Imagery | High-resolution optical | Online |
| **Topo** | Leaflet 2D | OpenTopoMap | Elevation lines & relief | Online |
| **ISRO Bhuvan** | Leaflet 2D | NRSC Resourcesat-2 | Indian sovereign imagery | Online |
| **God's Eye 3D** | CesiumJS 3D | Open Terrain / Google 3D Tiles | Photorealistic 3D Globe | Online WebGL |

---

## 3. DOM & Event Management

1. **Z-Index Layering**:
   - Leaflet Map (`#map`): `z-[1]`
   - Cesium 3D Container (`#gods-eye-3d-container`): `z-[300]`
   - 3D HUD & Controls (`.gods-eye-hud`): `z-[320]`
   - Layer Control Panel (`#layer-control-panel`): `z-[400]`
   - Data Status Panel (`#gis-data-status-panel`): `z-[400]`
2. **Context Retention**:
   Switching between 2D and 3D preserves all active alert selections, incident queues, and corridor filters without page reloading or remounting DOM elements.
