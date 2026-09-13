# PARVAT NETRA / PAHAD AI — PHASE 9C ENGINEERING & ARCHITECTURE REPORT
## CLEAN GOVERNMENT EOC FRONTEND REDESIGN

---

### Executive Summary
Phase 9C successfully transforms the PARVAT NETRA frontend into an authentic, calm, authoritative National/State Emergency Operations Centre (EOC) disaster-intelligence platform compliant with GIGW 3.0, NIC, NDMA, and MDoNER institutional requirements. All visual startup cliches, cyberpunk glow tropes, and extraneous interactive widgets have been removed from the primary viewport, establishing a strict decision-first user experience.

---

### 1. Core UX Rule: The Four Operational Questions
The default homepage workspace (`#view-prediction`) now focuses exclusively on answering four critical operational questions:

$$\text{WHERE IS THE RISK?} \longrightarrow \text{HOW HIGH IS THE RISK?} \longrightarrow \text{WHY?} \longrightarrow \text{WHAT SHOULD THE AUTHORITY DO?}$$

```
+-----------------------------------------------------------------------------------------------+
| [GOVERNMENT IDENTITY HEADER]  PARVAT NETRA | पर्वत नेत्र (MDoNER / NDMA / Govt of India)       |
+-----------------------------------------------------------------------------------------------+
| [TOP OPERATIONAL KPI BAR]     Overall Risk: HIGH | Priority: NH-10 Km 48 | Monitored: 8 States|
+-----------------------------------------------------------------------------------------------+
|  1. WHERE IS THE RISK?                                                                        |
|     - Cascading Selector: State -> District -> Strategic Corridor                             |
|     - "Use Map Location" Map Point Picker + Mini-Map Footprint Indicator (Lat/Lon)            |
+-----------------------------------------------------------------------------------------------+
|  2. HOW HIGH IS THE RISK?                                                                     |
|     - Minimal, High-Legibility CRI Score Circle (CRI 72 / 100 • HIGH RISK)                    |
|     - Physical Factor of Safety (FoS 0.745) • Calibrated 24h Event Probability (72.0%)       |
|     - Model Status: [TRAINED_LIMITED_DATA] • IMD Rainfall & NCS Seismic Condition             |
+-----------------------------------------------------------------------------------------------+
|  3. WHY?                                                                                      |
|     - Plain-Language Geotechnical & Meteorological Explanation                                |
|     - Multimodal Signal Breakdown (Rainfall Loading, FoS Stability, InSAR Creep, Seismicity)  |
|     - Non-Causal Model Driver Ranking                                                         |
+-----------------------------------------------------------------------------------------------+
|  4. WHAT SHOULD THE AUTHORITY DO?                                                             |
|     - Stage 2: AI Recommended Operational Advisory                                            |
|     - Stage 3: Statutory Human Authority Sign-Off (District Magistrate / EOC Commander)       |
|     - 2-of-3 Sensor Corroboration Guardrail                                                   |
+-----------------------------------------------------------------------------------------------+
| [SLIDE-OUT EOC NAVIGATION DRAWER] (Accessed via Hamburger Button)                             |
|  1. PAHAD AI Core | 2. Map & Terrain | 3. Field Ops | 4. EOC Command | 5. Response | 6. System|
+-----------------------------------------------------------------------------------------------+
```

---

### 2. Workspace View Segregation
All secondary, tertiary, and detailed engineering views have been partitioned into dedicated `.workspace-view` containers, accessible seamlessly via the slide-out navigation drawer:

1. **`#view-prediction` (Default Active View)**:
   - Contains the Operational KPI bar and the clean PAHAD AI overview card.
   - Strictly answers Where, How High, Why, and What to Do.

2. **`#view-map` (Full GIS Map & Operational Telemetry)**:
   - Encloses the full Leaflet GIS Map, layer control toggles, contour overlays, InSAR deformation raster, habitations, cut slopes, and BRO fleet staging.
   - Features top return navigation: `<button onclick="navigateToPanel('prediction')"> ← Return to Prediction Dashboard</button>`.
   - Automatically triggers `window.map.invalidateSize()` after transition.

3. **`#view-response` (Emergency Response & Autonomous Siren Access)**:
   - Houses the new **PAHAD Autonomous Siren Access Control Card**.
   - Strict statutory safety invariants enforced:
     - State: `DISABLED` (by default) $\leftrightarrow$ `ARMED FOR AUTHORITY USE`.
     - Invariant: `human_authorization_required: True`.
     - Invariant: `two_of_three_corroboration_required: True`.
     - AI model CANNOT independently dispatch sirens.

4. **`#view-system` (System Operations & Multi-Channel Pipeline)**:
   - Houses the SIH Command Strip, PAHAD AI Model Status Panel, Edge Network LoRa Mesh Module, Alert Orchestrator Module, and the 13-stage interactive demo sequence.

---

### 3. Visual & Technical Invariants Enforced
1. **Dark Black Government EOC Palette**:
   - Backgrounds: Obsidian slate (`#05080C` to `#070B10`), dark navy (`#0B1320` to `#0F172A`), structural borders (`#1E293B` to `#334155`).
   - No visible light mode toggle on header. System defaults strictly to dark mode.
2. **Absolute Zero Unicode Emojis**:
   - 100% SVG Phosphor vector icons (`ph-bold`) across all HTML templates and scripts.
   - Zero Unicode emojis verified via regex test scanning all 10,980 lines.
3. **No Neon / Cyberpunk Aesthetics**:
   - CRI score circle redesigned with crisp high-contrast typography (`Inter` + `JetBrains Mono`).
   - Flat, legible SVG ring indicator without artificial glow filters.
4. **Local Anime.js Integration**:
   - Self-hosted at `static/js/anime.min.js`.
   - Subtle, fast (<350ms) easing animations for drawer and CRI score transitions.
   - Automatically bypassed if user system prefers reduced motion (`prefers-reduced-motion: reduce`).
5. **Cascading State $\to$ District $\to$ Strategic Corridor Hierarchy**:
   - All 8 North Eastern Region (NER) states supported: Sikkim, Manipur, Mizoram, Assam, Meghalaya, Nagaland, Arunachal Pradesh, Tripura (+ Strategic Border corridor).
   - Embedded Leaflet mini-map footprint with live coordinate display (`#pahad-prediction-minimap`).

---

### 4. Verification & Test Suite Summary
- `tests/test_phase9c_ui.py`: **9 passed**
- `tests/test_phase9c_navigation.py`: **6 passed**
- `tests/test_phase9c_theme.py`: **4 passed**
- `tests/test_phase9c_corridor.py`: **6 passed**
- `tests/test_phase9c_authority_siren.py`: **6 passed**
- **Total Phase 9C Dedicated Tests**: **31 passed (100% pass rate)**.
- **Full Backward Compatibility**: All legacy DOM element IDs preserved, ensuring zero test regressions across existing suites.
