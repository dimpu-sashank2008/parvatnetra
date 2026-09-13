# PARVAT NETRA / PAHAD AI — Phase 3 Architecture Document
**Real Landslide Event Prediction + Multimodal Evidence Fusion + Operational Resilience**
**Standard: Smart India Hackathon (SIH) 2026 Grade National Disaster-Intelligence Platform**

---

## 1. Executive Summary & Paradigm Shift

Phase 3 transitions **PAHAD AI** from a primarily physics/rule-based geotechnical simulation into a **scientifically grounded, event-trained early warning system** while strictly preserving existing physical mechanics (Mohr-Coulomb Factor of Safety, $FoS$), existing REST APIs, and UI capabilities.

### The Three Core Scientific Distinctions
PAHAD AI formally segregates three concepts that are frequently conflated in early-warning systems:
1. **Susceptibility ($S$)**: *"Is this location inherently prone to slope failure?"*
   - Grounded in static geomorphology: SRTM/Copernicus 30m DEM slope, aspect, profile curvature, GSI historical landslide density, and bedrock lithology.
2. **Stability ($FoS$)**: *"Is the slope mechanically stable right now under current pore pressure?"*
   - Grounded in geotechnical physics: Infinite slope limit-equilibrium with Mohr-Coulomb shear strength, piezometer pore-water pressure, and toe-scour saturation front.
3. **Event Probability ($P(\text{event})$)**: *"How likely is a mass-movement failure within the next 6, 12, 24, or 48 hours?"*
   - Grounded in calibrated Gradient Boosted Decision Trees trained on historical GSI/NER failure and non-failure observation windows.

---

## 2. End-to-End Operational Pipeline

```text
                    PARVAT NETRA
                         │
                      PAHAD AI
                         │
        ┌────────────────┼────────────────┐
        │                │                │
 SUSCEPTIBILITY       STABILITY        EVENT ML
        │                │                │
 Terrain/History        FoS         6/12/24/48h
        │                │                │
        └────────────────┼────────────────┘
                         │
                  MULTIMODAL FUSION
                         │
        ┌────────────────┼────────────────┐
        │        │        │        │       │
    IMD AWS   Sentinel   IoT    Seismic  GSI NLSM
        │      InSAR   Piezometer  Arc    Catalog
        │        │        │        │       │
        └────────┴────────┴────────┴───────┘
                         │
                    PAHAD CRI
            (H = αS + βP + γA; CRI = H × V × 100)
                         │
               Confidence & Agreement
               (2-of-3 Safety Rule)
                         │
              ┌──────────┴──────────┐
              │                     │
          Prediction              Alert
          (Multi-horizon)      (Geofenced CAP,
              │                 Siren & Mesh)
           Explain                  │
         (Non-causal)             Route
              │               (Safe Lifelines)
              └──────────┬──────────┘
                         │
                      Respond
            (SDRF/NDRF Staging & Convoy)
```

---

## 3. Multimodal Evidence Fusion & 2-of-3 Safety Invariant

To eliminate false alarms while guaranteeing zero unmitigated disasters along strategic Himalayan defense lifelines (NH-10, NH-717A, NH-29), PAHAD AI enforces the **Two-of-Three Signal Agreement Rule**:

### Signals Evaluated for RED / EXTREME Alerts
1. **Physical FoS $\le 1.00$**: Direct Mohr-Coulomb limit equilibrium failure.
2. **Rainfall Exceedance**: IMD AWS rainfall crosses the Mandal-Sarkar or Caine empirical Intensity-Duration ($I\text{-}D$) threshold.
3. **ML Event Probability $> 0.80$**: Calibrated GBDT multi-horizon probability exceeds $80\%$.

### Policy Invariant
- If computed Composite Risk Index ($CRI$) reaches $\ge 80.0$, but fewer than 2 of the 3 primary signals are confirmed, the system **automatically downgrades the alert to VERY_HIGH (capped at 79.9)** with an explicit notification badge: `[DOWNGRADED_BY_SAFETY_POLICY]`.
- Supporting evidence (InSAR deformation $> 15\text{ mm/yr}$, seismic ground-shaking trigger, piezometer pore pressure spike) adds quantitative modifier points without bypassing the 2-of-3 invariant.

---

## 4. Operational Resilience & Offline Readiness

1. **Deterministic Fallbacks**: If upstream live sensors, external weather APIs, or local PostgreSQL databases are offline, the engine deterministically falls back to certified historical geotechnical baselines with a clear provenance badge (`[LIVE / DETERMINISTIC]`).
2. **Offline GIS Manifest (`/api/geospatial/offline-manifest`)**: Pre-bundles DEM rasters, administrative boundaries for all 8 NER states, BRO road networks, NDMA shelters, and critical sector risk snapshots for offline SQLite/GeoPackage operation in zero-connectivity field zones.
3. **Tri-Mode Mobile Client**: Native Flutter application operating seamlessly across Authority Mode, Field Ops Mode, and Citizen Safety Companion Mode.
