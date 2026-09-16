# PARVAT NETRA / PAHAD AI — PHASE 12: GIS HAZARD MAP ANIMATION UPGRADE
## Operational Visual Intelligence & Temporal Evolution Engineering Report

**Platform:** PARVAT NETRA (NER Sentinel)  
**System:** PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Subsystem:** Geospatial Information System (GIS) Dynamic Hazard Layer  
**Phase:** 12 — Visual Intelligence Enhancement  
**Status:** COMPLETED & VERIFIED (Zero Regressions)  
**Date:** September 2026  
**Authority:** Ministry of Development of North Eastern Region (MDoNER) / NDMA Grade  

---

### Executive Summary

The Phase 12 GIS Hazard Map Animation Upgrade transforms the static corridor visualization into a dynamic, temporal hazard evolution engine. The enhanced map visibly and defensibly answers four core operational questions for emergency responders and tactical commanders:

1. **WHERE is the hazard?** — Pinpointed on the canonical North Eastern Region (NER) corridor network with georeferenced halo extents (250m to 1400m).
2. **HOW severe is it?** — Rendered through authoritative 5-tier CRI risk bands (LOW, MODERATE, HIGH, VERY HIGH, EXTREME) coupled with Mohr-Coulomb Factor of Safety (FoS).
3. **HOW is the hazard changing?** — Illustrated via smooth temporal evolution scrubbers, multi-step playback controls, and calibrated physical saturation progressions (T-24h -> T-12h -> T-6h -> NOW).
4. **WHY is it changing?** — Transparent modal inspectability revealing real-time contributing drivers (cumulative precipitation, pore-water pressure, antecedent moisture, slope gradient).

Crucially, this upgrade **strictly preserves scientific and operational invariants**:
- **Zero Synthetic Live Data:** Live mode displays strictly authentic real-time telemetry ([LIVE] / [LIVE / DETERMINISTIC]).
- **Separation of Modes:** Physics-calibrated failure simulations are explicitly badged [SIMULATED]; archival ground-truth replays are badged [HISTORICAL].
- **Alert Safety Invariant:** Temporal playback and scenario drills **never** trigger audible sirens, public SMS alerts, or Common Alerting Protocol (CAP) dispatches. The statutory 2-of-3 multi-signal corroboration heuristic remains unaltered.
- **Scientific Fidelity:** CRI formulas, Mohr-Coulomb infinite slope equations, and GBDT model weights are completely unchanged.

---

### 1. Architecture & Component Decomposition

`
+-----------------------------------------------------------------------------------+
|                            PARVAT NETRA BACKEND PIPELINE                          |
|  Canonical Corridor Registry (26 Corridors) -> pahad_gis_animation.py            |
|  Live Telemetry + Physical FoS Engine       -> GET /api/pahad/temporal-risk       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         LEAFLET FRONTEND VISUALIZATION                            |
|  PahadGisAnimationController (pahad_gis_animation.js)                             |
|  - Dedicated Leaflet Pane: 'pahadHazardAnimationPane' (z-index: 380)              |
|  - Outer Dynamic Halo Circle (Monotonic Scaling, Pulse CSS Keyframes)             |
|  - Inner Epistemic Core Circle (Precision Centroid Anchor)                        |
|  - Timeline Scrubber Widget (#pahad-gis-timeline-control, Mode Switcher)         |
|  - Click-to-Explain Modal Popup (Telemetry & Contributing Signals)                |
+-----------------------------------------------------------------------------------+
`

#### 1.1 Backend Engine (engine/pahad_gis_animation.py)
- get_corridor_temporal_risk(corridor_id, mode): Primary entry point handling live, scenario, and historical execution pathways.
- compute_visual_parameters(cri, fos): Monotonically scales visual dimensions:
  * Radius: 300m + 11.0 * CRI (clamped 250m - 1400m)
  * Opacity: 0.20 + 0.0045 * CRI (clamped 0.18 - 0.65)
  * Pulse Rate: None (<30 CRI), 8.0s (30-50 CRI), 3.8s (50-75 CRI), 2.0s (>=75 CRI)
- cri_to_risk_band(cri): Maps CRI [0, 100] to the official 5-tier NDMA/MDoNER operational bands.
- list_animated_corridors(): Returns all 26 canonical corridors across all 8 NER states.

#### 1.2 REST API (pp.py)
- GET /api/pahad/temporal-risk:
  * Accepts corridor_id / sector_id and mode query parameters.
  * Returns complete metadata, current risk state, temporal step sequences, dynamic halo geometry, and top contributing drivers.
  * Fail-safe error handling returning structured JSON with HTTP 200, 404, or 500 status codes.

#### 1.3 Client Controller (static/js/pahad_gis_animation.js)
- **Pane Isolation**: Allocates Leaflet pane pahadHazardAnimationPane with z-index: 380, positioning it above polygon choropleths (z=200) and basemaps (z=200) but beneath vector road polylines (z=400) and operational incident markers (z=600).
- **Layer Reuse**: Maintains persistent Leaflet L.circle instances for both the outer halo and inner core. Updates in-place via setLatLng(), setRadius(), and setStyle(), avoiding DOM thrashing or memory leaks.
- **Corridor Synchronization**: Hooks into window.onCorridorSelectionChanged so that selecting a sector from the sidebar, dropdown, or map immediately updates the temporal animation context.

---

### 2. Operational Modes & Data Honesty (Rule 16 Compliance)

| Operational Mode | Provenance Badge | Description | Trigger / Source | Public Dispatch Safety |
| :--- | :--- | :--- | :--- | :--- |
| **LIVE NOW** | [LIVE] or [LIVE / DETERMINISTIC] | Real-time operational snapshot. Represents current physical slope equilibrium and latest telemetry. | IMD AWS telemetry, in-situ piezometers, live inference pipeline | Normal SOP with strict 2-of-3 confirmation |
| **SCENARIO DRILL** | [SIMULATED] | Multi-temporal failure scenario illustrating 24-hour progressive slope saturation and collapse under monsoon conditions (T-24h -> T-12h -> T-6h -> NOW). | Calibrated infinite-slope physical equations | **Siren/CAP Dispatches Suppressed** |
| **HISTORICAL** | [HISTORICAL] | Playback of documented archival landslide event sequence from GSI/NRSC repository. | Documented historical ground truth records | **Siren/CAP Dispatches Suppressed** |

---

### 3. Visual & Accessibility Standards

#### 3.1 Color & Contrast Compliance (WCAG 2.1 AA)
The palette strictly follows the PARVAT NETRA Obsidian Slate operational aesthetic:
- **EXTREME RISK** (CRI >= 75, FoS < 1.0): Crimson Red (#dc2626)
- **VERY HIGH RISK** (CRI 65-74, FoS < 1.15): Dark Orange (#ea580c)
- **HIGH RISK** (CRI 50-64, FoS < 1.30): Amber Orange (#f97316)
- **MODERATE RISK** (CRI 30-49, FoS >= 1.30): Amber Yellow (#eab308)
- **LOW RISK** (CRI < 30, FoS >= 1.50): Emerald Green (#10b981)

Every visual color indicator is paired with unambiguous alphanumeric labels (EXTREME, HIGH, LOW) and numeric readouts (CRI: 89.5, FoS: 0.764) to guarantee readability for color-deficient users.

#### 3.2 Motion Accessibility (prefers-reduced-motion)
CSS animations for halo pulsing include @media (prefers-reduced-motion: reduce) media queries that immediately disable all pulsating keyframes, falling back to clean static borders and opacities.

#### 3.3 Responsive Adaptability
- **Desktop (>1024px):** Timeline control sits neatly at ottom-3 left-4, allowing full view of corridor road networks and camera feeds.
- **Tablet (768px - 1023px):** Compact scrubber with responsive button text and wrapped legend items.
- **Mobile (<768px):** Widget dynamically scales (max-w-[340px] w-[calc(100%-24px)]), avoiding map attribution overlap and touch-target conflicts.

---

### 4. Verification & Testing Matrix

The GIS Hazard Animation engine has been subjected to comprehensive automated testing:
- **GIS Hazard Animation Engine:** 	ests/test_gis_hazard_animation.py -> **14 / 14 PASSED**
- **NER Default GIS View:** 	ests/test_ner_gis_default_view.py -> **10 / 10 PASSED**
- **UI Theme & Corridor Integration:** 	ests/test_ui_theme_and_corridor.py -> **8 / 8 PASSED**
- **Model & Pipeline Regression:** 	ests/test_model_regression.py -> **4 / 4 PASSED**
- **Full Pytest Regression Suite:** 127 total tests -> **127 / 127 PASSED**
- **Phase 11F Operational Harness:** scripts/phase11f_e2e_verification.py -> **29 / 29 Checkpoints PASSED**
- **DevTools Browser Diagnostics:** Chrome DevTools MCP -> **0 JavaScript Errors**

---

### 5. Verified File Manifest

1. engine/pahad_gis_animation.py - Temporal hazard animation calculations, dynamic halo scaling, and scenario generation.
2. pp.py (Lines 5923-5947) - REST endpoint GET /api/pahad/temporal-risk.
3. static/js/pahad_gis_animation.js - Frontend Leaflet controller, dedicated pane, layer reuse, timeline UI, and click-to-explain modal.
4. public/static/js/pahad_gis_animation.js - Synced client asset for public distribution.
5. 	emplates/index.html - Script inclusion, corridor event hooking, and accessible 5-tier risk & 4-tier provenance map legend.
6. 	ests/test_gis_hazard_animation.py - Dedicated 14-test verification suite.
7. docs/PHASE12_GIS_HAZARD_ANIMATION_REPORT.md - Operational documentation.
