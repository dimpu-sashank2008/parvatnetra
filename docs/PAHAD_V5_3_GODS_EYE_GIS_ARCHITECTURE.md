# PARVAT NETRA • PAHAD AI — PHASE V5.3
# GOD'S EYE STYLE 3D GIS ARCHITECTURE & GEOSPATIAL PRESENTATION SPECIFICATION

**Document ID**: `PN-DOC-V5_3-001`  
**Classification**: Engineering Architecture Specification  
**Version**: `5.3.0`  
**Status**: APPROVED & IMPLEMENTED  
**Date**: `2026-09-21`  
**Corridor Focus**: `CORR-NH10-SIKKIM-KM48` (`27.3300°N, 88.6100°E`)

---

## 1. Executive Architectural Summary

Phase V5.3 delivers a cinematic, photorealistic 3D geospatial experience ("God's Eye 3D") directly into the existing PARVAT NETRA operational GIS map container (`#gis-map`).

### Key Invariants Maintained
1. **NOT a New Application / NOT a Separate Page**: The 3D engine operates as an additive basemap mode alongside existing 2D basemaps (`Dark`, `Terrain`, `Street`, `Satellite`, `Topo`, `ISRO Bhuvan`).
2. **Separation of Concerns**:
   - **God's Eye 3D**: Strictly a visualization and 3D geospatial presentation layer.
   - **PAHAD AI**: The sole authoritative source of geotechnical risk calculations, physical Factor of Safety ($FoS$), Composite Risk Index (CRI), and early-warning decision intelligence.
3. **Lazy-Loading Paradigm**: Zero bytes of 3D runtime code or shaders are downloaded until the user explicitly selects `God's Eye 3D` in the Map Style panel.
4. **Truthful Provider Fallback**: In the absence of proprietary Google 3D Tiles or Cesium Ion credentials, the system truthfully displays `[3D PROVIDER: TERRAIN 3D FALLBACK (AUTH_REQUIRED FOR GOOGLE 3D TILES)]` over high-resolution elevation ellipsoid terrain.

---

## 2. Container Hierarchy & Layout Topology

```
+--------------------------------------------------------------------------------+
| #gis-map (relative flex-grow container, overflow-hidden)                       |
|                                                                                |
|  +-------------------------------------+  +---------------------------------+  |
|  | #map (Leaflet 2D Container)         |  | #gods-eye-3d-container (3D)     |  |
|  | - WGS84 2D Web Mercator             |  | - WebGL 3D Globe Canvas         |  |
|  | - Display: block (in 2D mode)       |  | - Display: none (default)       |  |
|  | - Display: none (in 3D mode)        |  | - Display: block (in 3D mode)   |  |
|  +-------------------------------------+  +---------------------------------+  |
|                                                                                |
|  +--------------------------------------------------------------------------+  |
|  | Floating GIS Overlays (z-[400], persistent across both 2D and 3D modes):  |  |
|  |  1. #layer-control-panel (Map Style Switcher & Feature Toggles)          |  |
|  |  2. #gis-data-status-panel (Compact Multi-Source Provenance Feed)        |  |
|  |  3. .gods-eye-hud (3D Flight Breadcrumb, Orbit, Focus KM48, Legend)     |  |
|  +--------------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------+
```

---

## 3. 2D $\leftrightarrow$ 3D Transition Lifecycle

When transitioning between 2D Leaflet and 3D Cesium:
1. **Activation (`GodsEye3D.activate()`)**:
   - Captures current viewport center and zoom from Leaflet.
   - Hides `#map` (`style.display = 'none'`).
   - Displays `#gods-eye-3d-container` (`style.display = 'block'`).
   - Dynamically loads CesiumJS script and widgets CSS if not already present.
   - Re-enables Cesium render loop (`viewer.useDefaultRenderLoop = true`).
   - Initiates hierarchical camera flight sequence to KM48.
2. **Deactivation (`GodsEye3D.deactivate()`)**:
   - Stops 360-degree orbit if active.
   - Hides `#gods-eye-3d-container` (`style.display = 'none'`).
   - Displays `#map` (`style.display = 'block'`).
   - Pauses Cesium render loop (`viewer.useDefaultRenderLoop = false`) to free GPU/CPU cycles.
   - Dispatches `window.map.invalidateSize()` immediately and at $t+150\text{ ms}$ to guarantee zero tile displacement.

---

## 4. Operational Corridors & Camera Hierarchy

| Hierarchy Level | Geographic Scope | Target Coordinates | Altitude ($m$) | Pitch | Heading |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Level 1** | India National Overview | $78.9629^\circ\text{E}, 20.5937^\circ\text{N}$ | $4,500,000$ | $-90^\circ$ | $0^\circ$ |
| **Level 2** | North-East Region (NER) | $92.5000^\circ\text{E}, 26.0000^\circ\text{N}$ | $1,200,000$ | $-75^\circ$ | $10^\circ$ |
| **Level 3** | Sikkim Himalayas | $88.5000^\circ\text{E}, 27.5000^\circ\text{N}$ | $250,000$ | $-60^\circ$ | $25^\circ$ |
| **Level 4** | Teesta Gorge / NH-10 | $88.6100^\circ\text{E}, 27.3300^\circ\text{N}$ | $25,000$ | $-45^\circ$ | $35^\circ$ |
| **Level 5** | KM48 Hazard Escarpment | $88.6100^\circ\text{E}, 27.3300^\circ\text{N}$ | $3,500$ | $-30^\circ$ | $35^\circ$ |

---

## 5. Security & Isolation Verification

- Zero credential exposure: API keys are masked or verified server-side.
- Zero autonomous dispatch: The 3D presentation layer has no capability to sound sirens or dispatch public alerts.
- Model integrity verified: Production V3 (`7cb8...`) and Research V4.5 (`31e1...`) remain immutable.
