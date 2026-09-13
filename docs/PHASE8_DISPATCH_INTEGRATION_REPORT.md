# PARVAT NETRA / PAHAD AI — PHASE 8: DISPATCH INTEGRATION REPORT
**Geofencing, Field Inspection Tasking, and Multi-Profile Evacuation Routing**
*Pilot Corridor: NH-10 KM 48 (29th Mile, Pakyong District, Sikkim)*
*Date: 2026-09-11 | Authority: Emergency Operations Center & Border Roads Organisation (BRO)*

---

## 1. 15 km Public Safety Geofence Assessment (Checkpoint 8-06)
For every corroborated incident candidate, the EOC calculates a dynamic geodesic safety buffer around the slope instability epicenter:
- **Center Coordinates**: $27.3300^\circ\text{N}, 88.6100^\circ\text{E}$ (NH-10 KM 48, 29th Mile Sector).
- **Geodesic Method**: Haversine great-circle calculation using Earth mean radius $R = 6371.0\,\text{km}$.
- **Geofence Geometry**: 16-point closed polygon approximation for vector mapping.

### Intersected Settlement Entities
| Settlement Name | Distance (km) | District | Population Exposed |
| :--- | :---: | :--- | :---: |
| **29th Mile Settlement** | 0.00 | Pakyong | 850 |
| **Singtam Bazaar** | 15.12 | Gangtok | 6,500 |
| **Rangpo Border Town** | 18.94 | Pakyong | 10,200 |
| **Rorathang Village** | 14.51 | Pakyong | 2,400 |
| **Dikchu Hydel Colony** | 11.20 | North Sikkim | 1,900 |

- **Total Direct Exposed Population within 15 km**: 5,150 residents.
- **Monitored Lifeline Roads Intersected**:
  1. `NH-10 (Sikkim Lifeline)`: KM 48 chokepoint (Criticality: HIGH_LIFELINE).
  2. `NH-717A (Strategic BRO Bypass)`: KM 65 alternate corridor (Criticality: STRATEGIC_BYPASS).
  3. `Rongli-Rorathang Road`: Secondary civilian evacuation route.
  4. `Dikchu-Gangtok Highway`: Northern feeder link.

---

## 2. Field Team Ground Inspection Tasking (Checkpoint 8-16)
Ground truth validation provides the essential physical corroboration before statutory alert approval:
- **Task Entity Schema**: `task_id`, `incident_id`, `team`, `priority`, `target`, `coordinates`, `deadline`, `routing_profile`, `instructions`, `status`, `evidence`.
- **Lifecycle States**:
  $$\text{CREATED} \to \text{ASSIGNED} \to \text{EN\_ROUTE} \to \text{ON\_SITE} \to \text{VERIFIED} \to \text{RETURNED} \quad (\text{or } \text{CANCELLED})$$

### Field Evidence Verification Protocol
Field operators (BRO / SDRF Quick Reaction Units) inspect the slopes and submit structured evidence:
- GPS verification coordinates.
- Tension crack aperture measurements (mm).
- Slope movement / toe bulge observations.
- Road crown subsidence and culvert blockage state.
- High-resolution photographic/video references.
- Ground truth status: `GROUND_TRUTH_CONFIRMED` or `NO_DEFORMATION`.

Submission of positive evidence automatically advances the parent incident to `STATE_AUTHORITY_REVIEW`.

---

## 3. Multi-Profile Tactical Routing Integration (Checkpoint 8-17)
The EOC integrates `services/offline_routing_service.py` to calculate and compare three distinct route options between staging depots (BRO KM 48 Staging) and chokepoints or evacuation relief shelters:

| Routing Profile | Distance (km) | ETA (min) | Hazard Penalty Exposure | Strategic Application |
| :--- | :---: | :---: | :---: | :--- |
| **FASTEST** | 4.2 | 10.0 | Moderate | Rapid quick-reaction team initial reconnaissance |
| **SHORTEST** | 3.8 | 14.0 | Elevated (transits chokepoint) | Local light emergency personnel transit |
| **SAFEST** | 5.8 | 18.0 | Minimal (steers clear of slip zone) | Heavy relief convoys, ambulance evacuation, public detour |

### Detour & Chokepoint Severance Resilience
When NH-10 KM 48 is severed by mudflow or rockfall, the router dynamically adds a severe cost penalty to the blocked road segment, automatically re-routing all traffic via the BRO NH-717A corridor without human routing intervention.
If all bridges and road links are severed, the router returns `status: UNREACHABLE` to alert EOC commanders to mobilize air rescue (NDRF/IAF choppers).
