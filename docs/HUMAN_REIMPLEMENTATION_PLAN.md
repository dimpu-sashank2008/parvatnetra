# PARVAT NETRA / PAHAD AI — Human Reimplementation & Defense Plan
**Document ID**: `DOC-SIH-2026-PLAN-001`  
**Problem Statement**: SIH 26001 — Intelligent Landslide Monitoring & Disaster Management  
**Target**: Complete Student Team Authorship, Defense Mastery, and Code Hygiene  
**Status**: ACTIVE EXECUTION RUNBOOK  

---

## 1. Purpose & Strategy

The purpose of this Human Reimplementation Plan is to ensure that every member of the student team has **100% intellectual command** over the core mathematical formulations, safety constraints, embedded protocols, and machine learning pipelines of PARVAT NETRA.

During SIH grand finale evaluation:
1. Evaluators do not just inspect working software; they cross-examine students on how equations work, why parameters were chosen, and how the code executes step-by-step.
2. AI-assisted scaffolding must never mask a lack of student comprehension.
3. The codebase must be lean, disciplined, and stripped of confusing experimental duplicate scripts.

---

## 2. Ranked Reimplementation & Mastery Priorities

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    STUDENT MASTERY & REIMPLEMENTATION TIERS                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ [TIER 1] CRITICAL CORE (Must derive on whiteboard without looking at notes)     │
│   • Mohr-Coulomb FoS limit equilibrium equation with saturated groundwater ratio│
│   • Caine/Guzzetti power-law Intensity-Duration (I-D) rainfall curves & API     │
│   • Multi-Modal Composite Risk Index (CRI) convex fusion formula                │
│   • 2-of-3 Independent Corroboration Safety Rule and automatic downgrade logic │
│   • MoRTH / IRC SP:84 Mountain Freight Routing Cost & Habitation Index (HCII)  │
│   • 18-Byte Low-Power LoRa bit-packed binary telemetry struct                   │
│   • 14.8-Day Autonomous LiFePO4 battery power budget derivation                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│ [TIER 2] HIGH PRIORITY (Must explain architecture, losses, and data flow)       │
│   • BiLSTM v3 deep sequence network (33 features, 72h window, temporal attn)    │
│   • Focal Loss formulation and Platt temperature scaling calibration            │
│   • Multi-Horizon GBDT Event Classifier (6h, 12h, 24h, 48h) & Brier score       │
│   • Leakage prevention and chronological temporal holdout splitting             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ [TIER 3] MEDIUM PRIORITY (Must understand system integration & APIs)            │
│   • IoT REST telemetry ingestion endpoints & bounds checking                    │
│   • EOC 5-Stage Alert Lifecycle & OASIS CAP-XML v1.2 generation                 │
│   • External data connectors (IMD AWS, CWC Teesta hydrometry, NCS seismology)   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ [TIER 4] LOW PRIORITY / ACCEPTED BOILERPLATE (Standard scaffolding)             │
│   • Flask app entrypoint, CORS headers, and Jinja2 template rendering           │
│   • Leaflet.js map layer rendering and CartoDB base tiles                       │
│   • Service worker offline asset caching (PWA)                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tier 1: Critical Core Modules — Step-by-Step Mastery

### 3.1 Geotechnical Mechanics: `engine/pahad_models.py`
- **What to study**: Lines 195–250 (`calculate_infinite_slope_fs`).
- **Mathematical proof to memorize**:
  $$FoS = \frac{c' + (\gamma_{sat} - m \gamma_w) z \cos^2\theta \tan\phi'}{\gamma_{sat} z \sin\theta \cos\theta}$$
- **Key boundary conditions to practice**:
  1. $m = 0 \implies FoS = \frac{c'}{\gamma z \sin\theta \cos\theta} + \frac{\tan\phi'}{\tan\theta}$ (Dry slope)
  2. $m = 1, c' = 0 \implies FoS \approx 0.5 \frac{\tan\phi'}{\tan\theta}$ (Fully submerged slope)
  3. $\theta \to 0 \implies$ division-by-zero protection (`math.sin(theta) < 1e-4` caps at $10.0$).
- **Student Exercise**: Practice deriving this on paper in under 3 minutes starting from a free-body diagram of a soil slice showing shear stress $\tau$, normal stress $\sigma$, and pore pressure $u$.

---

### 3.2 Meteorological Trigger Logic: `engine/pahad_history.py`
- **What to study**: Lines 45–120 (`is_empirical_threshold_exceeded`).
- **Equation to memorize**:
  $$I_{thresh} = \alpha \cdot D^{-\beta} \quad (\alpha=9.80, \beta=0.38 \text{ for Darjeeling-Sikkim})$$
- **Antecedent Index**:
  $$API_t = P_t + 0.84 \cdot API_{t-1}$$
- **Student Exercise**: Explain why a moderate 35 mm rainstorm on Day 7 causes a landslide if $API_{7d} > 120\text{ mm}$, whereas an 80 mm storm on bone-dry soil ($API = 0$) might not fail.

---

### 3.3 Multi-Modal CRI Fusion: `engine/pahad_fusion.py`
- **What to study**: Lines 80–190 (`PahadFusionEngine.fuse`).
- **Formula to memorize**:
  $$CRI = 0.40 \cdot S_{static} + 0.35 \cdot H_{rain} + 0.25 \cdot M_{geotech}$$
- **Key Concept**: Static susceptibility governs the baseline floor; dynamic rainfall and in-situ pore pressure scale the instantaneous risk.
- **Student Exercise**: Walk through an evaluation where $S_{static} = 70$, $H_{rain} = 85$, and $M_{geotech} = 90$, compute raw CRI, and trace the alert band mapping.

---

### 3.4 2-of-3 Corroboration Safety Rule: `engine/pahad_corroboration.py`
- **What to study**: Lines 30–95 (`evaluate_corroboration`).
- **Core Invariant**:
  $$\text{EXTREME Alert Valid} \iff (\mathbb{I}_{\text{Physics}} + \mathbb{I}_{\text{Rainfall}} + \mathbb{I}_{\text{Telemetry}}) \ge 2$$
- **Student Exercise**: Explain what happens if an inclinometer wire is severed by a wild animal and reports a sudden 50 mm displacement when rainfall is 0 mm and pore pressure is normal. (Answer: Downgraded to HIGH; dispatch inspection patrol; no public siren).

---

### 3.5 Mountain Highway Routing Engine: `backend/routing_engine.py`
- **What to study**: Lines 35–180 (`calculate_route_cost`).
- **Formula to memorize**:
  $$\text{RouteCost} = \sum \left( T_{base} + P_{gradient} + P_{curve} + P_{hazard}(CRI) + P_{load} \right)$$
- **Student Exercise**: Explain how the cost function automatically diverts a 28.5T army convoy off NH-10 (severed by a landslide at KM 48) and routes it via the Lava–Gorubathan NH-717A bypass.

---

### 3.6 Low-Power 18-Byte Binary Packet: `backend/edge/packet.py`
- **What to study**: Lines 20–65 (`pack_telemetry`, `unpack_telemetry`).
- **Binary layout to memorize**:
  - `NodeID` (2 bytes, unsigned short `H`)
  - `TimestampDelta` (4 bytes, unsigned int `I`)
  - `BatteryVoltage` (2 bytes, unsigned short `H`, millivolts)
  - `PorePressure` (4 bytes, float `f`, kPa)
  - `TiltAngle` (4 bytes, float `f`, degrees)
  - `Rainfall1h` (2 bytes, unsigned short `H`, tenths of mm)
  - **Total**: Exactly **18 Bytes**.
- **Student Exercise**: Explain why 18 bytes takes 95 ms of Time-on-Air vs 850 ms for JSON, and calculate the battery savings over 1 year.

---

### 3.7 Hardware BOM & Power Budget: `services/hardware_bom_service.py`
- **What to study**: Lines 15–120 (`get_hardware_bom_data`).
- **Numbers to memorize**:
  - Total station cost: **₹16,850** (vs ₹3.5 Lakh imported Geokon).
  - Battery: 12.8V 10Ah LiFePO4 (128 Wh storage, 108.8 Wh usable @ 85% DoD).
  - Average continuous draw: $306\text{ mW}$.
  - Autonomy: $\frac{108.8\text{ Wh}}{0.306\text{ W} \times 24\text{ h}} = \mathbf{14.8\text{ Days}}$.
  - Legal spectrum: WPC GSR 564(E) 865–867 MHz unlicensed band.
- **Student Exercise**: Present the 11 BOM components and justify each selection on price and ruggedness.

---

## 4. Code Consolidation & Quarantine Directives

To eliminate confusion during SIH technical inspection, the following script hygiene directives are enforced:

1. **Canonical Training Pipeline**:
   - `scripts/train_event_model.py` is the official, authoritative GBDT event trainer.
   - `scripts/train_lstm_v3.py` is the official, authoritative PyTorch BiLSTM sequence trainer.
2. **Quarantine Experimental Iterations**:
   - `scripts/train_lstm_v4.py`, `train_lstm_v4_1.py`, and `train_lstm_v4_2.py` are explicitly marked as **`[EXPERIMENTAL R&D ARCHIVE]`**. They explore historical backfill techniques but are NOT active production pipelines.
3. **Canonical Model Checkpoints**:
   - `models/pahad_event_model.pkl` (GBDT classifier)
   - `models/pahad_lstm_v3_weights.pt` (33-feature BiLSTM with temporal attention)
   - `models/pahad_fos_model.pkl` (Geotechnical FoS regressor)

---

## 5. Team Mock Oral Defense Regimen

| Day / Session | Focus Area | Activity | Verification Gate |
| :--- | :--- | :--- | :--- |
| **Session 1** | Geotechnical Physics & Mohr-Coulomb | Whiteboard derivation of FoS, effective stress, and pore pressure | Every member derives $FoS$ without notes in under 3 minutes |
| **Session 2** | Hydrology & Rainfall Thresholds | Derivation of Caine/Guzzetti power-law and API recursive calculation | Graphing $I$-$D$ curves and explaining antecedent saturation |
| **Session 3** | Deep Learning BiLSTM & Focal Loss | Whiteboard sketch of BiLSTM v3, 33 features, and temporal attention | Explaining class imbalance handling and honest data constraints |
| **Session 4** | Embedded Hardware & LoRa | Explaining 18-byte struct, SX1262 transceiver, and 14.8-day power budget | Calculating battery autonomy from raw current numbers |
| **Session 5** | Adversarial Grilling | 12-question cross-examination simulation with harsh evaluator roleplay | 100% fluent, confident, scientifically rigorous responses |

---

**Plan Approved**: PARVAT NETRA Engineering Leadership  
**Execution Status**: Active & Enforced.
