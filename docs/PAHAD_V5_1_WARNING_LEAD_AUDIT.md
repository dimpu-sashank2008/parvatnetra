# PARVAT NETRA / PAHAD AI — PHASE V5.1 WARNING LEAD TIME AUDIT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: Warning Lead Time Lineage, Horizon Modeling, and Saito Formula Resolution  

---

## 1. Executive Summary

A critical operational metric for any early-warning platform is **Warning Lead Time** ($\Delta t_{\text{lead}}$):
$$\Delta t_{\text{lead}} = t_{\text{failure}} - t_{\text{first alert}}$$
During cross-phase audits, an untraced summary statement claimed "Median Warning Lead Time: 4.2 hours". This audit establishes the exact origins, distributions, and physical scales of all lead-time metrics across PARVAT NETRA.

---

## 2. Lead Time by Model Family

```
+----------------------------------------------------------------------------------------------------+
| Model Key         | Architecture               | Scale     | Horizons / Lead Times | Verified Lead |
+----------------------------------------------------------------------------------------------------+
| Event GBDT        | GradientBoostingClassifier | Regional  | 1h, 3h, 6h, 12h, 24h  | 24.0 hours    |
| BiLSTM V3 (Prod)  | 2-layer BiLSTM (72h seq)   | Regional  | 6h, 12h, 24h, 48h     | 24.0 - 48.0 h |
| BiLSTM V4.5 (Res) | 1-layer BiLSTM (168h seq)  | Regional  | 48h, 72h, 168h        | 48.0 - 168.0 h|
| Defense Sheet     | Multi-modal Ensemble       | Historical| Min: 4.2h, Max: 36.0h | 14.5 h median |
| Kinematic IoT ML  | In-situ Borehole Model     | Slope-spec| NOT TRAINED           | 0.0 hours     |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Resolution of the "4.2 Hours" Metric

1. **Origin in Historical Ensemble**:
   In `CORE_IMPLEMENTATION_DEFENSE_SHEET.md`, the documented lead times across all 17 historical disasters were:
   - Minimum Lead Time: **4.2 hours** (observed during flash-triggered cloudburst events)
   - Median Lead Time: **14.5 hours** (typical synoptic saturation lead)
   - Maximum Lead Time: **36.0 hours** (slow-moving deep-seated failures)
2. **Origin in Interactive Simulator (`templates/demo.html`)**:
   The value 4.2 hours also appeared as a hardcoded static calculation in the demo UI derived from Saito's tertiary creep inverse-velocity formula:
   $$t_r = \frac{1}{\alpha \dot{\epsilon}}$$
3. **Audit Finding**:
   Citing 4.2 hours as the *median* early-warning lead time was an untraced narrative transposition. In reality:
   - 4.2 hours was the historical **minimum** lead time.
   - The true historical ensemble median lead time was **14.5 hours**.
   - The operational event classifier GBDT provides **24.0 hours** verified lead time.
   - The research BiLSTM V4.5 provides up to **48.0–168.0 hours** infiltration lead time.
   - The Kinematic IoT ML model has **0.0 hours** lead time because physical field sensors are not yet installed.

Therefore, claiming 4.2 hours as the median warning lead time is classified as **`UNSUPPORTED`**.
