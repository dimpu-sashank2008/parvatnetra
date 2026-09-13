# PARVAT NETRA — Final Professional UI/UX Architecture & Experience Framework

**Platform**: PARVAT NETRA — Unified Decision Intelligence & Life-Safety System  
**Engine**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Release**: Phase 3.6 Production Final  
**Standard**: Smart India Hackathon (SIH 2026 Grade) • GIGW 3.0 Institutional Quality  

---

## 1. Product Identity & Persona Segregation

PARVAT NETRA maintains a strict conceptual separation of responsibilities:
- **PARVAT NETRA**: The national operational platform, decision support framework, and life-safety dispatch system.
- **PAHAD AI**: The predictive multimodal intelligence engine providing early hazard detection, Factor of Safety calculations, and multi-horizon event probabilities.

### Dual Operational Personas
1. **EOC Command Authority (`role=authority`)**:
   - Authorized officers, District Disaster Management Authorities (DDMAs), Border Roads Organisation (BRO).
   - Unrestricted access to tactical siren arming, CAP v1.2 broadcast dispatch, 15 km geofence controls, and full telemetry audit rails.
2. **Citizen Advisory Mode (`role=citizen`)**:
   - Public-facing advisory interface with high-contrast road closures, safe detour routing, localized warnings, and one-tap emergency citizen report generation.
   - Authority-only dispatch buttons, siren arming triggers, and internal raw triage queues are automatically removed from the DOM.

---

## 2. Institutional Visual System & Theme

### Color Palette (Obsidian Slate Standard)
- **Primary Background**: `#070B10` (Deep Obsidian)
- **Surface Elevation**: `#0B132B` (Slate Card Base) / `#0F172A` (Floating Panel)
- **Border & Separator**: `#1E293B` / `#334155`
- **National Emblem Accent**: `#FF9933` (Saffron), `#FFFFFF` (White), `#138808` (India Green)
- **Status Tiers**:
  - `CRITICAL RED`: `#EF4444` / `#991B1B` (Life-safety emergency, siren dispatch)
  - `WARNING AMBER`: `#F59E0B` / `#92400E` (Heightened watch, pre-position equipment)
  - `ELEVATED CYAN`: `#06B6D4` / `#003366` (Model driver divergence, sensor scrutiny)
  - `NORMAL GREEN`: `#10B981` / `#065F46` (Nominal baseline equilibrium)

### Typography
- **Headings & Body**: `Inter` / `Noto Sans` (Compact, high legibility, -0.015em letter spacing).
- **Telemetry & Mathematics**: `JetBrains Mono` (Zero ambiguity between 0 and O, 1 and l).
- **Multilingual Script Support**: Full native font stacks for Devanagari (Hindi/Nepali), Tibetan/Sikkimese (Bhutia), Lepcha (Róng-ring), and Eastern Nagari (Assamese).

### Strict Prohibitions Enforced
- **ZERO EMOJIS**: Replaced everywhere with clean, semantic vector iconography (`Phosphor Icons` / SVG paths).
- **NO CYBERPUNK / GAMING HUDs**: Strictly eliminated video-game crosshairs, pulsing sci-fi grids, and distracting glow effects.
- **DATA HONESTY PROTOCOL**: Every card, map layer, and graph displays an explicit provenance badge (`[LIVE]`, `[DERIVED]`, `[SIMULATED]`, `[HISTORICAL]`, `[DEMO]`).

---

## 3. Dedicated Workspace Ecosystem

The platform unifies 7 specialized workspaces accessible via the persistent institutional toolbar:

| URL Endpoint | Workspace Identity | Primary Responsibility |
| :--- | :--- | :--- |
| `/` | **Command Dashboard** | Multi-hazard map, live incident feed, safe route corridors, citizen reports, and SIH demonstration engine. |
| `/pahad-ai` | **PAHAD AI Observatory** | 3D digital twin, 6 converging streams, 8-stage pipeline stepper, physics formulas, and interactive sensitivity simulator. |
| `/climate-map` | **Climate Intelligence** | Regional precipitation matrix, IMD AWS downpour rates, 24h/72h rainfall, and Mandal-Sarkar I-D threshold analysis. |
| `/seismic` | **Seismic Intelligence** | National Center for Seismology telemetry, MBT/MCT fault proximity, peak ground acceleration, and pseudostatic load modifiers. |
| `/terrain-3d` | **3D Terrain Studio** | High-performance Three.js GLO-30 DEM rendering, slope angle, profile curvature, and risk drape surfaces. |
| `/notifications` | **Alert Center** | 15 km spatial geofencing, multi-channel notification tracking (Web Push, Mobile Push, SMS, CAP v1.2), and delivery audit. |
| `/console` | **Evaluator Defense Rig** | Developer and operational telemetry bus, live SSE stream inspector, physics auditor, and geofence verification terminal. |

---

## 4. SIH Presentation Demonstration Bar

To guarantee an evaluative walkthrough during live Smart India Hackathon assessments without requiring erratic real-world storms, the platform embeds a persistent, deterministic demonstration controller:

- **Component**: `#sih-presentation-demo-bar`
- **Controls**: `[START DEMO]`, `[PAUSE]`, `[RESET]`, Speed selector (`1x`, `2x`, `FAST`).
- **Scenario**: *Active Teesta Basin Monsoon Failure Sequence* (13 deterministic stages).
- **Safety Indicator**: High-contrast, persistent `[DEMO SCENARIO ACTIVE]` badge ensuring zero ambiguity between real-world sensor feeds and simulated evaluation walkthroughs.
