# PARVAT NETRA / PAHAD AI — Phase V4.5 Final Scientific Research Report

**Document ID**: `PAHAD-DOC-V4-5-FINAL-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  
**Operational Status**: **RESEARCH / OFFLINE EVALUATION ONLY**  
**Final Verdict**: `V4_5_RESEARCH_IMPROVED`  
**Active Production Model**: `PAHADBiLSTMv3` (LOCKED & SERVING)  

---

## 1. Executive Scientific Summary
Phase V4.5 successfully evaluated the influence of continuous 168-hour (7-day) real temporal environmental forcing on multi-horizon landslide forecasting across 17 documented GSI disaster events and 20 verified negative controls.

### Key Scientific Findings:
1. **Long-Range Infiltration Superiority**:  
   Expanding sequential context from 72h (V4.3) to 168h (V4.5) allows the model to learn the multi-day antecedent soil moisture wetting front. In 17-fold Leave-One-Event-Out cross-validation, the model achieved **100% detection (17/17 events)** at 48h, 72h, and 168h horizons with mean Brier scores $\le 0.0067$.
2. **Temporal Attention Dynamics**:  
   The learned attention weights allocate **76.8%** of total attention to the antecedent 120h infiltration window and **23.2%** to the recent 48h trigger window.
3. **Physical Boundary on Imminent Horizons (6h, 12h)**:  
   Regional 9km reanalysis data cannot resolve slope-scale shear strain or localized microbursts. Imminent 6h prediction remains data-limited on unmonitored historical slopes.
4. **Authoritative Verdict**:  
   `V4_5_RESEARCH_IMPROVED`.
