# PAHAD AI — Satellite Earth Observation Architecture
## PARVAT NETRA Disaster Intelligence Platform
**SIH Problem Statement: 26001 | Ministry of Development of North Eastern Region (MDoNER)**

---

> [!IMPORTANT]
> This document describes the satellite intelligence subsystem of PARVAT NETRA / PAHAD AI.
> Data provenance tiers are strictly enforced. Any output that does not originate from a live,
> authenticated pipeline is labelled **[SIMULATED]**, **[CACHED]**, **[HISTORICAL]**, **[DEMO]**,
> or **[STATIC_PRODUCT]** at the point of generation and in every downstream API response.
> No field shall carry a live-data label without `PARVAT_LIVE_INSAR_PIPELINE=1` being active.

---

## Table of Contents

1. [Satellite Intelligence Overview](#1-satellite-intelligence-overview)
2. [Sentinel-1 InSAR Line-of-Sight (LOS) Deformation](#2-sentinel-1-insar-line-of-sight-los-deformation)
3. [GLO-30 DEM Terrain Attributes](#3-glo-30-dem-terrain-attributes)
4. [NDVI Anomaly Detection — Sentinel-2 / MODIS](#4-ndvi-anomaly-detection--sentinel-2--modis)
5. [Satellite Data Ingestion Architecture](#5-satellite-data-ingestion-architecture)
6. [Provenance Classification Matrix](#6-provenance-classification-matrix)
7. [API and Engine Integration](#7-api-and-engine-integration)
8. [Operational Limitations](#8-operational-limitations)
9. [Configuration Reference](#9-configuration-reference)

---

## 1. Satellite Intelligence Overview

PAHAD AI integrates three complementary satellite sensor streams for multi-modal
hillslope instability intelligence across the North-Eastern Region (NER) of India.
Each sensor type captures a different physical signal; fusion of all three produces
the Composite Risk Index (CRI) used for operational alerting.

### 1.1 Tracked Sensor Missions

| # | Mission | Sensor Class | Resolution | Primary Observable | Source Gateway |
|---|---------|-------------|------------|-------------------|---------------|
| 1 | **Sentinel-2A MSI** | Optical Multispectral | 10 m (B04/B08) | Surface reflectance, NDVI, landslide scarps | Copernicus Open Access Hub / ESA |
| 2 | **Sentinel-1A C-Band SAR** | SAR IW SLC | ~5 × 20 m (IW SLC) | Ground displacement LOS, InSAR deformation | Copernicus Sentinel-1 / ESA |
| 3 | **ISRO NISAR S-Band SAR** | SAR S-Band | ~10 m | Deep soil moisture, sub-canopy deformation | ISRO NRSC Bhoonidhi / NASA-ISRO SAR |

These missions are tracked in the `NER_SATELLITE_ACQUISITIONS` list within
`services/satellite_service.py` (lines 57–124) and are exposed through the
`SatelliteService` singleton (`SATELLITE_SERVICE`).

### 1.2 Geographic Scope

The system monitors two nested spatial extents:

| Extent | Lat Range | Lon Range | Purpose |
|--------|-----------|-----------|---------|
| **NER Bounds** (full) | 20.0° N – 30.0° N | 87.0° E – 98.0° E | Regional catalog search and DEM coverage |
| **Sikkim Focus** | 26.8° N – 28.2° N | 88.0° E – 89.2° E | High-resolution InSAR, NDVI, DEM terrain analysis |

Primary hazard epicenter used by SAR Tracking: **27.2010° N, 88.5180° E** (NH-10 Km 48 / 29th Mile),
with a 15 km hazard radius.

### 1.3 Service Architecture

```
SatelliteService (singleton: SATELLITE_SERVICE)
├── InSARDeformationProcessor  (engine/pahad_insar.py)
├── NER_SATELLITE_ACQUISITIONS (catalog: 3 records)
└── Public Methods:
    ├── get_latest_acquisition(sensor_type?)   → Dict
    ├── get_all_acquisitions()                 → List[Dict]
    ├── get_footprints_geojson()               → GeoJSON FeatureCollection
    └── get_insar_deformation_for_sector(id)   → Dict [SIMULATED | PROCESSED_LIVE]
```

The `SATELLITE_SERVICE` singleton is instantiated at module import time. Its InSAR processor
is an instance of `InSARDeformationProcessor` (`engine/pahad_insar.py`, lines 65–190),
which is always available. However, whether it runs on real or simulated input depends
entirely on the `PARVAT_LIVE_INSAR_PIPELINE` environment variable.

---

## 2. Sentinel-1 InSAR Line-of-Sight (LOS) Deformation

### 2.1 Mission & Orbital Parameters

| Parameter | Value |
|-----------|-------|
| Mission | Sentinel-1A (ESA Copernicus) |
| Sensor | C-Band SAR, 5.405 GHz |
| Processing Level | Single Look Complex (SLC), Interferometric Wide (IW) swath |
| Scene ID (latest) | `S1A_IW_SLC__1SDV_20260825T112040` |
| Orbit Track | 121 |
| Pass Direction | Descending |
| Acquisition Time | 2026-08-25T11:20:40Z |
| Footprint | 88.00°E–89.30°E × 26.70°N–28.10°N |
| Repeat Pass Cycle | **12 days** |
| All-Weather Capable | Yes (cloud cover: 0.0%) |
| Provenance Tier | `[SIMULATED]` (default when live pipeline is offline) |

Sentinel-1's 12-day repeat pass cycle is the **fundamental temporal resolution floor**
for interferometric pairs. No InSAR measurement is possible between two acquisitions
within the same 12-day window. This is a hard orbital constraint, not a software limitation.

### 2.2 InSAR Processing Chain

When `PARVAT_LIVE_INSAR_PIPELINE=1`:

```
Sentinel-1A SLC Scene Pair (12-day interval)
         │
         ▼
  Co-registration & Interferogram Formation
  (Range-Doppler geometry, IW SLC burst)
         │
         ▼
  Adaptive Filtering (Goldstein filter)
         │
         ▼
  Phase Unwrapping
  (SNAPHU or MCF algorithm)
         │
         ▼
  Geocoding to WGS84 (EPSG:4326)
         │
         ▼
  InSARDeformationProcessor.analyze_slope_deformation()
  ┌─────────────────────────────────────────────────────┐
  │  Input:                                             │
  │    displacement_time_series_mm  (LOS mm, cumulative)│
  │    time_intervals_days          (e.g. [12,24,36,48])│
  │    coherence                    (float, 0.0–1.0)    │
  └─────────────────────────────────────────────────────┘
         │
         ▼
  Velocity, Acceleration, Inverse-Velocity, Creep State
  → InSARAnalysisResult (deformation_source_tier: [PROCESSED_LIVE])
```

When `PARVAT_LIVE_INSAR_PIPELINE` is **not set or is `0`** (default state):

- The processor runs on **physics-calibrated simulated displacement series**
- Output is explicitly labelled `deformation_source_tier: "[SIMULATED]"`
- The `status` field is set to `"SIMULATED_BASELINE"`, never `"AVAILABLE"`
- A mandatory `notice` field states: _"Real-time automated interferogram unwrapping currently
  offline; displaying physics-calibrated InSAR simulation."_

See `get_insar_deformation_for_sector()` in `services/satellite_service.py` (lines 181–219)
for the authoritative branching logic.

### 2.3 Simulated Baseline Displacement Series

The sector-specific simulated displacement series used when live pipeline is inactive:

| Sector | Displacement Series (mm) | Time Intervals (days) | Coherence |
|--------|--------------------------|----------------------|-----------|
| **KM48** (NH-10 Km 48) | [-1.5, -3.2, -6.1, -11.4] | [12, 24, 36, 48] | 0.72 |
| **Other sectors** | [-0.5, -1.1, -2.2, -4.0] | [12, 24, 36, 48] | 0.72 |

These values are geotechnically calibrated to represent realistic creep rates for
the Teesta Basin lithology. They must never be presented as measured values.

> [!IMPORTANT]
> **[SIMULATED]** — The above displacement series are physics-calibrated simulations.
> They are NOT measured interferometric displacements. Do not cite them as field measurements.

### 2.4 InSAR Geotechnical Formulations

All calculations are implemented in `engine/pahad_insar.py`:

```
Velocity:        v = Δd / Δt              [mm/day]
Annual velocity: v_annual = v × 365.25    [mm/year]
Acceleration:    a = Δv / Δt              [mm/day²]
Inverse velocity: 1/v                     (Fukuzono 1985 / Voight 1988 tertiary creep)
```

**Creep State Classification:**

| Condition | Creep State |
|-----------|------------|
| `v_annual > 50 mm/yr` **OR** `a > 0.5 mm/day²` | `TERTIARY_CREEP_ACCELERATION` |
| `v_annual > 15 mm/yr` | `STEADY_SECONDARY_CREEP` |
| Otherwise | `BASE_STABLE_OR_SETTLING` |

**InSAR Anomaly Factor (A_insar)** — normalized [0.0, 1.0] for CRI multi-modal fusion:

| Creep State | Formula |
|-------------|---------|
| `TERTIARY_CREEP_ACCELERATION` | `0.80 + 0.20 × min(a / 1.0, 1.0)` |
| `STEADY_SECONDARY_CREEP` | `0.40 + 0.38 × min((v_annual − 15) / 35, 1.0)` |
| `BASE_STABLE_OR_SETTLING` | `0.35 × min(v_annual / 15, 1.0)` |

**Fukuzono Collapse Risk** is flagged when creep state is `TERTIARY_CREEP_ACCELERATION`
AND `1/v < 0.1` (i.e., velocity > 10 mm/day — imminent failure threshold).

### 2.5 Coherence Validation

| Parameter | Value | Source |
|-----------|-------|--------|
| Coherence threshold | **0.45** | `COHERENCE_THRESHOLD` constant in `pahad_insar.py` line 30 |
| Reliability if coherence ≥ 0.45 | `"HIGH"` | |
| Reliability if coherence < 0.45 | `"LOW"` | |
| Typical live coherence (KM48 sector) | 0.78 | `satellite_service.py` live pipeline path |
| Simulated coherence (all sectors) | 0.72 | `satellite_service.py` simulated path |

> [!WARNING]
> Interferometric coherence below **0.45** indicates excessive phase noise — likely due to
> dense vegetation cover, severe rainfall, or temporal decorrelation from rapid surface
> change (e.g., active debris flow). Deformation values computed at coherence < 0.45
> must not be used for quantitative displacement measurements. The `reliability` field
> will read `"LOW"` in all such cases.

### 2.6 NISAR S-Band SAR Status

| Parameter | Value |
|-----------|-------|
| Scene ID | `NISAR_S_BAND_20260820T061015` |
| Orbit Track | 48 (Ascending) |
| Acquisition Time | 2026-08-20T06:10:15Z |
| Processing Level | L2 Geocoded Unwrapped Interferogram |
| Processing Status | `PENDING_UNWRAP` |
| Provenance Tier | `[SIMULATED]` |
| Source | ISRO NRSC Bhoonidhi / NASA-ISRO SAR |
| Footprint | 88.20°E–89.05°E × 26.95°N–27.80°N |

NISAR's S-band penetrates vegetation canopy more deeply than Sentinel-1 C-band,
providing superior coherence on forested hillslopes — critical for Sikkim's dense moist
temperate forest corridors. Until `PENDING_UNWRAP` resolves, NISAR data carries
`[SIMULATED]` provenance.

---

## 3. GLO-30 DEM Terrain Attributes

### 3.1 DEM Sources and Resolution

The `DEMService` singleton (`DEM_SERVICE`) in `services/dem_service.py` supports
the following elevation data sources:

| Source | Resolution | Provenance |
|--------|-----------|------------|
| **Copernicus GLO-30** (default) | 30 m | `[HISTORICAL]` |
| **ISRO CartoDEM** | 30 m | `[HISTORICAL]` |
| **NASA SRTM / NASADEM** | 30 m | `[HISTORICAL]` |
| Local GeoTIFF cache | 30 m | `[HISTORICAL]` |

**Primary source string (code):** `"Copernicus GLO-30 / ISRO CartoDEM"`

The DEM source data is classified as `[HISTORICAL]` — it represents a static baseline of
terrain geometry and does not update in real time. All terrain attribute derivatives
computed from the DEM are classified as `[MODELLED]`.

### 3.2 Vertical Datum and CRS

| Parameter | Value |
|-----------|-------|
| Horizontal CRS | `EPSG:4326` (WGS84 Geographic) |
| Vertical datum | `EGM2008` (Earth Gravitational Model 2008) |
| Alternate datum | WGS84 ellipsoidal height (for GNSS interoperability) |
| Supported CRS inputs | `EPSG:4326`, `WGS84`, `EPSG:3857`, `EPSG:32645` |

> [!NOTE]
> EGM2008 orthometric heights are used throughout the platform. GNSS-derived ellipsoidal
> heights must be corrected with the EGM2008 geoid undulation model before comparison
> with DEM-derived elevations. Separation in the Sikkim region is approximately +36 m
> to +39 m (geoid above ellipsoid).

### 3.3 Local GeoTIFF Cache Location

The local raster cache is stored at:

```
data/geospatial/dem/
└── ner_elevation_30m.tif      ← Primary GeoTIFF raster (GLO-30 mosaic, NER coverage)
```

The full `data/geospatial/` directory structure is:

```
data/geospatial/
├── dem/                       ← DEM GeoTIFF raster cache
├── imagery/                   ← Optical scene cache (Sentinel-2 tiles)
├── landslides/                ← Landslide inventory GIS layers
├── roads/                     ← Road network (NH-10, NH-717A, etc.)
├── terrain_products/          ← Pre-computed terrain attribute grids
└── vegetation/                ← NDVI product cache (Sentinel-2 derived)
```

The `DEMService.__init__()` auto-creates `data/geospatial/dem/` if absent:

```python
self.dem_dir = dem_dir or os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "geospatial", "dem"
)
os.makedirs(self.dem_dir, exist_ok=True)
self.local_raster_path = os.path.join(self.dem_dir, "ner_elevation_30m.tif")
```

### 3.4 Elevation Range (Sikkim Focus Area)

| Attribute | Value | Notes |
|-----------|-------|-------|
| Minimum elevation | 210 m | Teesta alluvial plain at Sevoke |
| Maximum elevation | 4,850 m | North Sikkim high-altitude ridge |
| NH-10 Km 48 road-level | ~540 m | GSI critical sector calibration point |

### 3.5 Terrain Attribute Computation

All terrain derivatives are computed by `get_point_terrain_attributes()` in `dem_service.py`
(lines 182–236) using a 3×3 local sub-grid centred at the query point. The sub-grid
spacing `delta_deg = 0.0003°` (≈ 33 m at 27°N).

#### 3.5.1 Slope — Horn Finite-Difference Method

```
dz/dx = [(z_NE + 2·z_E + z_SE) − (z_NW + 2·z_W + z_SW)] / (8 · cell_m)
dz/dy = [(z_SW + 2·z_S + z_SE) − (z_NW + 2·z_N + z_NE)] / (8 · cell_m)

slope_rad = arctan(√((dz/dx)² + (dz/dy)²))
slope_deg = degrees(slope_rad)
```

`cell_m` is computed as: `delta_deg × 111,000 × cos(lat_rad)` to account for
meridional convergence at the observation latitude.

The Horn (1981) 8-neighbour weighted finite-difference scheme is used, which provides
more accurate slope estimates than the simple 4-neighbour method, particularly in areas
of complex topography such as the Teesta gorge valley walls.

#### 3.5.2 Aspect — Zevenbergen-Thorne Method

```
aspect_rad = atan2(dz/dy, −dz/dx)
aspect_deg = (degrees(aspect_rad) + 360) % 360
```

Aspect is measured clockwise from North (0° = North, 90° = East, 180° = South,
270° = West). South-facing slopes (135°–225°) in the Himalayan context receive higher
solar radiation and lower long-term soil moisture; however, north-facing slopes in Sikkim
often coincide with steeper glacially-carved valley walls with higher intrinsic failure
probability due to oversteepening.

#### 3.5.3 Curvature — Laplacian Approximation

```
curvature = [(z_W + z_E + z_N + z_S) / 4 − z_center] / cell_m
```

Positive curvature → convex slope (diverging flow, lower saturation risk).
Negative curvature → concave slope (converging flow, higher saturation and
pore-pressure risk — primary trigger zone for debris flows).

#### 3.5.4 Terrain Ruggedness Index (TRI) — Riley et al. (1999)

```
TRI = √(Σ(z_neighbor − z_center)² / 8)
```

Computed over all 8 neighbours of the 3×3 grid. High TRI values (>200 m) indicate
highly dissected ridge-and-gully terrain typical of active tectonic uplift zones in
the Himalayan collision arc.

#### 3.5.5 Relative Relief

```
relative_relief = max(grid_3x3) − min(grid_3x3)
```

Expressed in metres over the 3×3 local window (~99 m × 99 m at 27°N).
Values > 500 m indicate extreme local vertical relief, a primary conditioning factor
for deep-seated landslide susceptibility.

### 3.6 DEMService Output Schema

Example output from `get_point_terrain_attributes()`:

```json
{
  "latitude": 27.33000,
  "longitude": 88.60000,
  "elevation_m": 540.0,
  "slope_deg": 38.42,
  "aspect_deg": 217.3,
  "curvature": -0.0021,
  "terrain_ruggedness_index": 124.88,
  "relative_relief_m": 312.4,
  "resolution_m": 30.0,
  "crs": "EPSG:4326",
  "source": "Copernicus GLO-30 / ISRO CartoDEM",
  "provenance": "[HISTORICAL]"
}
```

> [!NOTE]
> The `provenance` field in terrain attribute output reads `"[HISTORICAL]"` (from
> `DEMService.provenance`). The derived attributes (slope, curvature, etc.) are
> properly classified as `[MODELLED]` in system documentation, being computed from
> `[HISTORICAL]` source data.

---

## 4. NDVI Anomaly Detection — Sentinel-2 / MODIS

### 4.1 Formulation

The `VegetationService` singleton (`VEGETATION_SERVICE`) in `services/vegetation_service.py`
computes NDVI from Sentinel-2 Level-2A Bottom-of-Atmosphere (BOA) surface reflectance:

```
NDVI = (NIR − RED) / (NIR + RED)

Where:
  RED = Sentinel-2 Band 4 (centre wavelength: 665 nm, spatial resolution: 10 m)
  NIR = Sentinel-2 Band 8 (centre wavelength: 842 nm, spatial resolution: 10 m)

Domain: NDVI ∈ [−1.0, 1.0]
```

Implemented in `calculate_ndvi()` (lines 95–106 of `vegetation_service.py`).
Division-by-zero guard: if `NIR + RED ≤ 1×10⁻⁷`, returns `0.0`.
Output is clipped to `[−1.0, 1.0]` and rounded to 4 decimal places.

### 4.2 Vegetation State Classification Tiers

| NDVI Range | State Label | Geomorphic Significance |
|-----------|-------------|------------------------|
| ≥ 0.65 | `DENSE_FOREST_CANOPY` | High root cohesion; baseline slope protection active |
| 0.45 – 0.65 | `MODERATE_VEGETATION` | Partial canopy; moderate root reinforcement |
| 0.25 – 0.45 | `SPARSE_VEGETATION_OR_STRESS` | Degraded cohesion; canopy stress or disturbance |
| 0.10 – 0.25 | `DEGRADED_SCRUB_EXPOSED_SOIL` | Significant bare soil exposure; elevated susceptibility |
| < 0.10 | `BARE_ROCK_ACTIVE_SCARP_WATER` | Active landslide scarp, bare rock face, or water body |

> [!CAUTION]
> **Scientific Caveat (mandatory):**
> _"Vegetation loss contributes to hillslope susceptibility; it does not in isolation
> cause landslide failure."_
>
> NDVI anomalies are one of multiple conditioning factors in the CRI. A low NDVI score
> must never be presented to users as a direct landslide warning in isolation.
> Root cohesion reduction adds approximately +0.06 to the static terrain susceptibility
> component when significant canopy loss (ΔNDVI < −0.10) is detected.

### 4.3 Monitored Vegetation Corridors

The following corridors have authoritative baseline records in `CORRIDOR_VEGETATION_BASELINES`
(`vegetation_service.py`, lines 41–92):

| Corridor ID | Sector Name | Canopy Type | 30-Day Baseline NDVI | Scar Loss % | Provenance |
|------------|-------------|-------------|----------------------|-------------|------------|
| `SK-NH10-KM48` | NH-10 Km 48 (29th Mile Sector) | Sub-tropical hill sal & mixed broadleaf | 0.742 | 8.4% | `[CACHED]` |
| `SK-SINGTAM-01` | Singtam Teesta Basin Toe-Scour Zone | Riparian bank vegetation & scrub | 0.620 | 14.2% | `[CACHED]` |
| `SK-DIKCHU-01` | Dikchu Hydro Sector Bluffs | Dense moist temperate forest | 0.755 | 3.1% | `[CACHED]` |
| `SK-MANGAN-01` | Mangan Relict Landslide Complex | Degraded secondary scrub on colluvium | 0.485 | 22.6% | `[CACHED]` |
| `MZ-HUNTHAR-01` | Aizawl NH-6 Hunthar Veng Slump | Urban fringe bamboo scrub & slope cuts | 0.450 | 18.0% | `[CACHED]` |

All NDVI products are derived from Sentinel-2 scene `S2A_MSIL2A_20260828T044531`
(acquired 2026-08-28T04:45:31Z, orbit track 134, descending pass, cloud cover 14.2%).
All corridor baselines carry provenance tag `[CACHED]`.

### 4.4 Band Reflectance Records

Current scene Band 4 (RED) and Band 8 (NIR) reflectances per corridor:

| Corridor | RED (B04) | NIR (B08) | Computed NDVI |
|----------|-----------|-----------|---------------|
| `SK-NH10-KM48` | 0.082 | 0.468 | 0.7010 |
| `SK-SINGTAM-01` | 0.115 | 0.395 | 0.5490 |
| `SK-DIKCHU-01` | 0.076 | 0.490 | 0.7317 |
| `SK-MANGAN-01` | 0.148 | 0.292 | 0.3267 |
| `MZ-HUNTHAR-01` | 0.162 | 0.315 | 0.3212 |

Provenance: `[CACHED]` — sourced from Sentinel-2 Level-2A BOA reflectance products
stored in `data/geospatial/vegetation/`.

### 4.5 NDVI Change Detection for Landslide Scarp Mapping

Multi-temporal NDVI difference `(NDVI_current − NDVI_baseline_30d)` is computed
per corridor. Interpretation rules applied by `get_vegetation_for_sector()`:

| ΔNDVI Threshold | Interpretation |
|-----------------|----------------|
| `< −0.10` | Significant canopy loss; contributes +0.06 to static terrain susceptibility |
| `−0.10` to `−0.04` | Mild canopy disturbance along corridor edge; minor susceptibility modifier |
| `≥ −0.04` | Intact root cohesion and vegetation canopy; baseline slope protection active |

NDVI anomalies can identify:
- Fresh landslide scarp exposure (NDVI drop from ≥0.65 to <0.10 in a single scene pair)
- Progressive canopy stress preceding slope failure
- Riparian vegetation loss from river bank erosion / toe scour

### 4.6 Sentinel-2 Scene Metadata

The Sentinel-2 acquisition tracked by PAHAD AI:

| Field | Value |
|-------|-------|
| Sensor ID | `S2A_MSIL2A_20260828T044531` |
| Mission | Sentinel-2A MSI |
| Processing Level | Level-2A BOA Surface Reflectance |
| Cloud Cover | 14.2% |
| Orbit Track | 134 (Descending) |
| Source | Copernicus Open Access Hub / ESA |
| Deformation Source Tier | `[STATIC_PRODUCT]` |
| Provenance | `[CACHED]` |
| Spatial Resolution | 10 m (Bands B02, B03, B04, B08) |
| Footprint | 88.10°E–89.15°E × 26.90°N–27.95°N |

---

## 5. Satellite Data Ingestion Architecture

### 5.1 Static Catalog (Default / Offline-Capable)

In the absence of authenticated API credentials, PAHAD AI operates from a
**pre-seeded static catalog** of acquisition metadata embedded in
`NER_SATELLITE_ACQUISITIONS` (lines 57–124 of `satellite_service.py`).

This static catalog:
- Contains exact `footprint_geojson` polygons in GeoJSON `Polygon` format for all 3 missions
- Carries explicit `provenance`, `deformation_source_tier`, and `processing_status` per record
- Is served via `get_all_acquisitions()` and `get_footprints_geojson()` with no external dependency
- Enables full demonstration and operational-planning capability at zero API cost
- Is appropriate for training, demonstration, and planning scenarios

### 5.2 Live API Proxies

Live scene acquisition requires the following authenticated endpoints:

#### 5.2.1 Copernicus Data Space Ecosystem (ESA)

- **Purpose:** Sentinel-1A SLC and Sentinel-2A L2A scene discovery and download
- **Auth:** OAuth 2.0 client credentials
  - `COPERNICUS_CLIENT_ID` (env var)
  - `COPERNICUS_CLIENT_SECRET` (env var)
- **API base:** `dataspace.copernicus.eu`
- **Scene search:** OData query by collection, temporal range, footprint WKT, processing level
- **Download:** HTTPS direct download of SLC product ZIP archives

#### 5.2.2 Sentinel Hub Process API (Sinergise / Planet Labs)

- **Purpose:** On-the-fly band reflectance retrieval, NDVI computation, imagery tiles
- **Auth:** Instance-based — `SENTINEL_HUB_INSTANCE_ID` (env var)
- **Protocol:** Process API (evalscript-based computation)
- **NDVI evalscript:** `return [(B08 - B04) / (B08 + B04 + 1e-10)]`

#### 5.2.3 ISRO Bhoonidhi (NRSC Data Portal)

- **Purpose:** NISAR S-Band SAR L2 unwrapped interferogram acquisition
- **Auth:** Bhoonidhi registered institutional credentials (separate from Copernicus)
- **Integration:** REST API for scene catalog query; SFTP for bulk product download
- **Current status:** `PENDING_UNWRAP` for scene `NISAR_S_BAND_20260820T061015`
  (typical L2 latency from NRSC: 3–5 days post-acquisition)

### 5.3 Ingestion State Machine

```
On service initialisation
│
├─ [Credentials absent OR PARVAT_LIVE_INSAR_PIPELINE ≠ 1]
│   └── Load NER_SATELLITE_ACQUISITIONS from embedded static catalog
│       All provenance: [CACHED] / [SIMULATED] / [STATIC_PRODUCT]
│       InSAR: SIMULATED_BASELINE path
│
└─ [PARVAT_LIVE_INSAR_PIPELINE=1 AND credentials present]
    ├── OAuth2 authentication with Copernicus Data Space
    ├── Query latest S1A SLC pair over Sikkim bounds (88.0–89.2°E, 26.8–28.2°N)
    ├── Download SLC pair → local staging directory
    ├── Co-registration + interferogram formation
    ├── Phase unwrap (SNAPHU/MCF) → geocode to EPSG:4326
    ├── Feed displacement series into InSARDeformationProcessor
    └── All InSAR provenance: [PROCESSED_LIVE]
```

### 5.4 Data Freshness and Cache Policy

| Layer | Cache Location | Refresh Policy | Provenance |
|-------|---------------|----------------|------------|
| DEM raster | `data/geospatial/dem/ner_elevation_30m.tif` | Static (on-disk) | `[HISTORICAL]` |
| NDVI products | `data/geospatial/vegetation/` | Per Sentinel-2 scene (~5 days) | `[CACHED]` |
| SAR/InSAR scene metadata | In-memory `NER_SATELLITE_ACQUISITIONS` | At service restart | `[SIMULATED]` / `[PROCESSED_LIVE]` |
| Terrain attributes | In-process `DEMService._cache` dict (lat/lon keyed) | Persistent across requests | `[HISTORICAL]` / `[MODELLED]` |
| Imagery tiles | `data/geospatial/imagery/` | On demand | `[CACHED]` |
| Landslide inventory | `data/geospatial/landslides/` | On dataset update | `[HISTORICAL]` |

### 5.5 SAR Hazard Zone Tracking Integration

The `SARTrackingService` singleton (`SAR_TRACKING_SERVICE`) uses satellite-derived
hazard geometry as follows:

```python
# services/sar_tracking.py
HAZARD_EPICENTER_LAT = 27.2010   # NH-10 Km 48 (SAR-derived deformation centroid)
HAZARD_EPICENTER_LNG = 88.5180
HAZARD_RADIUS_KM     = 15.0     # 15 km perimeter from epicenter
DISCONNECT_TIMEOUT_SEC = 120.0  # Silence > 120s inside hazard zone → SAR TARGET
```

Devices within this radius that go silent for > 120 seconds are flagged as
`OFFLINE_DISCONNECTED` and escalated as SAR targets for NDRF dispatch.
The Haversine formula (`calculate_haversine_km()`) computes distance to epicenter
on every `get_devices()` call, ensuring real-time positional re-evaluation without
stale cache.

---

## 6. Provenance Classification Matrix

Every satellite-derived data point in PAHAD AI carries an explicit provenance tag.
This table defines the complete taxonomy:

| Tier Label | When Applied | Data Reliability | UI Display Requirement |
|-----------|--------------|-----------------|----------------------|
| `[PROCESSED_LIVE]` | `PARVAT_LIVE_INSAR_PIPELINE=1` AND authenticated pipeline completes successfully | **Operational — supports decisions** | Green badge; no simulation warning required |
| `[STATIC_PRODUCT]` | Published GSI/ISRO InSAR deformation surface from a prior established baseline | **Reference-grade** | Blue badge; note "historical baseline" |
| `[CACHED]` | Pre-processed Sentinel-2 NDVI / scene metadata stored locally | **Operationally valid** but potentially stale | Grey badge; show scene acquisition date |
| `[HISTORICAL]` | DEM source data (GLO-30, SRTM, CartoDEM) | **Static reference** — terrain changes slowly | Grey badge; "DEM source: historical" |
| `[MODELLED]` | Derived terrain attributes (slope, aspect, curvature) computed from `[HISTORICAL]` DEM | **Physics-derived from historical data** | Grey badge; "computed from DEM" |
| `[SIMULATED]` | InSAR displacement / SAR provenance when live pipeline offline | **Physics-calibrated estimate — NOT measured** | **Yellow warning badge; simulation notice MANDATORY** |
| `[DEMO]` | Evaluation demo / walkthrough sequences | **Non-operational scenario data** | Orange badge; "DEMO MODE" banner mandatory |

> [!CAUTION]
> **`[SIMULATED]` data must never be presented without a visible warning label.**
> Displaying simulated InSAR deformation values without the simulation notice to emergency
> managers could result in incorrect evacuation or response decisions.
> This is a safety-critical labelling requirement enforced at the service layer via
> the `notice` field in `get_insar_deformation_for_sector()`.

### 6.1 `SatelliteAcquisitionRecord` Provenance Fields

Each acquisition record in `NER_SATELLITE_ACQUISITIONS` carries two distinct provenance fields:

```python
@dataclass
class SatelliteAcquisitionRecord:
    deformation_source_tier: str  # '[PROCESSED_LIVE]' | '[STATIC_PRODUCT]' | '[SIMULATED]' | '[DEMO]'
    provenance: str               # '[PROCESSED_LIVE]' | '[CACHED]' | '[SIMULATED]' | '[HISTORICAL]'
```

`deformation_source_tier` specifically qualifies the InSAR/deformation component quality.
`provenance` qualifies the overall acquisition record's data lineage.
Both fields must be present and truthful in every API response.

### 6.2 Per-Acquisition Provenance Summary

| Scene | Sensor | `deformation_source_tier` | `provenance` |
|-------|--------|--------------------------|-------------|
| `S2A_MSIL2A_20260828T044531` | Sentinel-2A MSI | `[STATIC_PRODUCT]` | `[CACHED]` |
| `S1A_IW_SLC__1SDV_20260825T112040` | Sentinel-1A C-Band SAR | `[SIMULATED]` | `[SIMULATED]` |
| `NISAR_S_BAND_20260820T061015` | ISRO NISAR S-Band SAR | `[SIMULATED]` | `[SIMULATED]` |

---

## 7. API and Engine Integration

### 7.1 `SatelliteService` — Public Interface

**Module:** `services/satellite_service.py`
**Singleton:** `SATELLITE_SERVICE`
**Constructor:** Instantiates `InSARDeformationProcessor` and loads `NER_SATELLITE_ACQUISITIONS`

#### `get_latest_acquisition(sensor_type=None) → Dict`

Returns the most recently acquired scene, optionally filtered by sensor type
(`"OPTICAL"`, `"SAR_C_BAND"`, `"SAR_S_BAND"`). Sorted by `acquisition_time` descending.
Returns `None` if no matching record exists.

#### `get_all_acquisitions() → List[Dict]`

Returns all 3 tracked acquisitions as a list of dictionaries, each serialised from
`SatelliteAcquisitionRecord.to_dict()`.

#### `get_footprints_geojson() → Dict`

Returns a GeoJSON `FeatureCollection` containing:
- One `Feature` per tracked acquisition
- `geometry`: footprint `Polygon` in WGS84 geographic coordinates
- `properties`: all acquisition metadata including provenance, processing level, and status
- `metadata.total_scenes`: integer count of features
- `metadata.generated_at`: ISO 8601 UTC timestamp of response generation

#### `get_insar_deformation_for_sector(sector_id: str) → Dict`

**Primary InSAR output method.** Branch behaviour:

**When `PARVAT_LIVE_INSAR_PIPELINE=1`:**
```json
{
  "sector_id": "SK-NH10-KM48",
  "status": "AVAILABLE",
  "deformation_source_tier": "[PROCESSED_LIVE]",
  "provenance": "[LIVE]",
  "analysis": { ... InSARAnalysisResult ... },
  "message": "Live interferometric velocity unwrap completed"
}
```

**When `PARVAT_LIVE_INSAR_PIPELINE` is unset or `0` (default):**
```json
{
  "sector_id": "SK-NH10-KM48",
  "status": "SIMULATED_BASELINE",
  "deformation_source_tier": "[SIMULATED]",
  "provenance": "[SIMULATED]",
  "analysis": { ... InSARAnalysisResult ... },
  "notice": "Real-time automated interferogram unwrapping currently offline; displaying physics-calibrated InSAR simulation."
}
```

### 7.2 `InSARDeformationProcessor` — Engine Interface

**Module:** `engine/pahad_insar.py`
**Class:** `InSARDeformationProcessor`

```python
processor = InSARDeformationProcessor(coherence_threshold=0.45)

result = processor.analyze_slope_deformation(
    displacement_time_series_mm=[-2.1, -4.8, -8.2, -14.5],
    time_intervals_days=[12.0, 24.0, 36.0, 48.0],
    coherence=0.78
)
# Returns: {"status": "SUCCESS", "data": {...}, "provenance": "[SIMULATED] ISRO NISAR S-band & Sentinel-1 InSAR"}
```

**`analyze_slope_deformation()` parameter contract:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `displacement_time_series_mm` | `List[float]` | Cumulative or sequential LOS displacements (mm, negative = LOS shortening / subsidence) |
| `time_intervals_days` | `List[float]` | Cumulative days or per-interval step durations matching displacement series |
| `coherence` | `float` | Interferometric coherence [0.0, 1.0]; clamped to domain internally |

**`InSARAnalysisResult` output fields:**

| Field | Type | Description |
|-------|------|-------------|
| `velocity_mm_day` | float | Latest LOS velocity in mm/day |
| `velocity_mm_year` | float | Annualised velocity (× 365.25) |
| `acceleration_mm_day2` | float | Rate of velocity change in mm/day² |
| `inverse_velocity` | float or null | 1/v in day/mm; null if v ≈ 0 (Fukuzono/Voight method) |
| `creep_status` | str | `TERTIARY_CREEP_ACCELERATION` / `STEADY_SECONDARY_CREEP` / `BASE_STABLE_OR_SETTLING` |
| `insar_anomaly_factor` | float | Normalised [0.0, 1.0] — feeds CRI multi-modal fusion |
| `coherence` | float | Input coherence value (clamped) |
| `coherence_reliable` | bool | True if coherence ≥ 0.45 |
| `reliability` | str | `"HIGH"` or `"LOW"` |
| `provenance` | str | Always `"[SIMULATED] ISRO NISAR S-band & Sentinel-1 InSAR"` |
| `metadata.fukuzono_collapse_risk` | bool | True if TERTIARY_CREEP and 1/v < 0.1 |

### 7.3 `DEMService` — Terrain API

**Module:** `services/dem_service.py`
**Singleton:** `DEM_SERVICE`

| Method | Returns | Notes |
|--------|---------|-------|
| `get_metadata()` | `DEMMetadata.to_dict()` | Source, vertical datum, resolution, bounds, elevation range |
| `get_elevation(lat, lon)` | `float` (metres) | LRU-style `_cache` dict keyed by `"{lat:.4f}_{lon:.4f}"` |
| `get_elevation_grid(...)` | `(np.ndarray, lats, lons)` | 2D elevation grid; default 32×32 cells |
| `get_point_terrain_attributes(lat, lon, delta_deg)` | `Dict` | Elevation, slope, aspect, curvature, TRI, relative relief |
| `validate_crs(crs_string)` | `bool` | Validates against supported CRS list |

### 7.4 `VegetationService` — NDVI API

**Module:** `services/vegetation_service.py`
**Singleton:** `VEGETATION_SERVICE`

| Method | Returns | Notes |
|--------|---------|-------|
| `get_vegetation_for_sector(sector_id)` | `Dict` | Full NDVI analysis for a named corridor |
| `get_vegetation_for_bbox(min_lat, max_lat, min_lon, max_lon)` | `Dict` | Spatially averaged NDVI for a bounding box |

Both methods always return `"provenance": "[CACHED]"` until a live Sentinel-2 pull
is integrated via the Process API.

---

## 8. Operational Limitations

> [!WARNING]
> The following are hard operational constraints — not temporary software gaps.
> They arise from physics, orbital mechanics, and data latency. They cannot be
> resolved by software changes alone.

### 8.1 No Real-Time InSAR During Rapid Events (< 6 Hours)

**This is a fundamental limitation of repeat-pass satellite InSAR.**

| Constraint | Detail |
|-----------|--------|
| Sentinel-1 repeat cycle | 12 days (orbital mechanics — cannot be reduced) |
| InSAR pair requirement | Two SLC acquisitions separated by ≥ 1 repeat cycle (≥ 12 days) |
| Processing time | Typically 4–8 hours (download + coregistration + unwrap + geocoding) |
| **Minimum event-to-InSAR latency** | **≥ 12 days + 4–8 hours** |

**Consequence:** For a debris flow, cloudburst, or earthquake that triggers slope failure
within minutes to hours, **no Sentinel-1 InSAR measurement is available** during the
emergency response window. The InSAR system provides:
- Pre-event creep velocity baselines (situational awareness before events)
- Post-event change detection (damage mapping after the next satellite pass)

It does **NOT** provide real-time ground displacement measurement during an active event.

This limitation is acknowledged explicitly in the code: when `PARVAT_LIVE_INSAR_PIPELINE`
is inactive, `get_insar_deformation_for_sector()` returns `"status": "SIMULATED_BASELINE"`
with the mandatory notice string.

### 8.2 Coherence Degradation Under Active Conditions

Interferometric coherence drops below the 0.45 operational threshold under:

| Cause | Mechanism |
|-------|-----------|
| Dense vegetation cover | Temporal decorrelation between C-band passes (leaf/branch movement) |
| Heavy rainfall | Surface dielectric change; strong signal scattering |
| Active mass movement | Irreversible surface change between acquisitions |
| Snow / ice cover | Rapid phase transition, volumetric scattering |
| Shadow / layover | Steep terrain: signal-to-noise collapse in foreshortened areas |

In these conditions, `coherence_reliable = False` and `reliability = "LOW"`.
Deformation magnitudes from low-coherence interferograms must not be presented as measurements.

### 8.3 Sentinel-2 Cloud Contamination

Optical NDVI from Sentinel-2 requires cloud-free or partially-cloud-free conditions.
The latest tracked scene has **14.2% cloud cover** — acceptable for corridor-level
analysis but may result in data gaps over specific high-altitude sectors
(above 3,000 m in North Sikkim). No real-time cloud-mask bypass is implemented;
affected pixels fall back to cached 30-day baseline NDVI values.

### 8.4 NISAR S-Band Processing Latency

The NISAR `NISAR_S_BAND_20260820T061015` scene is in `PENDING_UNWRAP` state.
L2 Geocoded Unwrapped Interferogram products from ISRO Bhoonidhi typically have
a 3–5 day latency from acquisition to public availability on the Bhoonidhi portal.
Until the product is released and ingested, NISAR data carries `[SIMULATED]` provenance.

### 8.5 DEM Temporal Currency

The Copernicus GLO-30 / CartoDEM 30 m DEM represents terrain at the time of
original TanDEM-X acquisition (2011–2015). Post-acquisition terrain changes caused by:
- Large mass wasting events (> 1 million m³)
- River channel avulsion (Teesta 2023 GLOF)
- Road construction or bench-terracing on hillslopes

...are **not captured** in the static DEM. For active hazard zones where major slope
failures have occurred (e.g., Singtam, Rangpo post-2023 GLOF), DEM-derived slope
angles may not reflect current terrain geometry. This is flagged by the `[HISTORICAL]`
provenance tag and must be disclosed to operators.

### 8.6 Authentication Dependency for Live Pipeline

The live InSAR pipeline requires all three of the following:

1. `COPERNICUS_CLIENT_ID` and `COPERNICUS_CLIENT_SECRET` set in `.env`
2. `PARVAT_LIVE_INSAR_PIPELINE=1` set in `.env`
3. Network connectivity to `dataspace.copernicus.eu`

Without all three, the system **automatically falls back to `SIMULATED_BASELINE` mode**
with no exception thrown — intentional safe degradation. Operators must verify live
pipeline status before interpreting InSAR outputs quantitatively.

### 8.7 In-Memory Terrain Cache (No Disk Persistence)

`DEMService._cache` is a plain Python `dict` that persists only for the lifetime of
the process. Cache is rebuilt on service restart. For high-load deployments with
frequent point queries, consider externalising the elevation cache to Redis or
pre-computing a full-resolution terrain attribute grid at startup.

---

## 9. Configuration Reference

All satellite and earth observation configuration is managed via environment variables.
See `.env.example` for the full template. **Never commit `.env` with real credentials.**

### 9.1 Satellite / EO Environment Variables

| Variable | Required | Description | Default |
|---------|----------|-------------|---------|
| `COPERNICUS_CLIENT_ID` | For live ingestion | OAuth 2.0 client ID for Copernicus Data Space Ecosystem | _(unset)_ |
| `COPERNICUS_CLIENT_SECRET` | For live ingestion | OAuth 2.0 client secret for Copernicus Data Space | _(unset)_ |
| `SENTINEL_HUB_INSTANCE_ID` | For Sentinel Hub | Instance identifier for band-level Process API queries | _(unset)_ |
| `PARVAT_LIVE_INSAR_PIPELINE` | **Critical** | Set to `1` to activate real interferometric processing pipeline. Any other value or unset → `SIMULATED_BASELINE` mode. | `0` (simulated) |

### 9.2 Operational Mode Variables

| Variable | Description | Default |
|---------|-------------|---------|
| `PAHAD_DEMO_MODE` | `0` = Production Live Priority; `1` = Scenario Walkthrough | `0` |
| `ENVIRONMENT` | `development` / `production` | `development` |
| `PAHAD_ALERT_RADIUS_KM` | Geofence radius for push notification and SAR triggers | `15` |
| `PAHAD_ALERT_DEDUP_MINUTES` | Deduplication window for alert suppression | `30` |

### 9.3 InSAR Engine Constants (Code-Level, Not Env-Configurable)

These constants are defined in `engine/pahad_insar.py` and require code edits to change:

| Constant | Value | Description |
|---------|-------|-------------|
| `COHERENCE_THRESHOLD` | `0.45` | Minimum interferometric coherence for `"HIGH"` reliability |
| `DAYS_PER_YEAR` | `365.25` | Julian year constant for mm/year velocity conversion |
| Tertiary creep velocity threshold | 50 mm/year | Annual velocity above which state = `TERTIARY_CREEP_ACCELERATION` |
| Tertiary creep acceleration threshold | 0.5 mm/day² | Acceleration above which state = `TERTIARY_CREEP_ACCELERATION` |
| Secondary creep velocity threshold | 15 mm/year | Annual velocity above which state = `STEADY_SECONDARY_CREEP` |
| Fukuzono collapse risk threshold | `1/v < 0.1` (v > 10 mm/day) | Imminent failure flag condition |

### 9.4 DEMService Constants (Code-Level)

| Constant | Value | Source Location |
|---------|-------|-----------------|
| `NER_BOUNDS` min/max lat | 20.0°N – 30.0°N | `dem_service.py` lines 34–39 |
| `NER_BOUNDS` min/max lon | 87.0°E – 98.0°E | `dem_service.py` lines 34–39 |
| `SIKKIM_BOUNDS` min/max lat | 26.8°N – 28.2°N | `dem_service.py` lines 42–47 |
| `SIKKIM_BOUNDS` min/max lon | 88.0°E – 89.2°E | `dem_service.py` lines 42–47 |
| Default `delta_deg` for terrain attrs | 0.0003° (≈ 33 m) | `get_point_terrain_attributes()` line 182 |
| Local raster path | `data/geospatial/dem/ner_elevation_30m.tif` | `DEMService.__init__()` line 91 |
| DEM resolution | 30 m | `DEMService.resolution_m` |
| CRS | `EPSG:4326` | `DEMService.crs` |
| Vertical datum | `EGM2008` | `DEMService.vertical_datum` |
| Source string | `"Copernicus GLO-30 / ISRO CartoDEM"` | `DEMService.source` |
| Provenance | `"[HISTORICAL]"` | `DEMService.provenance` |

### 9.5 SAR Tracking Constants (Code-Level)

| Constant | Value | Notes |
|---------|-------|-------|
| `HAZARD_EPICENTER_LAT` | 27.2010° N | NH-10 Km 48 / 29th Mile centroid |
| `HAZARD_EPICENTER_LNG` | 88.5180° E | NH-10 Km 48 / 29th Mile centroid |
| `HAZARD_RADIUS_KM` | 15.0 km | SAR target detection perimeter |
| `DISCONNECT_TIMEOUT_SEC` | 120.0 s | Silence threshold — exceeding this inside hazard zone → `OFFLINE_DISCONNECTED` |
| Distance formula | Haversine (great-circle) | `calculate_haversine_km()` in `sar_tracking.py` |
| Earth radius constant | 6371.0 km | `R_EARTH_KM` in `sar_tracking.py` |

---

## Appendix A — Acquisition Footprint Summary

| Sensor | Scene ID | Footprint (WGS84 Polygon vertices) |
|--------|----------|------------------------------------|
| Sentinel-2A MSI | `S2A_MSIL2A_20260828T044531` | [88.10, 26.90] → [89.15, 26.90] → [89.15, 27.95] → [88.10, 27.95] |
| Sentinel-1A C-SAR | `S1A_IW_SLC__1SDV_20260825T112040` | [88.00, 26.70] → [89.30, 26.70] → [89.30, 28.10] → [88.00, 28.10] |
| ISRO NISAR S-Band | `NISAR_S_BAND_20260820T061015` | [88.20, 26.95] → [89.05, 26.95] → [89.05, 27.80] → [88.20, 27.80] |

## Appendix B — Key Source Files

| Component | File Path |
|-----------|-----------|
| Satellite orchestration service | `services/satellite_service.py` |
| InSAR deformation engine | `engine/pahad_insar.py` |
| DEM terrain service | `services/dem_service.py` |
| Vegetation / NDVI service | `services/vegetation_service.py` |
| SAR Tracking / NDRF Dispatch | `services/sar_tracking.py` |
| Environment configuration template | `.env.example` |

## Appendix C — Creep State Decision Matrix

```
Input: v_annual (mm/year), a (mm/day²)

v_annual > 50 OR a > 0.5
    └── TERTIARY_CREEP_ACCELERATION
        └── A_insar = 0.80 + 0.20 × min(a/1.0, 1.0)
        └── If 1/v < 0.1 → fukuzono_collapse_risk = TRUE

v_annual > 15 (and not above)
    └── STEADY_SECONDARY_CREEP
        └── A_insar = 0.40 + 0.38 × min((v_annual-15)/35, 1.0)

Otherwise
    └── BASE_STABLE_OR_SETTLING
        └── A_insar = 0.35 × min(v_annual/15, 1.0)
```

---

*Document generated: 2026-09-09 | PARVAT NETRA / PAHAD AI Core Engineering Team | SIH 26001*
*All facts sourced directly from production codebase. No values fabricated.*
*File: `docs/PAHAD_SATELLITE_ARCHITECTURE.md` | Project root: `silly-fermi/`*
