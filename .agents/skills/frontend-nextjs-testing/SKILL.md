---
name: frontend-nextjs-testing
description: >-
  Implementation and automated verification guide for PARVAT NETRA's Next.js frontend.
  Use when building React components, configuring MapLibre GL map layers, implementing
  Safe Routes interactive drawers, or running automated visual QA with Chrome DevTools MCP.
---

# PARVAT NETRA — Frontend Architecture & Testing Guide

PARVAT NETRA's frontend is a high-performance Next.js web application engineered for emergency operations centers and mobile-first citizen warning.

---

## 1. Core Frontend Stack

- **Framework**: Next.js (App Router) + React 19 + TypeScript
- **Styling**: Tailwind CSS + Lucide React Icons
- **Mapping**: MapLibre GL / `react-map-gl` with vector tiles and terrain DEM hillshading
- **State Management**: Zustand / Lightweight React Context
- **Testing & Verification**: Chrome DevTools MCP for automated browser navigation, console monitoring, and visual audits

---

## 2. Safe Routes Interactive UX Requirements

Safe Routes is a life-critical feature with zero tolerance for visual glitching:

```
[Citizen / Authority selects Route Card]
                     │
                     ▼
[Route highlighted on MapLibre Canvas]  <-- No full re-render; update GeoJSON source only
                     │
                     ▼
[Route Drawer Slides Up / In]           <-- Shows distance, time, risk factor, hazard warnings
                     │
                     ▼
[User Clicks "Start Navigation"]        <-- High-contrast turn-by-turn guidance begins
```

### Strict Quality Rules:
1. **No Blank Re-renders**: Route selection must mutate the GeoJSON source dynamically without remounting the map instance.
2. **Deterministic Fallback**: If vector routing tiles fail, render the fallback geometric Polyline from the local API without throwing exceptions.
3. **No Dead Redirects**: All buttons must maintain active loading/disabled states while awaiting calculations.

---

## 3. Automated Browser QA Workflow with Chrome DevTools MCP

Use Chrome DevTools MCP to validate the application in an actual browser:

1. **Launch Application**: Ensure dev server is running on `http://localhost:3000`.
2. **Navigate Page**:
   ```json
   { "url": "http://localhost:3000/citizen" }
   ```
3. **DOM & Visual Inspection**:
   - Verify presence of localized risk badge (`SAFE`, `ALERT`, `EVACUATE`).
   - Click Safe Routes tab and inspect drawer opening.
   - Capture screenshot to verify high-contrast obsidian styling.
4. **Console Sniffing**:
   - Run `list_console_messages` to ensure zero uncaught JavaScript exceptions or hydration mismatches.
5. **Accessibility Check**:
   - Run Lighthouse audit via Chrome DevTools MCP to confirm WCAG compliance score $\ge 95$.
