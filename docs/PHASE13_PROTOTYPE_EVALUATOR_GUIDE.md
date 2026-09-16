# PARVAT NETRA — Evaluator Review Guide (SIH 2026 Top-5 Selection)
**Objective**: Rapid, confusion-free assessment of the PARVAT NETRA prototype for SIH 2026 evaluators.

---

## 1. The Five Evaluator Comprehension Tests

### The 20-Second Test: What Does It Do?
> **Answer**: PARVAT NETRA is an AI-assisted landslide risk intelligence and emergency decision-support platform designed for the 8 states of the North Eastern Region (NER). It monitors critical mountain highway corridors (such as NH-10 in the Teesta Valley), predicts slope failure 24–48 hours ahead of time, and coordinates emergency logistics, detour routing, and multi-lingual alerts.

### The 40-Second Test: Why Is It Different?
> **Answer**: Existing tools rely on single-rainfall thresholds (producing ~48% false alarms) or black-box neural networks that disaster managers hesitate to trust. PARVAT NETRA is different because it fuses **Geotechnical Physics** (Mohr-Coulomb limit equilibrium & Green-Ampt infiltration) with **Machine Learning** (GBDT event classification), **Multimodal Evidence** (InSAR satellite deformation + ground sensors + citizen reports), and **Explainable Attribution** under strict **Human-in-the-Loop EOC Authorization**.

### The 90-Second Test: How Does It Work?
> **Answer**: 
> 1. **Data Ingestion**: Ingests live IMD weather forecasts, satellite radar deformation, and geotechnical telemetry.
> 2. **Physical Computation**: Calculates matric suction degradation and Factor of Safety ($FoS$).
> 3. **Machine Learning**: Runs a calibrated Gradient Boosting Classifier to estimate 24h event probability ($P_{event}$).
> 4. **Multimodal Corroboration**: Evaluates the **2-of-3 Rule** (Rainfall threshold exceeded + Geotechnical FoS $< 1.0$ + ML $P_{event} \ge 0.50$).
> 5. **Decision Support**: If confirmed, recommends executive actions (e.g. BRO Project Swastik SOP-ALPHA excavator pre-positioning, IRC SP:84 Lava-Gorubathan freight bypass, and 4-language CAP voice alerts).

### The 2-Minute Test: What Is Genuinely Live?
> **Answer**:
> - **[LIVE]**: IMD Numerical Weather Prediction (NWP) precipitation grids and nowcasting.
> - **[CACHED]**: PostGIS road network geometry, CartoDEM terrain slope layers, and OpenStreetMap basemaps.
> - **[HISTORICAL]**: GSI National Landslide Susceptibility Mapping (NLSM) and historical landslide inventory.
> - **[SIMULATED]**: In-situ geotechnical sensors (piezometer pore-water pressure, volumetric water content, MEMS tilt) are simulated via validated Mohr-Coulomb soil mechanics.
> - **[AUTH_REQUIRED]**: Civil defense sirens and CAP broadcasts require authenticated EOC human clearance.

### The 2-Minute Test: What Are Its Limitations?
> **Answer**:
> 1. Continuous in-situ borehole piezometer and inclinometer telemetry is not yet physically deployed across every kilometer of the Himalayan highway network; telemetry in uninstrumented corridors is simulated using rigorous physics models.
> 2. The event prediction model status is honestly labeled `TRAINED_LIMITED_DATA / RESEARCH PROTOTYPE` due to the limited volume of clean, timestamped historical landslide records in the NER.
> 3. The temporal sequence model (`engine/pahad_lstm.py`) is explicitly identified as a physics-informed surrogate (`NOT_TRAINED LSTM`), as continuous multi-year sequence training data is currently being instrumented.

---

## 2. Recommended Evaluator Click Journey

### Step 1: Open Homepage (`http://localhost:8080/`)
- Observe the **Full NER Map** initializing across all 8 states (Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura).
- Notice that camera zoom is never hijacked or auto-focused unexpectedly.
- Observe the **Decision Intelligence Card** on the right with the Fast KPI summary row:
  - **CRI Score**: `68.0 / 100` (Multi-Modal Composite Risk)
  - **FoS Limit**: `1.040` (Mohr-Coulomb Geotechnical Stability)
  - **P(Event)**: `72.0%` (24h GBDT Horizon)
  - **Quality**: `HIGH` (Data Confidence)
- Inspect the **WHY THIS RISK?** section displaying explicit multimodal evidence (IMD Rainfall, Static Susceptibility, InSAR Deformation, Soil Saturation, Field Tension Cracks).

### Step 2: Explore the 48-Hour Risk Evolution
- Drag the **Temporal Risk Evolution Scrubber** at the bottom of the map from $T_{-24h}$ through $T_{+48h}$.
- Watch slope saturation and risk bands evolve spatially on the vector layer without page reload.

### Step 3: Test Role Realism & Security
- As a **Public Citizen** (default):
  - Check the arterial status banner, evacuation bypass route recommendations, and citizen hazard submission button.
  - Notice that all siren dispatch and executive protocol buttons are completely hidden from the view.
  - Try accessing `http://localhost:8080/?mode=authority` without logging in: the system protects state authority and renders the safe public citizen view.
- As an **EOC Authority**:
  - Log in via the authority portal.
  - Access the complete command suite: BRO Project Swastik SOP staging, dual-key human authorization dialogue, and interlocked siren actuator test rig.
