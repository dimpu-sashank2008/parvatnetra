# PARVAT NETRA — Architecture & Engineering Specification

> **Mission:** "See the risk. Act before the disaster."  
> **Classification:** SIH-Grade Multi-Hazard Disaster Intelligence Platform (NER Sentinel)  
> **Paradigm:** Predict → Detect → Explain → Warn → Prioritise → Respond → Recover

---

## 1. Executive Summary & Core Technical Differentiator

The core technical differentiator of **PARVAT NETRA** is **Multimodal Evidence Fusion**. Rather than relying solely on precipitation thresholds or black-box machine learning models, PARVAT NETRA correlates physical slope mechanics with environmental, satellite, sensor, and optical telemetry:

```
+---------------------------------------------------------------------------------------+
|                                EXTERNAL DATA SOURCES                                  |
|  Rainfall (IMD) | Weather (ECMWF) | InSAR (Sentinel) | Geotech Sensors | Optical CCTV |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                               FASTAPI INGESTION ENGINE                                |
|  - Rate limiting & idempotency check                                                  |
|  - Normalization into GeoJSON / Sensor Timeseries                                     |
|  - Telemetry anomaly pre-filtering                                                    |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                         POSTGRESQL + POSTGIS SPATIAL STORE                            |
|  - High-precision DEM & elevation contours                                            |
|  - Critical infrastructure exposures (roads, bridges, schools, hospitals)             |
|  - Time-series observation tables                                                     |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                               FEATURE GENERATION ENGINE                               |
|  - Antecedent Precipitation Index (API 24h/72h)                                       |
|  - Pore-water pressure gradient (dP/dt)                                               |
|  - Ground displacement velocity (InSAR mm/yr + Inclinometer mm)                       |
|  - Optical mudflow / tension crack detection confidence                               |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                    PHYSICS-INFORMED AI + MULTIMODAL EVIDENCE FUSION                   |
|  - Infinite Slope Factor of Safety (FoS = Resisting Forces / Driving Forces)          |
|  - Gradient-Boosted Spatio-Temporal Landslide Susceptibility ML                       |
|  - Bayesian Belief Network (BBN) / Dempster-Shafer Fusion                             |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                              SYNTHESIS & EXPLAINABILITY                               |
|  - Fused Risk Score (0 - 100)                                                         |
|  - Dynamic Threat Level: WATCH | ALERT | WARNING | EVACUATE                           |
|  - "Why" Explainability Breakdown (SHAP / Contribution percentages)                   |
|  - Actionable Mitigation Directives                                                   |
+---------------------------------------------------------------------------------------+
                                           |
                      +--------------------+--------------------+
                      |                                         |
                      v                                         v
+-------------------------------------------+ +-----------------------------------------+
|            CITIZEN EXPERIENCE             | |          AUTHORITY EXPERIENCE           |
|  - Live Risk Map & Alert Banners          | |  - Emergency Operations Control Room    |
|  - Safe Route Navigation (Hazard-Aware)   | |  - Multimodal Evidence Deep-Dive Panel  |
|  - SOS / Hazard Reporting                 | |  - Road Closures & Response Dispatch   |
|  - Multilingual AI Audio/Visual Assistant | |  - Infrastructure Exposure Analysis     |
|  - Offline-ready Village Warning Cards    | |  - Recovery Task Tracking & Audit Logs  |
+-------------------------------------------+ +-----------------------------------------+
```

---

## 2. MCP Integration vs External Application APIs

To ensure clean system architecture and avoid creating unnecessary MCP bloat, PARVAT NETRA strictly decouples development tools from application runtime services:

### Agent MCP Integrations (Antigravity IDE Tooling)
These tools assist the AI agent during development:
1. **StitchMCP**: Rapid UI screen generation and design system exploration.
2. **Figma MCP**: Inspects layout tokens, spacing grids, and component hierarchies.
3. **Spline MCP**: Interactive 3D high-altitude mountain terrain scenes.
4. **GitHub MCP**: Pull requests, commits, and branch operations via Node.js (`npx`).
5. **Neon MCP**: Direct PostgreSQL / PostGIS branch management and schema exploration.
6. **Chrome DevTools MCP**: Automated end-to-end browser testing, DOM inspection, and Core Web Vitals profiling.
7. **Cloud Run MCP**: Container deployment orchestration.

### External Application APIs (FastAPI Backend Consumption)
External services are consumed as standard REST/WebSocket/MQTT APIs by the application backend:
* **IMD / OpenWeather / ECMWF**: Weather and rainfall forecasts.
* **Sentinel Hub / Copernicus**: Satellite SAR & optical multispectral imagery.
* **Mapbox / Google Maps Platform**: Geocoding, vector tile rendering, and routing.
* **IoT Gateways**: In-situ borehole tiltmeters, piezometers, and rain gauges.
* **Notification Providers**: SMS Gateways, Slack webhooks, and SMTP alert dispatch.

---

## 3. Database Foundation (PostgreSQL + PostGIS)

The core relational and spatial schema is structured into the following decoupled domains:

### Domain 1: Identity & Access Control
- `users`: ID, email, hashed_password, full_name, phone_number, role (`CITIZEN`, `FIELD_RESPONDER`, `DISTRICT_OFFICER`, `STATE_DISASTER_ADMIN`), created_at.
- `roles_permissions`: Granular role capability matrix.

### Domain 2: Geographic & Exposure Infrastructure
- `spatial_zones`: ID, zone_code (e.g. `UK-CHM-04`), name, boundary (PostGIS `GEOMETRY(Polygon, 4326)`), slope_mean, geology_class, soil_depth.
- `exposure_assets`: ID, zone_id, asset_type (`ROAD`, `BRIDGE`, `HOSPITAL`, `SCHOOL`, `VILLAGE`, `POWER_STATION`), name, location (`GEOMETRY(Point/LineString, 4326)`), capacity_or_length, vulnerability_weight.
- `road_network`: ID, highway_name, segment_code, geom (`GEOMETRY(LineString, 4326)`), current_status (`OPEN`, `RESTRICTED`, `CLOSED`), alternate_detour_id.

### Domain 3: Telemetry & Ingested Observations
- `sensor_stations`: ID, station_code, location (`GEOMETRY(Point, 4326)`), altitude_m, status, last_heartbeat.
- `sensor_readings`: ID, station_id, timestamp, pore_water_pressure_kpa, soil_moisture_pct, tilt_x_deg, tilt_y_deg, vibration_rms_g.
- `rainfall_records`: ID, station_id, timestamp, rainfall_1h_mm, rainfall_24h_mm, rainfall_72h_mm.
- `satellite_passes`: ID, satellite_name (`SENTINEL-1`, `SENTINEL-2`), pass_date, insar_displacement_mm_yr, ndvi_mean, raw_tiff_url.
- `camera_detections`: ID, camera_id, timestamp, surface_displacement_detected (bool), debris_flow_prob, snapshot_url.

### Domain 4: Risk Assessment & Evidence Fusion
- `risk_assessments`: ID, zone_id, timestamp, fused_risk_score (0-100), factor_of_safety, ml_probability, threat_level (`WATCH`, `ALERT`, `WARNING`, `EVACUATE`), data_mode (`LIVE`, `SIMULATED`, `DEMO`, `HISTORICAL`).
- `evidence_records`: ID, assessment_id, modality (`RAINFALL`, `GEOTECH`, `INSAR`, `VISION`, `PHYSICS`, `CITIZEN`), weight, evidence_summary, metrics_json.

### Domain 5: Operations, Alerts & Recovery
- `alerts`: ID, assessment_id, severity, title, advisory_text, broadcast_status, dispatched_channels, issued_at.
- `citizen_reports`: ID, user_id, location (`GEOMETRY(Point, 4326)`), report_type (`CRACKS`, `ROCKFALL`, `MUD_SPRING`, `RIVER_BLOCKAGE`), photo_url, verification_status.
- `response_teams`: ID, team_code, unit_type (`NDRF`, `SDRF`, `MEDICAL`, `PWD`), active_zone_id, current_status.
- `damage_assessments`: ID, incident_id, road_km_damaged, structures_affected, casualty_estimate, verified_by_id.
- `recovery_tasks`: ID, incident_id, task_name, department (`BRO`, `DISASTER_MGMT`, `HEALTH`), priority, status (`PENDING`, `IN_PROGRESS`, `COMPLETED`).
- `audit_logs`: ID, actor_id, action, target_table, record_id, timestamp, ip_address.

---

## 4. Safe Routes Engine Specification

Safe routing is a critical life-safety system component.

### Route Computation Modes
1. **FASTEST**: Optimizes purely for travel duration on open roadways.
2. **SHORTEST**: Minimizes physical kilometer distance.
3. **SAFEST**: Multi-criteria Dijkstra / A* cost optimization factoring:
   $$\text{Edge Cost} = \text{Distance} \times \left(1 + \omega_1 \cdot \text{Landslide Risk} + \omega_2 \cdot \text{Slope Hazard} + \omega_3 \cdot \text{Active Rainfall}\right) + \text{Penalty}_{\text{Restricted Road}}$$

### Strict Frontend Interaction Guarantees
* Selecting a route card highlights the specific path on the vector map without redrawing or clearing base layers.
* The detailed Route Drawer opens smoothly showing turn-by-turn alerts, hazard proximity warnings, and elevation gradients.
* "Start Navigation" transitions into an active, high-contrast tracking mode.
* **No blank screens or dead timeouts**: If external routing APIs (Mapbox/Google) are unavailable or unconfigured, the engine seamlessly falls back to pre-calculated geometric road network graphs with PostGIS `ST_MakeLine`.

---

## 5. Flagship Scenario: Incident A-17

Incident **A-17** is the reference testbed validating end-to-end evidence fusion along National Highway 58 / Rishikesh-Badrinath Corridor:

| Timeline Step | Subsystem Observation | Data Modality | State Transition |
| :--- | :--- | :--- | :--- |
| **T0: Baseline** | Normal monsoon precipitation (8 mm/h), slope dry | Baseline Sensors | `WATCH (Score: 18)` |
| **T+2h: Heavy Rain** | Cloudburst event: 48 mm/h rainfall; 72h accumulation reaches 142 mm | Rainfall Gauge / IMD | `WATCH (Score: 38)` |
| **T+4h: Saturation** | Soil moisture reaches 84%; Piezometer pore pressure spikes from 12 kPa to 48 kPa | Geotechnical In-situ | `ALERT (Score: 59)` |
| **T+6h: Deformation** | Borehole inclinometer detects 18 mm shear displacement; InSAR indicates -32 mm/yr velocity | Inclinometer + InSAR | `ALERT (Score: 74)` |
| **T+7h: Physical Instability** | Infinite slope Factor of Safety (FoS) drops to 0.98 (Failure imminent) | Physics Engine | `WARNING (Score: 88)` |
| **T+7.5h: Optical Confirmation** | Roadside optical CCTV detects tension cracks widening across the road shoulder | Computer Vision | `EVACUATE (Score: 96)` |
| **T+8h: Multi-Agency Action** | Automatic emergency broadcast sent to citizen app; NH-58 closed; Traffic rerouted to Safest Bypass; NDRF team dispatched | Authority Dispatch | `RESPONSE ACTIVE` |
| **T+24h: Recovery** | Post-slide drone ortho-mosaic calculates 3,400 $m^3$ debris; BRO debris clearance task created | Drone + Damage Assessment | `RECOVERY` |

---

## 6. Design System & Visual Style Guide

PARVAT NETRA adheres to a **National Emergency Operational Standard**:
* **Theme**: Deep obsidian dark mode (`#070B10` to `#0F172A`) with high-legibility slate typography (`Inter`, `JetBrains Mono` for telemetry).
* **Color Hierarchy**:
  * `EVACUATE / CRITICAL`: Signal Crimson (`#EF4444`)
  * `WARNING / HIGH`: Solar Amber (`#F59E0B`)
  * `ALERT / MODERATE`: Signal Gold (`#EAB308`)
  * `WATCH / STABLE`: Emerald Cyan (`#10B981`)
  * `OPERATIONAL ACCENT`: Tactical Slate Blue (`#3B82F6`)
* **Prohibited Visual Tropes**: No purple neon gradients, no decorative glassmorphism, no fake sci-fi HUDs, no decorative AI sparkles. Every element serves an operational purpose.

---

## 7. Data Honesty & Integrity Protocol

Every single data field rendered in PARVAT NETRA UI must display its provenance banner:
* `[LIVE]`: Ground-truth authenticated API/sensor feed.
* `[SIMULATED]`: Statistically realistic physics simulation based on historical rainfall datasets.
* `[HISTORICAL]`: Archival ground truth from GSI (Geological Survey of India) landslide inventory.
* `[DEMO]`: Synthetic walkthrough sequence for evaluator inspection.
