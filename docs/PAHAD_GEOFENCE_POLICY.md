# PARVAT NETRA / PAHAD AI — Spatial Geofence Policy & Impact Zone Specification

**Document Version:** 1.0  
**Phase:** 3.5 — 15 km Geofencing & Spatial Eligibility Engine  
**Classification:** Disaster-Intelligence Operational Standard  
**Standard:** Smart India Hackathon (SIH) Grade  

---

## 1. Objective & Operational Scope

In mountainous terrain, landslide impacts are not confined to the rupture scarp. Debris flows, river damming, outburst floods (GLOF / LDOF), and highway corridor severed access propagate risk kilometers downstream and upstream.

PARVAT NETRA establishes an operational **15 km Default Geofence Policy** (configurable via `PAHAD_ALERT_RADIUS_KM`) to define the spatial boundary for emergency alert delivery, evacuation staging, and civil defense resource mobilization.

> **Operational Note**: The 15 km radius is a configurable SIH demonstration policy and operational starting standard for major Himalayan arterial corridors (e.g., NH-10). It is dynamically adjustable based on local topography, river basin geometry, and administrative directives.

---

## 2. Geometry Support

The Geofence Engine (`engine/pahad_geofence.py`) natively resolves three distinct geometry paradigms:

| Geometry Type | Representation | Primary Operational Application | Core Proximity Threshold |
| :--- | :--- | :--- | :--- |
| **Point (Radial Circle)** | $[lat, lon] + r$ (km) | Isolated slope failures, quarry collapses, single sensor clusters | $d \le 3.0$ km (Direct), $d \le 15.0$ km (Buffer) |
| **Corridor (Buffered Line)** | Array of $[lat, lon] + b$ (km) | Mountain highways (NH-10, NH-717A), rail corridors (Sevoke-Rangpo) | $d \le 2.0$ km (Direct), $d \le 15.0$ km (Buffer) |
| **Polygon (Catchment)** | Closed vertex ring $+ b$ (km) | GSI High Susceptibility Zones, Teesta river catchments, town borders | Inside polygon (Direct), $d \le 15.0$ km (Buffer) |

---

## 3. Spatial Zone Categorization

Recipients inside candidate registries are categorized into three operational distance bands:

1. **`IMPACT_DIRECT`**:
   - **Point**: Distance from epicenter $\le 3.0$ km.
   - **Corridor**: Distance from nearest highway waypoint $\le 2.0$ km.
   - **Polygon**: Geographically enclosed inside the polygon boundary.
   - **Operational Action**: Immediate tactical evacuation, road closure, acoustic civil defense siren trigger.

2. **`BUFFER_ZONE`**:
   - Distance from epicenter/corridor between Direct threshold and $15.0$ km (or `PAHAD_ALERT_RADIUS_KM`).
   - **Operational Action**: Pre-cautionary advisory, SMS/push notification, traffic diversion onto secondary BRO corridors (e.g. NH-717A via Lava/Algarah).

3. **`OUTSIDE`**:
   - Distance exceeds $15.0$ km.
   - **Operational Action**: Suppressed from push and SMS emergency dispatch to avoid alert fatigue and network congestion.

---

## 4. Mathematical Geodesic Implementation

Distance calculations use the Haversine formula for spherical great-circle distance:

$$d = 2 R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

where:
- $R = 6371.0$ km (mean volumetric Earth radius).
- $\phi_1, \phi_2$ are latitudes in radians.
- $\Delta\phi = \phi_2 - \phi_1$, $\Delta\lambda = \lambda_2 - \lambda_1$ are coordinate deltas.

For Polygon containment checks, the system leverages `shapely.geometry.Polygon.contains()` with equirectangular projected coordinates for high performance and sub-millisecond execution.

---

## 5. Zero-PII Spatial Privacy

To ensure citizen and field personnel privacy:
1. Recipient coordinates are stored only in volatile in-memory registries or encrypted PostGIS tables.
2. The spatial evaluation returns candidate IDs and distance values without exposing coordinates to public APIs or frontend DOM elements.
3. The frontend Notification Center and SIH Evaluator dashboards display only aggregate counts (`Total in Zone`, `Authorities`, `Field Teams`, `Push Eligible`, `SMS Eligible`).
