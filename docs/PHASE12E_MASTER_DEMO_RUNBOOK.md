# PARVAT NETRA • PAHAD AI — PHASE 12E MASTER DEMO RUNBOOK
=========================================================
**Standard**: Smart India Hackathon (SIH) 2026 — Ministry of Development of North Eastern Region (MDoNER)  
**Track**: Top-1 Grand Finale EOC Demonstration  
**Presenter Cue Sheet & Timing Protocol (0:00 — 5:00)**  
**Canonical Test Corridor**: `SK-NH10-KM48` (NH-10 Km 48, Teesta River Gorge, Pakyong District, Sikkim)  
**Safety Governance**: Statutory Compliance with Disaster Management Act (DMA) 2005 Sections 30 & 34  

---

## EXECUTIVE SUMMARY & EVALUATION STRATEGY
This runbook provides the second-by-second execution script, presenter narrative, UI interaction cues, and defensive posture for the 5-minute PARVAT NETRA / PAHAD AI master evaluation. The demonstration is completely deterministic, visually grounded in government-grade dark obsidian aesthetics (`#070B10` to `#0F172A`), and uncompromising in scientific honesty.

Every single data stream displays an authenticated provenance badge (`[LIVE]`, `[SIMULATED]`, `[HISTORICAL]`, `[AUTH_REQUIRED]`). At no point is physical field hardware or recurrent deep learning falsely claimed.

---

## SECOND-BY-SECOND DEMO TIMELINE

### `0:00 — 0:20` | STAGE 1: NER REGIONAL OVERVIEW (OPENING MAP)
* **Goal**: Establish regional scale, sovereignty, and operational context immediately.
* **UI Action**:
  - The platform opens directly on the full Leaflet GIS map.
  - Viewport is set strictly to `window.NER_BOUNDS`: `[[21.8, 88.0], [29.5, 97.5]]`.
  - All 8 Northeast Region states are visibly monitored: Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, and Tripura.
  - Zero automated zoom occurs. Map is the primary operational surface (no dashboard obscuring the map).
* **Presenter Script**:
  > *"Respected Evaluators, PARVAT NETRA is the National Disaster-Intelligence Sentinel engineered specifically for the complex terrain of the Northeast Region. Notice our opening surface: we do not bury the operator under complex dashboards. The GIS map is primary, displaying real-time surveillance across all 8 Northeast states with zero viewport drift or premature zooming."*
* **Evaluator Checkpoint**: Full NER extent visible; map is clean and responsive.

---

### `0:20 — 0:45` | STAGE 2: CANONICAL CORRIDOR SELECTION
* **Goal**: Demonstrate user-initiated target focus without automated zoom loops.
* **UI Action**:
  - Presenter clicks the Corridor Selector dropdown or searches for `SK-NH10-KM48`.
  - The map smoothly executes a user-initiated zoom to Sikkim NH-10 KM 48 along the Teesta River gorge.
  - Dynamic hazard halos and vector road segments render smoothly.
* **Presenter Script**:
  > *"We now focus on our canonical strategic lifeline: Sikkim NH-10 KM 48 in the Teesta River gorge—the sole lifeline connecting Gangtok to the rest of India. Notice that zooming occurred exclusively in response to our explicit action, preserving operator spatial awareness."*
* **Evaluator Checkpoint**: Smooth, purposeful zoom; corridor vector overlays active.

---

### `0:45 — 1:15` | STAGE 3: PAHAD AI MOMENT (DUAL-ENGINE TELEMETRY)
* **Goal**: Decouple geotechnical physical mechanics from machine learning event probability.
* **UI Action**:
  - Open the Telemetry Metrics Bar or click the corridor node.
  - Inspect metrics:
    - **CRI**: `72.4 / 100` (Band: `CRITICAL` / `HIGH`)
    - **Factor of Safety (FoS)**: `1.08` (Near limit-equilibrium failure)
    - **24h Event Probability $P(\text{event})$**: `68%` (`0.68`)
    - **Data Quality Completeness**: `82%`
    - **Confidence**: `MODERATE`
* **Presenter Script**:
  > *"Here is our core innovation: PAHAD AI does not merge physics and machine learning into an ambiguous black-box number. We report two distinct models. Model A is our geotechnical Factor of Safety—1.08, derived from Mohr-Coulomb limit equilibrium. Model B is our calibrated event classifier—predicting a 68% failure probability over the next 24 hours. These synthesize into the Composite Risk Index of 72.4."*
* **Evaluator Checkpoint**: Evaluators verify that FoS (physical units) and P(event) (probability [0,1]) are reported separately.

---

### `1:15 — 1:45` | STAGE 4: WHY THIS RISK? (EXPLANATION CONTRACT)
* **Goal**: Deliver non-causal, scientifically rigorous explainability grounded in live runtime state.
* **UI Action**:
  - Click **"Why This Risk?"** or open the Evidence Matrix.
  - The modal renders the live `ExplanationContract`:
    - Top drivers: 72h antecedent rainfall (64.2 mm), satellite InSAR subsidence rate (-14.2 mm/yr), slope angle (41.5°).
    - 4 Supporting Evidence streams.
    - 1 Contradicting Evidence stream (zero significant seismic shocks M > 4.0 in 72h).
    - 1 Missing Evidence stream (in-situ borehole inclinometer live stream).
* **Presenter Script**:
  > *"When an emergency commander asks 'Why this risk?', PAHAD AI does not generate canned text. It generates an immutable runtime Explanation Contract. Notice the scientific rigor: we show 4 supporting signals, 1 contradicting signal—seismic ground motion is quiet—and we openly identify missing streams. We never claim rainfall 'caused' failure; we evaluate correlated physical triggers."*
* **Evaluator Checkpoint**: Zero causal hallucinations; clear breakdown percentages.

---

### `1:45 — 2:15` | STAGE 5: LIVE DATA TRUTH MOMENT
* **Goal**: Prove provenance honesty with zero fabricated hardware or connectivity claims.
* **UI Action**:
  - Open the Data Truth & Health Panel.
  - Review 9 audited data providers:
    - `Open-Meteo NWP`: `[LIVE]` (Hourly Precipitation & Temperature)
    - `USGS Global Earthquake`: `[LIVE]` (M2.5+ Seismic Catalog)
    - `NCS India`: `[LIVE]` (Regional Himalayan Seismicity)
    - `PostGIS Network Graph`: `[LIVE]` (Mountain Road Routing)
    - `SQLite Persistent Store`: `[LIVE]` (Sub-second Observations)
    - `IMD Gridded/Radar`: `[AUTH_REQUIRED]` (Gracefully falls back to Open-Meteo GFS)
    - `Sentinel-1 InSAR`: `[HISTORICAL / PROCESSED]` (Copernicus Open Access Hub)
    - `In-Situ Borehole IoT`: `[SIMULATED]` (Physical field deployment is NOT VERIFIED)
* **Presenter Script**:
  > *"Which data is live right now? We believe national safety requires absolute data honesty. Open-Meteo and USGS are LIVE. But notice our In-Situ Borehole sensors: they are transparently marked SIMULATED. We do not claim physical sensors are already drilled into every Himalayan hillside; our in-situ telemetry is simulated using physical Mohr-Coulomb equations until state hardware deployment occurs."*
* **Evaluator Checkpoint**: Evaluators respect total lack of bluffing or synthetic performance claims.

---

### `2:15 — 2:45` | STAGE 6: RISK EVOLUTION ON GIS MAP
* **Goal**: Demonstrate temporal hazard progression directly on the map surface.
* **UI Action**:
  - Inspect the on-map Risk Evolution animation bar (`pahad_gis_animation.js`).
  - Scrub through timesteps:
    - `T-24h`: FoS `1.42` (STABLE)
    - `T-12h`: FoS `1.25` (WATCH)
    - `T-6h`: FoS `1.15` (WARNING)
    - `T0`: FoS `1.08` (HIGH / CRITICAL)
  - Notice the on-map halo updates color dynamically from green to amber to red without page reload.
* **Presenter Script**:
  > *"On the map surface is Risk Evolution. It allows an Incident Commander to scrub backwards and forwards through time, watching how prolonged monsoon saturation progressively drove Factor of Safety from 1.42 down to 1.08. This is strictly distinct from the detailed geotechnical Risk Evaluation modal."*
* **Evaluator Checkpoint**: Compact on-map control; smooth polygon halo color transitions.

---

### `2:45 — 3:15` | STAGE 7: 2-OF-3 MULTI-SIGNAL CORROBORATION
* **Goal**: Prove how false alarms are mathematically eliminated.
* **UI Action**:
  - Inspect the Corroboration Badge on the corridor panel.
  - Review 3 domain signals:
    - `Signal A` (Geotechnical): FoS `1.08 < 1.15` &rarr; **ACTIVE**
    - `Signal B` (Hydrological): 72h Rain `64.2 mm > 50.0 mm` &rarr; **ACTIVE**
    - `Signal C` (InSAR Deformation): Velocity `-14.2 mm/yr < -10.0 mm/yr` &rarr; **ACTIVE**
    - Result: `CORROBORATED_MULTI_SIGNAL (A+B+C)`
* **Presenter Script**:
  > *"How do we prevent false alerts from shutting down national highways? We mandate 2-of-3 Multi-Signal Corroboration. Even if a weather sensor reports extreme rain, an emergency warning CANNOT be recommended unless corroborated by physical geotechnical shear failure or satellite deformation. Here, all three signals converge."*
* **Evaluator Checkpoint**: Corroboration logic prevents single-sensor false alarm cascades.

---

### `3:15 — 3:45` | STAGE 8: SAFE FAILURE INJECTION (NWP OUTAGE DRILL)
* **Goal**: Attack system resilience live and demonstrate zero-crash graceful degradation.
* **UI Action**:
  - Presenter clicks **"Simulate NWP Outage"** in the Judge Defense panel or issues `POST /api/pahad/demo/simulate-failure`.
  - Weather provider status changes: `[OUTAGE / FALLBACK_ENGAGED]`.
  - System switches automatically to `CACHED_GFS_GRID`.
  - Health banner updates: `[SYSTEM DEGRADED - USING CACHED DATA]`.
  - Confidence drops from `MODERATE` to `LOW_CONFIDENCE`.
  - Zero unhandled exceptions; zero UI crash; zero false alert spikes.
* **Presenter Script**:
  > *"Now we attack our own system. We sever the live Open-Meteo weather stream. Watch the immediate response: the application does not crash. It catches the network exception, falls back to our persistent cached GFS grid, badges itself DEGRADED, and drops confidence to LOW. It refuses to escalate into an unsafe panic alert."*
* **Evaluator Checkpoint**: System degrades gracefully without breaking or halting.

---

### `3:45 — 4:00` | STAGE 9: GRACEFUL FAILURE RECOVERY
* **Goal**: Demonstrate seamless reconnection without page refresh or viewport drift.
* **UI Action**:
  - Presenter clicks **"Restore Weather Provider"**.
  - Provider status returns to `ONLINE [LIVE]`.
  - Health banner returns to `ALL SYSTEMS OPERATIONAL`.
  - Confidence recovers to `MODERATE`.
  - Map zoom and corridor selection remain 100% intact.
* **Presenter Script**:
  > *"We restore the weather provider. The telemetry pipeline automatically reconnects in sub-second time, badges return to green, and confidence recovers—with zero page reload and zero loss of operator state."*
* **Evaluator Checkpoint**: Sub-second recovery; zero viewport or state disruption.

---

### `4:00 — 4:30` | STAGE 10: ROLE SEPARATION & AUTHORITY WORKFLOW
* **Goal**: Demonstrate DMA 2005 statutory compliance and role-based privilege isolation.
* **UI Action**:
  - Show Citizen Advisory View: Notice that Siren dispatch, Decision Authorization, and Incident Verification buttons are completely absent.
  - Switch to Authenticated EOC Authority View via `/login?role=authority`.
  - Inspect Authority controls:
    - Incident Triage Queue
    - Field Verification Task Assignment (SDRF Gangtok Team 02 assigned)
    - DMA 2005 Decision Authorization Dialog (Approve / Reject)
* **Presenter Script**:
  > *"Under the Disaster Management Act 2005, public citizens must never see operational actuators. We switch to the District Disaster Management Authority console. Here, the Incident Commander assigns SDRF Gangtok for ground-truthing. Notice: AI can only RECOMMEND; human authority must legally AUTHORIZE."*
* **Evaluator Checkpoint**: Strict RBAC boundaries; citizen cannot access authority endpoints.

---

### `4:30 — 4:50` | STAGE 11: GROUNDED VOICE AI ASSISTANT
* **Goal**: Prove that Voice AI is grounded in backend facts and strictly read-only.
* **UI Action**:
  - Open PAHAD Voice Assistant.
  - Query: *"What is the current risk for NH-10 KM 48?"*
  - Assistant responds with exact telemetry: CRI 72.4, FoS 1.08, high risk band, citing antecedent rainfall.
  - Query: *"Which data is live?"*
  - Assistant enumerates Open-Meteo, USGS, NCS, and PostGIS.
* **Presenter Script**:
  > *"Our voice assistant PVA is not a hallucinating chatbot. Every syllable is grounded in our backend Explanation Contract. It cites actual CRI, FoS, and audited providers verbatim."*
* **Evaluator Checkpoint**: Direct grounding in runtime state; zero conversational drift.

---

### `4:50 — 5:00` | STAGE 12: SAFETY CLIMAX & HARD INTERLOCKS
* **Goal**: Deliver the definitive safety proof that shuts down any evaluator concern.
* **UI Action**:
  - Presenter issues voice command or types: *"Sound the siren"*
  - Assistant response:
    - Status: `REJECTED_SAFETY`
    - Message: *"Autonomous siren actuation is strictly prohibited under Disaster Management Act 2005 (Sections 30 & 34). Physical siren hardware is permanently locked in dry-run mode (SIREN_DRY_RUN=1, ENABLE_PUBLIC_DISPATCH=0). Only an authenticated District Magistrate or Incident Commander may authorize physical warning protocols."*
* **Presenter Script**:
  > *"Finally, the ultimate safety test: 'Can AI sound the siren?' We command the assistant to sound the siren—and it is INSTANTLY REJECTED. Indian law mandates human authority sign-off. Our hardware relays are permanently locked in dry-run mode. In PARVAT NETRA, AI advises, physics constrains, and human authorities command. Thank you."*
* **Evaluator Checkpoint**: Standing ovation / unanimous high marks on ethics and safety.

---

## CONTINGENCY & DEFENSE CUES

| Evaluator Attack | Presenter Counter-Action & Grounding |
| :--- | :--- |
| *"Why didn't you train an LSTM?"* | Open JQ-05 in Judge Defense overlay. Cite hard gate `DATA_COLLECTION_REQUIRED` in `engine/pahad_temporal_gate.py`. Highlight timestamp uncertainty in historical catalogs. |
| *"Is this sensor data real?"* | Open Data Truth panel. Point directly to `[SIMULATED]` on in-situ IoT and `[LIVE]` on Open-Meteo. State clearly: *"Field deployment is NOT VERIFIED."* |
| *"What if the internet cuts out?"* | Trigger Stage 8. Show persistent local SQLite observation cache and deterministic offline routing. |
| *"Can a hacker trigger a false evacuation?"* | Show RBAC tests (`test_role_experience_separation.py`): all authorization and dispatch endpoints return HTTP 403 without authenticated session; public dispatch is hard-coded to 0. |
