# PARVAT NETRA / PAHAD AI — PHASE V5.2
## TEMPORAL LEAKAGE AUDIT & CAUSAL INTEGRITY REPORT

**Document ID:** `PN-DOC-V5.2-TEMPORAL-LEAKAGE`  
**Phase:** `V5.2 — External Data Expansion & Ground-Truth Ingestion`  
**Primary Corridor:** `CORR-NH10-SIKKIM-KM48`  
**Status:** `ELIMINATED & LEAKAGE-FREE`  
**Operating Boundary:** Strictly Localhost-Only (`127.0.0.1`)

---

### 1. The Temporal Leakage Hazard
In early warning AI, temporal leakage occurs when future information—such as peak post-collapse rainfall, emergency response road closure timestamps, or satellite imagery taken days after failure—infiltrates the pre-event prediction window. This produces deceptively high test accuracy but causes immediate operational failure in real-time deployment.

---

### 2. Temporal Invariant Verification

#### 2.1 ISO-8601 Timestamp Validation
- 100% of canonical event timestamps are verified UTC ISO-8601 strings (e.g. `2023-10-04T01:30:00Z`).
- Zero missing timestamps, zero unparseable dates, and zero relative or speculative event times.

#### 2.2 Strict Pre-Event Feature Boundary
For all multi-horizon feature vectors (1h, 3h, 6h, 12h, 24h, 48h, 72h antecedent windows):
$$t_{\text{observation}} \le t_{\text{event}} - \tau_{\text{lead\_time}}$$
- Zero observations occurring after the confirmed failure initiation time are admitted.
- Rainfall intensity, antecedent precipitation index (API), pore-water pressure, and seismic acceleration curves are clipped strictly at $t \le t_{\text{event}}$.

#### 2.3 Non-Event Control Window Integrity
- All 20 negative control windows feature strictly verified $[t_{\text{start}}, t_{\text{end}}]$ intervals ($t_{\text{start}} < t_{\text{end}}$).
- Control periods are selected from documented non-failure intervals and verified to have zero overlap with confirmed landslide failure windows in the same geographic radius ($< 5.0 \text{ km}$).

---

### 3. Temporal Holdout Split
Instead of unscientific random splits, Phase V5.2 establishes strict temporal partitioning:
- **Training Set (24 events)**: Oldest historical period (2018–2022).
- **Validation Set (10 events)**: Intermediate historical period (2023).
- **Test Set (8 events)**: Most recent operational period (2024).

This guarantees that models are evaluated on true future generalization without chronological leakage.
