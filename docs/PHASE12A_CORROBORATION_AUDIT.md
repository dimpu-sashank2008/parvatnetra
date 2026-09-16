# PARVAT NETRA / PAHAD AI — PHASE 12A CORROBORATION AUDIT
**Audit of the 2-of-3 Multi-Signal Corroboration Heuristic & False Alarm Suppression**
*SIH 2026 Problem Statement: SIH 26001*

---

## 1. Executive Summary & Mandatory Scientific Terminology

The multi-modal confirmation mechanism in PARVAT NETRA is formally designated the:
> **`2-of-3 MULTI-SIGNAL CORROBORATION HEURISTIC`**

### Mandatory Scientific Clarification:
The system **NEVER** claims statistical independence among these three modalities. In natural hillslope geomorphology, heavy rainfall directly causes pore-water pressure elevation, which directly reduces effective shear strength and triggers physical limit equilibrium failure. Because these physical processes are mechanically coupled in nature, calling them "statistically independent" would be scientifically illiterate.

Instead, they represent **independent observational modalities and distinct mathematical paradigms** (Limit Equilibrium Mechanics, Empirical Climatological Thresholds, and Supervised Statistical Learning) that corroborate a single unfolding geological crisis.

---

## 2. Modality Specifications

| Signal Identifier | Operational Modality | Mathematical / Physical Condition | Data Sources |
|---|---|---|---|
| **Signal A** | **Geotechnical Limit Equilibrium** | Infinite-Slope Factor of Safety $FoS \le 1.0$ (Critical Instability) | Mohr-Coulomb equation with piezometer pore pressure and DEM slope. |
| **Signal B** | **Hydrometeorological Forcing** | Mandal & Sarkar I-D threshold exceeded ($I \ge 4.045 D^{-0.25}$) OR $R_{24h} \ge 100.0\text{ mm}$ | IMD nowcast stations, Open-Meteo telemetry, and local rain gauges. |
| **Signal C** | **Statistical Machine Learning / Telemetry Anomaly** | Calibrated Landslide Likelihood $P(\text{event}) > 0.80$ OR severe ground deformation | GBDT model artifact, borehole inclinometer ($>5\text{ mm/day}$), or InSAR LOS velocity. |

### Role of ML Probability:
Machine learning probability is NOT used as an unverified standalone trigger. It acts as **Signal C** — a correlated supporting classifier trained on historical failure windows. It can corroborate physical or hydrological evidence, but cannot unilaterally issue an evacuation order without concurring evidence.

---

## 3. Seven-Permutation Corroboration Truth Table

The table below demonstrates the exact behavior of the false alarm suppression engine when the raw Composite Risk Index reaches emergency levels ($\text{Raw CRI} \ge 80.0$, tentative `EXTREME`):

| Permutation | Modalities Triggered | Signals Count | Raw CRI | Final CRI | Alert Band | Auto-Downgraded? | Public Alert Eligible? | Operational Action |
|---|---|---|---|---|---|---|---|---|
| **1. A only** | FoS $\le 1.0$ only | $1 / 3$ | $85.0$ | **$79.9$** | `VERY_HIGH` | **YES** | **NO** | SDRF field inspection dispatched; dozer staging. |
| **2. B only** | Rain trigger only | $1 / 3$ | $85.0$ | **$79.9$** | `VERY_HIGH` | **YES** | **NO** | Advisory watch to DDMA; traveler route guidance. |
| **3. C only** | ML $> 0.80$ only | $1 / 3$ | $85.0$ | **$79.9$** | `VERY_HIGH` | **YES** | **NO** | Telemetry sanity check; sensor recalibration flagged. |
| **4. A + B** | FoS + Rain | $2 / 3$ | $85.0$ | **$85.0$** | `EXTREME` | **NO** | **YES** | Emergency siren armed; EOC command sign-off requested. |
| **5. A + C** | FoS + ML/Deform | $2 / 3$ | $85.0$ | **$85.0$** | `EXTREME` | **NO** | **YES** | Emergency siren armed; structural road closure ready. |
| **6. B + C** | Rain + ML/Deform | $2 / 3$ | $85.0$ | **$85.0$** | `EXTREME` | **NO** | **YES** | Arterial bypass diversion; evacuation standby. |
| **7. A + B + C**| All 3 Modalities | $3 / 3$ | $85.0$ | **$85.0$** | `EXTREME` | **NO** | **YES** | Highest confidence convergence; immediate evacuation protocol. |

---

## 4. Key Takeaways for SIH Evaluators & Authorities

1. **Zero False-Alarm Single Spikes:** A single malfunctioning sensor (e.g. a broken piezometer showing infinite pore pressure, or a sudden weather API spike) can NEVER produce an `EXTREME` evacuation alarm.
2. **Deterministic Ceiling:** If fewer than 2 signals agree, the final CRI is capped at $79.9$ (the uppermost limit of `VERY_HIGH`), completely preventing automatic emergency siren activation.
3. **Transparent Downgrade Audit Trail:** The downgrade reason is stored in machine-readable format (`res.downgraded = True`, `res.downgrade_reason = "..."`) and displayed on the EOC console.
