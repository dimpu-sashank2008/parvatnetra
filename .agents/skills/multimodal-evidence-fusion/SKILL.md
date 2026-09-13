---
name: multimodal-evidence-fusion
description: >-
  Implementation guide for PARVAT NETRA's core differentiator: Multimodal Evidence Fusion.
  Use when developing physics-based Factor of Safety (FoS) calculations, ML susceptibility models,
  geotechnical anomaly detection, Bayesian evidence weighting, or explainable AI ("Why" breakdowns).
---

# PARVAT NETRA — Multimodal Evidence Fusion Guide

The signature technical innovation of PARVAT NETRA is **Multimodal Evidence Fusion**. The platform rejects single-factor alerts in favor of cross-corroborated evidence spanning physical geotechnical mechanics, satellite radar, in-situ sensors, optical computer vision, and historical hazard records.

---

## 1. Physical Foundation: Infinite Slope Stability (Factor of Safety)

Before any AI model runs, physical equilibrium is evaluated via the modified Mohr-Coulomb Infinite Slope Equation:

$$\text{FoS} = \frac{c' + \left(\gamma \cdot z \cdot \cos^2 \beta - u\right) \cdot \tan \phi'}{\gamma \cdot z \cdot \sin \beta \cdot \cos \beta}$$

Where:
- $c'$: Effective soil cohesion ($kPa$)
- $\gamma$: Unit soil weight ($kN/m^3$)
- $z$: Failure plane depth ($m$)
- $\beta$: Slope inclination angle ($^\circ$)
- $u$: Pore-water pressure from piezometer ($kPa$)
- $\phi'$: Effective internal friction angle ($^\circ$)

### Equilibrium States:
- **$\text{FoS} > 1.5$**: Stable (Low trigger probability).
- **$1.0 \le \text{FoS} \le 1.5$**: Marginally Stable (Elevated watch condition).
- **$\text{FoS} < 1.0$**: Active Instability / Failure Imminent.

---

## 2. Evidence Fusion Matrix & Modality Weights

When observations are ingested, each modality contributes an evidence vector:

| Modality | Ingested Parameter | Anomaly Condition | Base Weight ($\omega_i$) |
| :--- | :--- | :--- | :--- |
| **Geotechnical** | Pore-water pressure ($u$) & Tilt ($\theta$) | $du/dt > 5\text{ kPa/h}$ or Tilt $> 2.5^\circ$ | 0.28 |
| **Physics FoS** | Infinite slope FoS | $\text{FoS} < 1.15$ | 0.25 |
| **Precipitation** | 24h & 72h accumulated rain | $> 80\text{ mm}$ in 24h or $> 150\text{ mm}$ in 72h | 0.18 |
| **Satellite Radar**| InSAR Line-of-Sight deformation | Velocity $> -15\text{ mm/year}$ | 0.12 |
| **Computer Vision**| CCTV / drone edge model | Tension crack or mudflow detected | 0.10 |
| **Citizen Reports**| Geo-tagged community reports | $\ge 2$ verified reports within 500m | 0.07 |

$$\text{Fused Risk Score} = \sum_{i=1}^{N} \omega_i \cdot s_i \times C_{\text{confidence}}$$

---

## 3. Explainability Engine ("Why" Breakdown)

Every risk assessment must generate a human-interpretable rationale. Black-box outputs without reasons are strictly forbidden.

### Output Structure:
```json
{
  "fused_risk_score": 88.4,
  "threat_level": "WARNING",
  "factor_of_safety": 0.98,
  "primary_trigger": "Pore-water pressure saturation and active slope shear",
  "explainability_breakdown": [
    { "modality": "Geotechnical Piezometer", "contribution_pct": 34.2, "detail": "Pore pressure spiked 28 kPa in 3 hours" },
    { "modality": "Physics Engine", "contribution_pct": 29.8, "detail": "Factor of Safety dropped below unity (0.98)" },
    { "modality": "Precipitation", "contribution_pct": 21.5, "detail": "Antecedent 72h rainfall reached 142mm" },
    { "modality": "Computer Vision", "contribution_pct": 14.5, "detail": "Road shoulder tension crack detected by CCTV-04" }
  ]
}
```
