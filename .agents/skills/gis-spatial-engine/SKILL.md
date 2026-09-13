---
name: gis-spatial-engine
description: >-
  Architectural guidelines for GIS, PostGIS spatial queries, vector map layers,
  and hazard-aware Safe Routes computation in PARVAT NETRA.
  Use when implementing GeoJSON endpoints, spatial indexing, terrain DEM processing,
  or multi-criteria route optimization.
---

# PARVAT NETRA — GIS & Geospatial Spatial Engine Guide

PARVAT NETRA operates on high-altitude mountainous terrain (Himalayan / Northeast Region). All spatial data must adhere to rigorous topological, coordinate, and performance standards.

---

## 1. Spatial Standards & Coordinate Reference Systems

- **Storage & Ingestion**: `EPSG:4326` (WGS 84 - Standard Latitude/Longitude in degrees).
- **Metric Calculations (Distance/Buffer/Slope)**: Always cast to `geography` or project to `EPSG:32644` / `EPSG:3857` before computing Euclidean distances in meters:
  ```sql
  -- Accurate distance in meters between sensor station and landslide polygon
  ST_Distance(station.geom::geography, hazard.geom::geography)
  ```
- **Spatial Indexing**: Mandatory GiST index on all spatial columns:
  ```sql
  CREATE INDEX idx_zones_geom ON spatial_zones USING GIST (geom);
  CREATE INDEX idx_roads_geom ON road_network USING GIST (geom);
  ```

---

## 2. Safe Routes Engine (Multi-Criteria Hazard Cost Function)

Safe Routes calculation provides three routing modes:
1. **FASTEST**: Minimizes travel time under current road speed limits.
2. **SHORTEST**: Minimizes total roadway distance in kilometers.
3. **SAFEST**: Multi-criteria Dijkstra / A* cost optimization penalizing landslide hazard exposure:

$$\text{Cost}(e) = \text{Length}(e) \times \left(1.0 + 3.0 \cdot R_{\text{landslide}} + 2.0 \cdot H_{\text{slope}} + 1.5 \cdot W_{\text{rain}}\right) + P_{\text{closure}}$$

Where:
- $R_{\text{landslide}}$: Normalized fused risk score (0.0 to 1.0) along road segment.
- $H_{\text{slope}}$: Slope hazard factor (1.0 if slope > 35° with unstable geology).
- $W_{\text{rain}}$: Real-time rainfall intensity penalty.
- $P_{\text{closure}}$: Infinite penalty ($\infty$) if road status is `CLOSED`.

### Fallback Guarantee (Zero Dead-Ends):
If external routing APIs (Mapbox / Google Maps) are unconfigured or fail, the backend MUST compute paths directly over the local PostGIS `road_network` topology using `pgRouting` or an in-memory NetworkX graph populated from PostGIS `LineString` geometries. **Never render straight-line interpolation when roadway topology exists.**

---

## 3. Map Layer Hierarchy & Interaction Rules

Vector maps (rendered via MapLibre GL or Mapbox GL) must structure layers cleanly:
1. **Base Layer**: Dark tactical canvas (`carto-dark-matter` or dark vector tiles).
2. **Terrain DEM / Slope Mesh**: Hillshade layer with subtle slope angle gradient.
3. **Hazard Polygons**: Color-coded risk zones (Green/Yellow/Amber/Red) with opacity 0.4.
4. **Road Network**: Solid vectors (Green = Open, Amber = Caution, Red = Closed).
5. **Sensor Stations & CCTV**: Interactive pulse markers indicating operational status.
6. **Active Route**: Cyan/Blue illuminated corridor (`#3B82F6`) with turn-by-turn guidance.
