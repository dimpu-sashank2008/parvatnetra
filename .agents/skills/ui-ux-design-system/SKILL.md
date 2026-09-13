---
name: ui-ux-design-system
description: >-
  Expert guidelines for designing and building PARVAT NETRA's government-grade, scientific UI/UX.
  Use when designing components, selecting color tokens, building dashboard layouts,
  enforcing accessibility (WCAG AA), responsive styling with Tailwind CSS, or conducting visual QA.
---

# PARVAT NETRA — UI/UX & Design System Guide

PARVAT NETRA is a national-grade disaster intelligence platform (NER Sentinel). Its visual design must convey calm authority, scientific credibility, and operational precision.

---

## 1. Visual Philosophy & Anti-Patterns

### Required Aesthetic:
- **Calm Operational Gravity**: Deep obsidian and charcoal surfaces (`#070B10`, `#0F172A`) with high-contrast, crisp slate typography.
- **Scientific Rigor**: Strict data hierarchy, explicit measurement units (mm/h, kPa, m/s, degrees), and confidence intervals.
- **Purposeful Micro-Interactions**: Smooth 150-200ms transitions, clear state indicators, zero motion for motion's sake.
- **Full WCAG 2.1 AA Compliance**: Minimum 4.5:1 text contrast, distinct focus rings (`focus-visible:ring-2`), and complete keyboard navigability.

### Prohibited Tropes (STRICTLY AVOID):
- **NO Cyberpunk / Neon**: Do not use vibrant neon purples, glowing cyan grids, or decorative sci-fi scans.
- **NO Gaming HUD Elements**: Do not use fake target reticles, decorative hex patterns, or spinning radars.
- **NO Excessive Glassmorphism**: Avoid blurry backdrop filters that obscure critical telemetry readability.
- **NO Generic SaaS Clutter**: Avoid rounded cartoon cards, bubbly gradients, or marketing illustrations.

---

## 2. Color Tokens & Semantic Hierarchy

| Role | Token / Hex | Tailwind Class | Semantic Meaning |
| :--- | :--- | :--- | :--- |
| **Canvas** | `#070B10` | `bg-slate-950` | Primary application viewport background |
| **Card / Surface** | `#0F172A` | `bg-slate-900` | Structured data cards, drawers, modals |
| **Elevated Surface** | `#1E293B` | `bg-slate-800` | Hover states, active tabs, floating controls |
| **Border / Divider** | `#334155` | `border-slate-700` | Clean, 1px structural separation |
| **Primary Text** | `#F8FAFC` | `text-slate-50` | Primary headers, critical telemetry figures |
| **Secondary Text** | `#94A3B8` | `text-slate-400` | Labels, timestamps, supplementary captions |
| **Critical / Evacuate**| `#EF4444` | `text-red-500`, `bg-red-500/10` | Factor of Safety < 1.0, active failure, road closed |
| **Warning / High** | `#F59E0B` | `text-amber-500`, `bg-amber-500/10` | High rainfall threshold, rapid pore pressure rise |
| **Alert / Moderate** | `#EAB308` | `text-yellow-500`, `bg-yellow-500/10` | Approaching saturation, advisory in effect |
| **Stable / Watch** | `#10B981` | `text-emerald-500`, `bg-emerald-500/10` | FoS > 1.5, normal background telemetry |
| **Command Blue** | `#3B82F6` | `text-blue-500`, `bg-blue-600` | Interactive controls, selected routes, authority actions |

---

## 3. Component Architecture & States

Every interactive component must implement all four lifecycle states:
1. **Normal / Resting**: Subtle border, clear icon, legible typography.
2. **Hover / Focus**: Distinct outline (`ring-2 ring-blue-500 ring-offset-2 ring-offset-slate-950`).
3. **Loading / Pending**: Skeleton shimmer (`animate-pulse bg-slate-800`) matching exact data layout; no blank pop-in.
4. **Empty / No Data**: Explicit explanatory message with retry action (never empty whitespace).

---

## 4. Visual QA & Verification Checklist

When reviewing or generating UI screens:
- [ ] Are all telemetry values accompanied by explicit units?
- [ ] Is every data source clearly badged (`[LIVE]`, `[SIMULATED]`, `[HISTORICAL]`)?
- [ ] Does the screen collapse cleanly to mobile without horizontal scrollbars?
- [ ] Does Chrome DevTools audit report zero accessibility contrast failures?
