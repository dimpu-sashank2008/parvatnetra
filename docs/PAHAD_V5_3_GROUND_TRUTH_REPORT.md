# PARVAT NETRA • PAHAD AI — PHASE V5.3
# GROUND TRUTH INTEGRITY & NEGATIVE CONTROL GOVERNANCE REPORT

**Phase**: V5.3 — External Source Evidence Verification & Canonical Event Forensics  
**Status**: VERIFIED & AUDITED  
**Corridor**: CORR-NH10-SIKKIM-KM48 & NER Regional Network  
**Overall Verdict**: `V5_3_EVIDENCE_VERIFIED`  
**Date**: September 2026  

---

## 1. Executive Summary

This report establishes the ground-truth partitioning, candidate quarantining, and negative control verification governing the PARVAT NETRA historical datasets.

Supervised machine learning requires mathematically rigorous ground-truth definitions:
- **Total Canonical Landslide Events**: 42
- **Authoritative Verified (`AUTHORITATIVE_VERIFIED`)**: 37 events (Eligible for Operational ML)
- **Research Candidates (`RESEARCH_CANDIDATE`)**: 5 events (Quarantined from Operational ML)
- **Verified Negative Controls (`VERIFIED_STABLE`)**: 20 observation windows
- **Synthetic Records in Operational Sets**: Exactly ZERO (0)
- **Control Selection Algorithm**: Verified observation windows with no documented failure during monitored high-precipitation or dry-season intervals.

---

## 2. Ground-Truth Partitioning Architecture

```
                       CANONICAL EVENT INVENTORY (42 Records)
                                      |
               +----------------------+----------------------+
               |                                             |
   AUTHORITATIVE_VERIFIED (37)                     RESEARCH_CANDIDATE (5)
   - Primary GSI Survey                            - Local Administrative Logs
   - BRO Operational Logs                          - Lacking Geodetic Survey
   - Multi-source Remote Sensing                   - Quarantined from Operational ML
               |                                             |
       [ OPERATIONAL ML ]                             [ QUARANTINE ]
```

### Quarantined Research Candidates
The 5 events assigned `RESEARCH_CANDIDATE` status are:
1. `EV-07` (Lunglei South, Mizoram): Single municipal bulletin.
2. `EV-25` (Bhalukhop Connector, Kalimpong): Local road memorandum without geodetic survey.
3. `EV-29` (Sonapur Hill Cut, Assam): Minor roadside clearing slip.
4. `EV-32` (Jowai Bypass, Meghalaya): Municipal town clearance memo.
5. `EV-35` (Kangpokpi Sinking Zone, Manipur): Slow continuous settlement without discrete collapse survey.

---

## 3. Negative Control Window Governance

In hillslope failure modeling, a non-event sample cannot merely be assumed stable without verified observation. 

PARVAT NETRA maintains 20 verified negative control windows (`CTRL-01` through `CTRL-20`):
- **Stability Criterion**: Slope monitored across identical corridors during significant weather events where zero road blockage, zero tension cracking, and zero slope movement occurred.
- **Verification Sources**: BRO road passability registers (confirming continuous unhindered convoy movement) and CWC gauge stability records.
- **Overlap Prevention**: Controls maintain $> 15\text{ days}$ separation from documented collapse windows at identical chainage markers.
- **Class Balance**: 37 Authoritative Positives to 20 Verified Negative Controls yields a defensible 1.85:1 ratio suitable for balanced risk thresholding without artificial synthetic inflation.

---

## 4. Zero Synthetic Performance Claims Policy

1. Synthetic or simulated samples are strictly prohibited from entering `data/features/real_train.csv` or any operational model evaluation.
2. The system adheres to the SIH Scientific Integrity Standard: *An honest limitation on small real data is infinitely superior to fabricated accuracy on synthetic data.*
3. Automated verification verified in `tests/test_v5_3_ground_truth.py` (3/3 passing).
