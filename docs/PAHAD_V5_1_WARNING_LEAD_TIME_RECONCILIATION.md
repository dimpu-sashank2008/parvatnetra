# PARVAT NETRA / PAHAD AI — PHASE V5.1 WARNING LEAD-TIME RECONCILIATION

**Document ID**: `DOC-V5-1-LEAD-TIME-RECON`  
**Phase**: V5.1 — Scientific Truth Ledger & Warning Lead-Time Audit  
**Primary Corridor**: `CORR-NH10-SIKKIM-KM48`  
**System Designation**: Smart India Hackathon (SIH) 2026 AI-Assisted Research and Decision-Support Prototype  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering Swarm  
**Date**: September 21, 2026  

---

## 1. Executive Summary

This report clarifies the warning lead-time capabilities of PARVAT NETRA / PAHAD AI across model families, resolving the discrepancy between the claimed "4.2h median warning lead time" and empirical historical observation sequences.

---

## 2. Model Family Warning Lead-Time Mapping

| Model Family | Target Horizon | Operational Lead Time | Empirical Basis | Status |
|---|---|---|---|---|
| **Production BiLSTM V3** | Multi-Horizon Susceptibility | **24.0 to 48.0 hours** | Synoptic meteorological forcing windows | `OPERATIONAL_FROZEN` |
| **PAHAD Event Classifier (GBDT)** | Binary Occurrence Probability | **24.0 hours** | Antecedent infiltration observation interval | `TRAINED_LIMITED_DATA` |
| **Research BiLSTM V4.5** | Long-Range Saturation Front | **48.0 to 168.0 hours** | 7-day antecedent saturation front ($CSI=0.952$) | `RESEARCH_BASELINE_OFFLINE` |
| **Historical Geotechnical Ensemble (Defense Sheet)** | Multi-Modal Warning Sequence | **Median 14.5 hours** (Min 4.2h, Max 38.0h) | Empirical reanalysis across 17 disaster sequences | `HISTORICAL_BENCHMARK` |
| **In-Situ Kinematic ML Model** | Imminent Slope Failure | **0.0 hours** (`NOT_TRAINED_DATA_PENDING`) | Requires high-frequency borehole telemetry (pending drilling) | `NOT_TRAINED` |

---

## 3. Discrepancy Resolution: 4.2h vs 14.5h

### 3.1 The Origin of "4.2 Hours"
In early development phases, 4.2 hours was identified as:
1. The **minimum** lead time observed during sudden cloudburst events (e.g., Kalijhora EV-01 flash failure).
2. A demo calculation formula based on Saito's inverse velocity equation.

### 3.2 The Empirical Reality
Across all 17 canonical historical events, the median warning lead time provided by the antecedent meteorological and hydrological indicators is **14.5 hours**.
- **Minimum**: 4.2 hours (rapid failure, high-intensity cloudburst).
- **Median**: 14.5 hours (typical monsoon saturation failure).
- **Maximum**: 38.0 hours (slow-moving progressive creep).

### 3.3 Formal Finding
Claiming that "4.2 hours" is the median lead time misrepresents both the statistical distribution and the system's operational capability. 4.2 hours is the historical **minimum**, while 14.5 hours is the empirical **median**. Both are recorded accurately in the Scientific Truth Ledger.
