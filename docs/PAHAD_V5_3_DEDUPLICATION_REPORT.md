# PARVAT NETRA • PAHAD AI — PHASE V5.3
# SPATIO-TEMPORAL DEDUPLICATION REPORT

**Phase**: V5.3 — External Source Evidence Verification & Canonical Event Forensics  
**Status**: VERIFIED & AUDITED  
**Corridor**: CORR-NH10-SIKKIM-KM48 & NER Regional Network  
**Overall Verdict**: `V5_3_EVIDENCE_VERIFIED`  
**Date**: September 2026  

---

## 1. Executive Summary

This report documents the pairwise spatio-temporal deduplication forensics applied to the historical landslide inventory.

In mountain hazard databases, multiple agencies often generate separate communiques for the same event using slightly differing local names (e.g., local bridge name vs mile-marker). Admitting duplicate records inflates training samples and introduces artificial sample density.
- **Deduplication Threshold**: Distance < 5.0 km AND Time Difference < 48.0 hours
- **Duplicate Records Detected**: 1 (`DUP-01`)
- **Action Taken**: Merged into canonical parent event `EV-11` lineage; removed from canonical count
- **Remaining Pairwise Collisions**: Exactly ZERO (0)
- **Deduplication Status**: 100% Validated & Leakage-Free

---

## 2. Spatio-Temporal Collision Logic

The pairwise distance between two events $A$ and $B$ is calculated using the Haversine great-circle formula:

$$d = 2 R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_A)\cos(\phi_B)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$

Where:
- $R = 6371.0 \text{ km}$ (Earth radius)
- $\phi_A, \phi_B$ are latitudes in radians
- $\lambda_A, \lambda_B$ are longitudes in radians

The time difference is:

$$\Delta t = |t_A - t_B| \text{ in hours}$$

A collision flag is triggered if and only if:

$$\left(d < 5.0 \text{ km}\right) \land \left(\Delta t < 48.0 \text{ hours}\right)$$

---

## 3. Detected Duplicate Case Forensics

### Duplicate Record: DUP-01
- **Reported Name**: Mawsynram East PWD Chute Collapse
- **Reported Coordinates**: $25.2980^\circ \text{N}, 91.5830^\circ \text{E}$
- **Reported Timestamp**: 2021-06-26T14:30:00Z
- **Source**: Local PWD Sub-division road memorandum
- **Canonical Parent**: `EV-11` (Mawsynram Debris Flow, $25.3012^\circ \text{N}, 91.5847^\circ \text{E}$, 2021-06-26T12:00:00Z)
- **Spatial Separation**: 0.41 km
- **Temporal Separation**: 2.50 hours
- **Forensic Determination**: `DUP-01` represents the continuous retrogressive failure of the upper crown scarp of the primary `EV-11` debris flow. Creating two independent training rows would cause immediate spatial autocorrelation leakage.
- **Resolution**: Merged as a supplementary corroborating citation in `data/processed/v5_3_event_lineage.json`.

---

## 4. Pairwise Separation Verification

An automated $42 \times 42$ matrix distance evaluation confirmed that:
1. Every distinct canonical event pair $(EV_i, EV_j)$ where $i \neq j$ maintains either:
   - Spatial separation $\ge 5.0\text{ km}$, OR
   - Temporal separation $\ge 48.0\text{ hours}$.
2. Events located on the same highway corridor (such as NH-10 Likhiphir `EV-24` and Teesta Bazar `EV-18`) are separated by more than 700 days, representing entirely distinct monsoon trigger seasons.
3. Automated regression verified in `tests/test_v5_3_deduplication.py` (2/2 passing).
