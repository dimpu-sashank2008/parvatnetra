# PARVAT NETRA / PAHAD AI — PHASE 9E REPORT
## Final Government-Style Visual Redesign & Live Risk Selection

**Authority:** Ministry of Development of North Eastern Region (MDoNER) / National Disaster Management Authority (NDMA)  
**Standard:** Guidelines for Indian Government Websites (GIGW 3.0) & National Institute of Disaster Management (NIDM)  
**System:** PARVAT NETRA — NER Sentinel (PS 26001)  
**AI Core:** PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Date:** September 11, 2026  
**Status:** **OPERATIONAL & VERIFIED**

---

### 1. Executive Summary
Phase 9E delivers the final government-grade visual redesign of the PARVAT NETRA / PAHAD AI platform, transforming the primary homepage from a cluttered engineering workbench into an authoritative, distraction-free **PAHAD AI Risk Prediction** interface that an official or evaluator can read and comprehend within **5 seconds**.

The redesign establishes:
1. **GIGW 3.0 Compliant Clean Visual Architecture**: All secondary GIS layers, raw sensor databases, and administrative incident queues are strictly compartmentalized into dedicated sidebar workspaces.
2. **Strict Black-Only Visual Palette**: Deep obsidian canvas (`#050505`), charcoal header (`#0A0A0A`), modular cards (`#111111`), inner inputs (`#171717`), and structural borders (`#222222`, `#262626`, `#2D2D2D`). Blue dominant background colors are eliminated, and chromatic colors are reserved solely for hazard communication.
3. **Dynamic Highest-Risk Default on Load**: The system queries `/api/pahad/highest-risk-corridor` on startup and sets the default assessment corridor to the corridor with the highest Composite Risk Index (CRI) across all 26 canonical corridors (currently `ML-SONAPUR-01` with CRI 40.6 and FoS 0.926, Meghalaya), rather than a hardcoded location.
4. **Multi-Corridor Selection & Instant Value Wiping**: Selecting any corridor immediately wipes prior values with an `EVALUATING...` loading state, retrieves real-time geotechnical telemetry, updates CRI, FoS, rainfall, risk level, and explanations, and smoothly animates values via Anime.js.
5. **Strict 6-Category Sidebar Navigation**: Re-architected into 1. PAHAD AI, 2. MAP, 3. FIELD, 4. EOC, 5. RESPONSE, 6. SYSTEM, removing any visible references to legacy recurrence or archive buttons.
6. **Physical & Statutory Safety Integrity**: Infinite slope Mohr-Coulomb mechanics ($FoS$), 2-of-3 independent sensor corroboration, and statutory District Magistrate sign-off under the Disaster Management Act (DMA) 2005 remain unconditionally enforced.

---

### 2. The 9-Step Clean Prediction Hierarchy
The redesigned homepage (`#view-prediction`) strictly answers four core operational questions:
* **Where is the risk?**
* **How high is it?**
* **Why is it elevated?**
* **What should the authority do?**

```
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 1: INSTITUTIONAL HEADER (NDMA • MDoNER • GIGW 3.0 Tricolor Accent)   │
├──────────────────────────────────────────────────────────────────────────┤
│ STEP 2: LOCATION ASSESSMENT (State, District, Corridor Cascading Picker) │
│         Sonapur Tunnel NH-06 Portal Scarp • East Jaintia Hills, Meghalaya│
├────────────────────────────────────┬─────────────────────────────────────┤
│ STEP 3: LARGE CRI CENTERPIECE      │ STEP 5: SHORT EXPLANATION (WHY)     │
│         40.6 / 100 Conic Ring      │         Rainfall Loading + FoS 0.926│
│                                    │         Non-Causal Drivers (Max 3)  │
├────────────────────────────────────┼─────────────────────────────────────┤
│ STEP 4: RISK LEVEL BADGE           │ STEP 6: KEY EVIDENCE (4 Cards)      │
│         [HIGH RISK]                │         FoS | Rain | ML | Seismic   │
├────────────────────────────────────┴─────────────────────────────────────┤
│ STEP 7: RECOMMENDED ACTION PROTOCOL                                      │
│         [Stage 2] AI Recommendation vs [Stage 3] Magistrate Sign-Off     │
├──────────────────────────────────────────────────────────────────────────┤
│ STEP 8: GEOGRAPHIC FOOTPRINT MINI-MAP (Context Coordinates + GIS Link)   │
├──────────────────────────────────────────────────────────────────────────┤
│ STEP 9: PROVENANCE & TIMESTAMPS ([HYBRID FUSION] • Updated: Live)         │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Strict Black-Only Visual System
In accordance with SIH / NIDM national emergency design standards, the UI was purged of consumer dark-blue tints and standardized onto a high-contrast charcoal hierarchy:

| Token | Hex Value | Semantic Usage |
| :--- | :--- | :--- |
| `--bg-canvas` | `#050505` | Master viewport canvas (Never white) |
| `--bg-header` | `#0A0A0A` | Institutional national portal header & ribbons |
| `--bg-card` | `#111111` | Primary prediction cards and modular surfaces |
| `--bg-subcard` | `#171717` | Input select controls, nested metric boxes, table rows |
| `--border-subtle` | `#222222` | Card separators and subtle grid lines |
| `--border-card` | `#262626` | Card outer frames |
| `--border-element` | `#2D2D2D` | Input borders and interactable component outlines |
| `--text-heading` | `#FFFFFF` | Primary metrics, values, and institutional titles |
| `--text-body` | `#E5E5E5` | Explanations, advisories, and corridor descriptions |
| `--text-muted` | `#A3A3A3` | Secondary labels, units, and signal agreements |
| `--text-subtle` | `#737373` | Disclaimers, technical metadata, and timestamps |

#### Restricted Hazard Accent Palette:
Colors are strictly forbidden for decorative styling and only appear where communicating hazard thresholds:
* **LOW**: `#16a34a` (text: `#4ade80`, bg: `rgba(22, 101, 52, 0.25)`)
* **MODERATE**: `#d97706` (text: `#fbbf24`, bg: `rgba(180, 83, 9, 0.25)`)
* **HIGH**: `#ea580c` (text: `#fb923c`, bg: `rgba(194, 65, 12, 0.25)`)
* **VERY HIGH**: `#dc2626` (text: `#f87171`, bg: `rgba(185, 28, 28, 0.3)`)
* **EXTREME**: `#b91c1c` (text: `#fca5a5`, bg: `rgba(185, 28, 28, 0.5)`)

#### High-Contrast & Light Mode Neutralization:
To guarantee that the dashboard never blinds operators during dark emergency control room operations, `body.light-mode` is permanently neutralized to `#0A0A0A`, while `body.high-contrast-mode` activates a true `#000000` pitch-black mode with `#525252` borders and `#FFFFFF` typography.

---

### 4. Dynamic Highest-Risk Default on Startup
Prior implementations defaulted statically to Sikkim NH-10. Phase 9E introduces real-time corridor ranking:

1. **Endpoint**: `GET /api/pahad/highest-risk-corridor`
2. **Evaluation**: Evaluates all 26 canonical corridors registered in `CANONICAL_REGISTRY` across all 8 North Eastern Region states.
3. **Deterministic Tie-Breaking**:
   * Order 1: CRI Descending (`-x['cri']`)
   * Order 2: Physical FoS Ascending (`x['fos']`, lower FoS = more unstable)
   * Order 3: Sector ID Alphabetical (`x['id']`)
4. **Caching**: 60-second in-memory TTL caching ensures that initial full ranking query (~18s) drops to `<10ms` for client reloads.
5. **Initial Corridor Identified**:
   * **Corridor**: `ML-SONAPUR-01` (Sonapur Tunnel NH-06 Portal Scarp, Meghalaya)
   * **CRI**: 40.6 / 100
   * **Risk Band**: HIGH RISK
   * **Physical FoS**: 0.926 ($FoS < 1.0$ limit equilibrium failure)
   * **P(event, 24h)**: 42.1%

---

### 5. Multi-Corridor Selection & Real Updates
When switching corridors, the UI enforces strict data honesty:
* **Immediate Value Wiping**:
  ```javascript
  scoreEl.textContent = '—';
  bandEl.textContent = 'EVALUATING...';
  probEl.textContent = 'P(event, 24h): —';
  fosEl.textContent = '—';
  rainEl.textContent = '— mm';
  mlEl.textContent = '—';
  seisEl.textContent = '—';
  loadingEl.classList.remove('hidden');
  ```
* **Live Update & Anime.js**:
  Upon receipt of backend inference:
  * CRI score counter counts smoothly using Anime.js (`animateCriScore`).
  * Conic ring dial fills and updates color according to hazard tier (`animateRingProgress`).
  * Respects `prefers-reduced-motion` media queries.
  * Mini-map dynamically re-centers on selected corridor coordinates.

#### Verification Data Across Evaluated Corridors:
| Corridor ID | Name / Highway | State | District | CRI | Risk Band | FoS | Rain 24h |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ML-SONAPUR-01` | Sonapur Tunnel NH-06 | Meghalaya | East Jaintia Hills | **40.6** | **HIGH** | **0.926** | 68.4 mm |
| `SK-NH10-KM48` | NH-10 Km 48 (29th Mile) | Sikkim | Pakyong | **22.7** | **MODERATE** | **0.928** | 68.4 mm |
| `MN-TUPUL-RLY` | Tupul Railway Corridor | Manipur | Noney | **35.4** | **MODERATE** | **0.940** | 45.0 mm |

---

### 6. Sidebar Reorganization
The sidebar drawer (`#eoc-sidebar-drawer`) was refactored into strictly 6 categories:
1. **1. PAHAD AI**: Current Prediction, Forecast, Prediction Evidence
2. **2. MAP & TERRAIN**: GIS Map, 3D Terrain, Climate, Seismic
3. **3. FIELD OPERATIONS**: Sensors, Field Reports, Field Tasks, Offline Operations
4. **4. EOC COMMAND**: Incidents, Command Brief, Authority Review, SITREP
5. **5. RESPONSE**: Routing, Geofence, Notifications, Siren Control
6. **6. SYSTEM**: Data Health, Model Status, Audit, Security

Zero visible references to `"GSI DISASTER ARCHIVE & RECURRENCE ENGINE"` or `"HISTORICAL RECURRENCE"` remain on the primary navigation.

---

### 7. Automated Test Suite Results
Five dedicated test suites were implemented and executed via pytest:

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
collected 21 items

tests\test_phase9e_highest_risk.py ....                                  [ 19%]
tests\test_phase9e_corridor_prediction.py ...                            [ 33%]
tests\test_phase9e_ui_theme.py ......                                    [ 61%]
tests\test_phase9e_sidebar.py ....                                       [ 80%]
tests\test_phase9e_prediction_consistency.py ....                        [100%]

============================= 21 passed in 21.70s =============================
```

#### Full Phase 9 Regression Test Suite:
```
tests\test_phase9b_ui.py ..............                                  [ 29%]
tests\test_phase9c_ui.py .........                                       [ 48%]
tests\test_phase9c_theme.py ....                                         [ 57%]
tests\test_phase9c_navigation.py ......                                  [ 70%]
tests\test_phase9c_corridor.py ......                                    [ 82%]
tests\test_phase9e_prediction.py ....                                    [ 91%]
tests\test_phase9e_explanation.py ..                                     [ 95%]
tests\test_phase9e_forecast.py .                                         [ 97%]
tests\test_phase9e_location_isolation.py .                               [100%]

============================= 47 passed in 15.62s =============================
```
**Total Tests Passing:** 68 / 68 (100% Pass Rate, Zero Regressions).

---

### 8. Chrome DevTools MCP Verification Proof

* **Desktop Viewport (1440x900)**:
  - Highest-risk corridor `ML-SONAPUR-01` loaded dynamically on clean startup.
  - `#pahad-ai-score` rendered `40.6`, `#pahad-ai-band` rendered `HIGH RISK`.
  - Body background verified as `rgb(5, 5, 5)`.
  - Conic ring dial displayed correct orange hazard color and progress.
* **Corridor Switching Live Verification**:
  - Switched corridor to `SK-NH10-KM48`: values immediately wiped with `EVALUATING...` state, then settled to `22.7` / `MODERATE` with FoS `0.928`.
  - Switched corridor to `MN-TUPUL-RLY`: settled to `35.4` / `MODERATE` with FoS `0.940`.
* **Mobile Viewport Emulation (390x844 iPhone 14/15)**:
  - Zero horizontal overflow.
  - Hamburger menu opened the 6-category sidebar drawer cleanly with smooth transition.
* **Console Health**:
  - `list_console_messages` returned `<no console messages found>` for uncaught errors.

---

### 9. Final Operational Commitments

```
DEFAULT_CORRIDOR_IS_HIGHEST_RISK = TRUE
CORRIDOR_CHANGE_UPDATES_CRI = TRUE
BLACK_THEME_INTEGRITY = PASS
BROWSER_FUNCTIONAL_VERIFICATION = PASS
```
