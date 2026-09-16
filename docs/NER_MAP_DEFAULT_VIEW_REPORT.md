# PARVAT NETRA / PAHAD AI — GIS MAP NER DEFAULT VIEW & STATE OUTLINES REPORT
**Platform**: PARVAT NETRA — National Disaster Intelligence Platform for Northeast India  
**Subsystem**: Operational GIS Hazard Viewer (Leaflet / WGS84 EPSG:4326)  
**Task**: Default Map View — Entire Northeast India (All 8 States) + Unobtrusive State Outlines  
**Date**: September 2026  
**Status**: VERIFIED & DEPLOYED  

---

## 1. Executive Summary
The PARVAT NETRA GIS hazard map has been updated so that upon initial launch, the map viewport displays the entire Northeast Region (NER) encompassing all 8 states (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura), rather than prematurely auto-zooming into a single corridor (such as NH-10 in Sikkim).

Subtle, non-distracting geographic state outlines and centered state labels have been rendered in a dedicated Leaflet pane underneath operational hazard and telemetry layers. The highest-risk corridor continues to be evaluated and populated in the telemetry and evidence panels on launch, but without overriding the regional map framing.

---

## 2. Dataset & Provenance
- **Dataset File**: `static/data/ner_state_boundaries.geojson` (and mirror `public/static/data/ner_state_boundaries.geojson`)
- **Dataset Hash (SHA-256)**: `bcff8b13068d3c70725a29764ba39453e472a916527308f7b5b447c7feb2eca7`
- **CRS**: WGS84 / EPSG:4326
- **Provenance**: `[HISTORICAL / OFFICIAL]` — Survey of India / Census of India administrative state boundary vectors
- **Format**: Standard GeoJSON FeatureCollection with exact Polygon/MultiPolygon coordinates and pre-computed state centroids

---

## 3. NER 8-State Coverage & Catalog

| # | State Name | State Code | Capital | Centroid (Lat, Lon) | Geometry Type |
|---|------------|------------|---------|---------------------|---------------|
| 1 | Arunachal Pradesh | AR | Itanagar | 27.75°N, 94.00°E | Polygon |
| 2 | Assam | AS | Dispur | 26.04°N, 92.44°E | Polygon |
| 3 | Manipur | MN | Imphal | 24.46°N, 93.73°E | Polygon |
| 4 | Meghalaya | ML | Shillong | 25.46°N, 91.16°E | Polygon |
| 5 | Mizoram | MZ | Aizawl | 23.01°N, 92.70°E | Polygon |
| 6 | Nagaland | NL | Kohima | 25.89°N, 94.29°E | Polygon |
| 7 | Sikkim | SK | Gangtok | 27.48°N, 88.43°E | Polygon |
| 8 | Tripura | TR | Agartala | 23.70°N, 91.66°E | Polygon |

**Total Feature Count**: 8 states (100% complete coverage of the North Eastern Council / MDoNER statutory mandate).

---

## 4. Geographic Bounding Box
- **NER Regional Extent Bounding Box**:
  - `South-West`: `[21.8000°N, 88.0000°E]`
  - `North-East`: `[29.5000°N, 97.5000°E]`
- **Centroid**: `[25.7000°N, 92.8000°E]`
- **Leaflet Boundary Definition**:
  ```javascript
  window.NER_BOUNDS = L.latLngBounds([[21.8, 88.0], [29.5, 97.5]]);
  map.fitBounds(window.NER_BOUNDS, { padding: [20, 20] });
  ```

---

## 5. Leaflet Architecture & Layer Ordering
To ensure strict adherence to mission-critical operational standards, state boundary vectors and labels must never obscure real-time slope stability risk, sensor alerts, or emergency detour routing:

1. **Dedicated Leaflet Pane**:
   - Pane Name: `nerStateBoundariesPane`
   - `zIndex`: `350`
   - **Visual Stacking Hierarchy**:
     - `Tile Basemap`: `zIndex: 200`
     - `NER State Boundaries (pane)`: `zIndex: 350`
     - `Road Hazard Vectors / CRI Polylines`: `zIndex: 400`
     - `IoT Sensors & InSAR Points`: `zIndex: 600`
     - `Active Sector Circle Marker`: `zIndex: 650`
     - `Leaflet Popups & Emergency Tooltips`: `zIndex: 700+`

2. **Vector Styling**:
   - Outline Color: `#38bdf8` (Cyan / Sky Blue)
   - Stroke Weight: `1.5px`
   - Dash Pattern: `4, 4` (subtle dashed border)
   - Fill Color: `#0284c7`
   - Fill Opacity: `0.03` (transparent tint preserving satellite basemap texture)
   - Hover Feedback: Stroke width increases to `2.2px`, fill opacity to `0.08`, with tooltips showing `<State Name> • Northeast Region`.

3. **Typography & Label Placement**:
   - Centered state labels using `L.divIcon` styled with high-contrast JetBrains Mono font (`.ner-state-center-label`).
   - Non-interactive (`interactive: false`) to prevent intercepting clicks targeted at roads, sensors, or background tiles.
   - Zoom-level awareness: Under zoom level 6 (`curZoom < 6`), the `.ner-map-zoom-low` class smoothly fades out state label markers to avoid clutter.

4. **Layer Control Panel**:
   - Added interactive toggle item under `MAP & LAYER CONTROL`:
     - Label: `NER State Outlines`
     - Key: `state_boundaries`
     - Synchronized with `layerVisibility.state_boundaries` and `layerGroupMap['state_boundaries']`.

---

## 6. Initial Load & User Interaction
1. **Initial Page Load**:
   - `initMap()` starts centered on `[25.7, 92.8]` (zoom 7) and immediately executes `map.fitBounds(window.NER_BOUNDS, { padding: [20, 20] })`.
   - `initHighestRiskCorridor()` selects the top-risk corridor (e.g. NH-10 KM 48), populates all KPI cards, telemetry cards, and drops the active circle marker with `onCorridorSelectionChanged(top.id, false)`.
   - The `shouldZoom = false` flag guarantees that the map does **not** jump away from the regional view on startup.
2. **User Corridor Selection**:
   - When a user explicitly interacts with the corridor selector dropdown or corridor table, `onCorridorSelectionChanged(id, true)` smoothly flies the camera to the selected sector (`zoom 12`).
3. **Reset View Button**:
   - Clicking `#btn-reset-view` invokes `resetMapToNerBounds()`, which cleanly re-fits the map to `window.NER_BOUNDS`, restoring the complete 8-state view at any time.

---

## 7. Verification & Test Results

### 7.1. Dedicated Unit Test Suite (`tests/test_ner_gis_default_view.py`)
- `test_geojson_file_exists`: **PASSED**
- `test_geojson_endpoint_serves_200`: **PASSED**
- `test_all_eight_ner_states_present`: **PASSED** (8/8 states verified)
- `test_ner_coordinate_bounding_box`: **PASSED** (lat [21.8, 29.5], lon [88.0, 97.5])
- `test_index_html_ner_configuration`: **PASSED** (NER_BOUNDS, pane zIndex 350, fitBounds, reset button, non-auto-zoom)
- `test_css_styling_for_ner_labels`: **PASSED** (label marker, center label, low zoom fade)

### 7.2. Core System Regression Suite
- `tests/test_map_modes.py`: **5/5 PASSED**
- `tests/test_pahad_data_fusion.py`: **7/7 PASSED**
- `tests/test_terrain_api.py`: **12/12 PASSED**
- `tests/test_weather_service.py`: **8/8 PASSED**
- **Total Tests Passed**: **38 / 38 (100%)**
