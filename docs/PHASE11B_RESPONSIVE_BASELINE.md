# PARVAT NETRA / PAHAD AI — PHASE 11B
# UNIVERSAL RESPONSIVE + DEVICE-ADAPTIVE UI REFINEMENT
## CP01: BASELINE INSPECTION & SYSTEM AUDIT REPORT

**Timestamp**: 2026-09-14 19:26:00 IST  
**Environment**: Windows, Python 3.11.0, Vercel Production (https://silly-fermi.vercel.app)  
**Git Baseline**: Commit `992b582` on branch `main` (synchronized with `staging` and `origin/main`)  
**Working Tree**: Clean (zero untracked or unstaged modifications)  

---

### 1. Current Frontend File Architecture

The PARVAT NETRA platform employs a server-rendered Jinja2 architecture driven by a Flask backend with Tailwind CSS, custom CSS custom properties (`parvat_theme.css`), and vanilla JavaScript UI controllers.

#### A. Templates (`templates/`):
| Template | File Size | Description & Role |
| :--- | :---: | :--- |
| `templates/index.html` | 845,591 B | Primary operational command dashboard (Authority & Citizen modes, GIS map, CRI gauge, EOC drawer, AI SitRep). |
| `templates/demo.html` | 25,847 B | Public Interactive 50m Geofence Evaluator and isolated drill simulator (`/demo`). |
| `templates/notifications.html` | 47,791 B | National & regional alert broadcast ledger and SMS/email dispatch monitor (`/notifications`). |
| `templates/pahad_ai.html` | 96,500 B | PAHAD AI predictive engine analytics observatory, multi-horizon forecasts, and model card (`/pahad-ai`). |
| `templates/climate_map.html` | 57,410 B | IMD precipitation and regional I-D rainfall threshold grid (`/climate-map`). |
| `templates/seismic.html` | 57,555 B | Main Central Thrust (MCT) seismic waveform telemetry and earthquake feed (`/seismic`). |
| `templates/terrain_3d.html` | 45,571 B | Three.js digital elevation model (DEM) and drone survey inspector (`/terrain-3d`). |
| `templates/edge_network.html` | 56,844 B | BLE Coded PHY and LoRa mesh relay node topology manager (`/edge-network`). |
| `templates/console.html` | 36,128 B | Authority system operator terminal and audit log. |
| `templates/login.html` | 17,238 B | Unified persona portal authenticator. |
| `templates/login_authority.html` | 16,818 B | Emergency Operations Center (EOC) authority login. |
| `templates/login_citizen.html` | 17,002 B | Citizen public safety portal login. |

#### B. Stylesheets (`static/css/`):
| Stylesheet | File Size | Role & Architecture |
| :--- | :---: | :--- |
| `static/css/parvat_theme.css` | 31,927 B | GIGW 3.0 theme system, obsidian slate (`#070B10` to `#0F172A`), safe-area variables, clamp typography, touch targets, and reduced motion rules. |

#### C. JavaScript Controllers (`static/js/`):
| Script | File Size | Role & Responsiveness |
| :--- | :---: | :--- |
| `static/js/pahad_voice_assistant.js` | 24,872 B | Floating interactive assistant with speech recognition, audio waveform, and quick query chips. |
| `static/js/i18n.js` | 37,212 B | Multilingual dictionary (English, Hindi, Nepali, Bengali, Assamese, etc.). |
| `static/js/theme.js` | 5,204 B | Theme persistence and accessibility toggles. |
| `static/js/network_state.js` | 10,878 B | Online/offline state listener and network status badge controller. |
| `static/js/offline_manager.js` | 6,967 B | Service worker caching and offline fallback asset manager. |
| `static/js/sync_manager.js` | 7,632 B | Background IndexedDB reconciliation and queue synchronization. |
| `static/js/local_store.js` | 13,659 B | Client-side IndexedDB telemetry store. |
| `static/js/anime.min.js` | 17,384 B | Lightweight animation engine. |

---

### 2. Core UI Components & Hierarchy Invariants

| Component | DOM Identifier | Primary Location | Responsive Behavior & Invariant |
| :--- | :--- | :--- | :--- |
| **Top Header Bar** | `#system-header-bar` | `templates/index.html` L2750 | Brand logo, problem statement badge (`SIH26001`), primary nav links, language selector, theme toggle, and login. Inline nav collapses on `< lg` screens into hamburger button. |
| **EOC Slide-out Drawer** | `#eoc-sidebar-drawer` | `templates/index.html` L2460 | Slide-out mobile and tablet navigation drawer (`w-84 max-w-[85vw]`), toggled via `#btn-hamburger-menu`. Covers 6 categories and 25 routes. |
| **Operational GIS Map** | `#gis-map-card`, `#map` | `templates/index.html` L3055 | Leaflet WGS84 viewer. Positioned **FIRST** in both Authority and Citizen modes. Bounds auto-invalidate on window resize and orientation change. |
| **CRI Command Showcase** | `#pahad-cri-hero` | `templates/index.html` L3374 | Positioned **SECOND** directly beneath GIS Map. Contains SVG circular gauge, risk band badge, location metadata, and cascading corridor picker. |
| **Regional EOC Drawer** | `#pahad-regional-drawer` | `templates/index.html` L3543 | Collapsible command panel with 8 NER states grid, InSAR diagnostic panel, and priority ranking table. Guarded: Authority-only. |
| **AI Situation Report** | `#ai-sitrep-card` | `templates/index.html` L3330 | Multi-source intelligence synthesis with IMD, CWC, InSAR, CV, and FoS corroboration badges. |
| **Observation Queue** | `#observation-queue-section` | `templates/index.html` L3908 | Authority field report triage table with live updates and responsive horizontal scroll container. |
| **Citizen Emergency Bar** | `#citizen-floating-action-bar` | `templates/index.html` L4276 | Floating emergency action bar with siren trigger and hazard reporting. |
| **Voice Assistant** | `#pahad-assistant-panel` | `templates/index.html` L13906 | Floating interactive assistant panel adapted for mobile viewports (`max-w-[calc(100vw-16px)]`, safe margins). |
| **Public Evaluator Demo** | `#geofence-card`, `/demo` | `templates/demo.html` | 50m geofence engine, GPS acquisition, proximity simulation presets, and multichannel test drill. |

---

### 3. Route & API Baseline Verification

All core routes and API endpoints were verified on the local Flask test client and production endpoint:

```
[OK] /                                -> HTTP 200 (Operational Homepage)
[OK] /demo                            -> HTTP 200 (50m Geofence Evaluator Demo)
[OK] /notifications                   -> HTTP 200 (Multi-Channel Alert Center)
[OK] /pahad-ai                        -> HTTP 200 (PAHAD AI Predictive Engine Observatory)
[OK] /climate-map                     -> HTTP 200 (IMD Precipitation & I-D Threshold Grid)
[OK] /seismic                         -> HTTP 200 (Main Central Thrust Waveform Telemetry)
[OK] /terrain-3d                      -> HTTP 200 (Three.js 3D DEM & Drone Survey)
[OK] /edge-network                    -> HTTP 200 (BLE & LoRa Mesh Relay Topology)
[OK] /login                           -> HTTP 200 (Unified Portal Authentication)
[OK] /api/pahad/model-status          -> HTTP 200 (TRAINED_LIMITED_DATA status & metrics)
[OK] /api/pahad/event-model/data-quality -> HTTP 200 (Data quality & provenance catalog)
```
**Route Health**: 100% Operational (11/11 Passed).

---

### 4. Browser Console & Runtime Status

Checked via Chrome DevTools MCP on live production (`https://silly-fermi.vercel.app/`):
- **JavaScript Runtime Crashes**: **0** uncaught exceptions (`ReferenceError`, `TypeError`, or syntax errors).
- **IndexedDB**: LocalStore IndexedDB v2 initialized successfully.
- **Geofence Service**: Active with user distance calculated against hazard centroid.
- **Real-Time Bus**: SSE real-time notification bus connected.
- **Advisories**: `cdn.tailwindcss.com should not be used in production` (Standard Tailwind CDN advisory; no runtime impact).

---

### 5. Existing Responsive Behavior & Viewport Audit

Tested across all 18 mandatory breakpoints with Chrome DevTools MCP:

| Category | Viewport | Device / Profile | ScrollWidth vs. InnerWidth | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Mobile Extra-Small** | 320 × 568 | iPhone SE (1st gen) | `320px <= 320px` (0 overflow) | **PASS** |
| **Mobile Compact** | 360 × 800 | Samsung Galaxy A series | `360px <= 360px` (0 overflow) | **PASS** |
| **Mobile Standard** | 375 × 667 | iPhone 8 / SE (2nd gen) | `375px <= 375px` (0 overflow) | **PASS** |
| **Mobile Flagship** | 390 × 844 | iPhone 12 / 13 / 14 / 15 Pro | `390px <= 390px` (0 overflow) | **PASS** |
| **Mobile High-Res** | 412 × 915 | Google Pixel 7 / Galaxy S23 | `412px <= 412px` (0 overflow) | **PASS** |
| **Mobile Phablet** | 430 × 932 | iPhone 14 / 15 Pro Max | `430px <= 430px` (0 overflow) | **PASS** |
| **Mobile Wide** | 480 × 854 | Budget Android / Wide Handset | `480px <= 480px` (0 overflow) | **PASS** |
| **Phablet / Handheld** | 600 × 960 | 7-inch Mini Tablet / Foldable | `600px <= 600px` (0 overflow) | **PASS** |
| **Tablet Portrait** | 768 × 1024 | iPad (9th/10th gen) Portrait | `753px <= 768px` (0 overflow) | **PASS** |
| **Tablet High-Density** | 820 × 1180 | iPad Air (10.9-inch) Portrait | `805px <= 820px` (0 overflow) | **PASS** |
| **Tablet Large** | 912 × 1368 | Microsoft Surface Pro 8/9 | `897px <= 912px` (0 overflow) | **PASS** |
| **Tablet Landscape** | 1024 × 768 | iPad Landscape / Netbook | `1009px <= 1024px` (0 overflow) | **PASS** |
| **Laptop Standard** | 1280 × 800 | 13-inch MacBook Pro | `1265px <= 1280px` (0 overflow) | **PASS** |
| **Laptop Common** | 1366 × 768 | Enterprise Standard Laptop | `1351px <= 1366px` (0 overflow) | **PASS** |
| **Desktop Medium** | 1440 × 900 | 15-inch Widescreen Display | `1425px <= 1440px` (0 overflow) | **PASS** |
| **Desktop Large** | 1600 × 900 | High-Res Workstation | `1585px <= 1600px` (0 overflow) | **PASS** |
| **Desktop Full HD** | 1920 × 1080 | 1080p Standard Monitor | `1905px <= 1920px` (0 overflow) | **PASS** |
| **Ultra-Wide / 2K** | 2560 × 1440 | 2K QHD Command Display | `2545px <= 2560px` (0 overflow) | **PASS** |

---

### 6. Identified Bottlenecks & Resolved Layout Guards

1. **320px Header Title Overflow**:
   - Issue: The long subtitle (`AI-Based Landslide Prediction & Early Warning...`) previously collided with the emblem and hamburger button on 320px screens.
   - Resolution: Clamped to `max-w-[170px] sm:max-w-none` on mobile, eliminating 320px header blowout.
2. **Cascading Corridor Selector**:
   - Issue: Hardcoded `max-w-[340px]` pushed beyond the 288px available width on 320px screens with 16px margins.
   - Resolution: Replaced with fluid `max-w-full sm:max-w-[340px]`.
3. **KPI Metric Ribbon**:
   - Issue: A 2-column grid on 320px screens produced 136px column widths, clipping multi-line status badges.
   - Resolution: Reflowed into single-column cards on mobile (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`).
4. **Table Container Invariant**:
   - Issue: Large data tables (triage queue, state priority lists) can force the `document.documentElement` to expand horizontally if table wrapper overflows.
   - Resolution: Wrapped tables in accessible scroll containers with `-webkit-overflow-scrolling: touch; overscroll-behavior-x: contain;`.

---

### 7. Baseline Invariant Lock

- **Geotechnical Physics (Model A)**: Mohr-Coulomb shear strength, infinite slope FoS, and piezometer pore-water pressure calculations are strictly locked and untouched.
- **Landslide Event Model (Model B)**: Calibrated `GradientBoostingClassifier` and prediction pipelines are strictly locked and untouched.
- **CRI Fusion Engine**: Composite Risk Index ($CRI = \alpha S + \beta P + \gamma G$) and 2-of-3 signal rule are strictly locked and untouched.
- **Safety Protocols**: Siren authorization, SMS/email dispatch logic, EOC state machine, and authority permission boundaries remain 100% untouched.
