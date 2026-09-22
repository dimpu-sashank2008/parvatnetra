# PARVAT NETRA / PAHAD AI — PHASE V5.2
# FIVE-TIER EVENT VERIFICATION PROTOCOL REPORT

**Document ID:** `PN-DOC-V5.2-FIVE-TIER`  
**Phase:** `V5.2`  
**Status:** `RATIFIED`

---

## 1. Executive Summary
To prevent data poisoning, anecdotal bias, and uncorroborated crowdsourced reports from entering the canonical training and validation datasets, Phase V5.2 enforces a rigorous Five-Tier Verification Protocol.

---

## 2. Verification Tier Definitions

| Tier ID | Status Name | Criteria | Canonical Admission |
| :--- | :--- | :--- | :---: |
| **Tier 1** | `VERIFIED_PRIMARY` | Direct field inspection report from Geological Survey of India (GSI) or Border Roads Organisation (BRO) project engineers. | **YES** |
| **Tier 2** | `VERIFIED_MULTI_SOURCE` | Corroboration by both State Disaster Management Authority (SDMA) communiques and optical / SAR satellite damage scars. | **YES** |
| **Tier 3** | `SECONDARY_VERIFIED` | Formal executive orders from District Emergency Operations Centers (DEOC), Police traffic records, or PWD engineering reports. | **YES** |
| **Tier 4** | `UNVERIFIED` | Single-source citizen report, social media post, or unverified local media claim without geotechnical inspection. | **NO** (Quarantined) |
| **Tier 5** | `REJECTED` | Inaccurate coordinates outside the NER boundary, duplicate entries, or non-landslide events (e.g. urban waterlogging). | **NO** (Quarantined) |

---

## 3. Current Inventory Tier Distribution
Among the 42 canonical landslide events in PARVAT NETRA:
- `VERIFIED_PRIMARY`: 32 events (76.2%)
- `VERIFIED_MULTI_SOURCE`: 6 events (14.3%)
- `SECONDARY_VERIFIED`: 4 events (9.5%)
- `UNVERIFIED`: 0 events admitted
- `REJECTED`: 0 events admitted

This ensures 100% official institutional traceability for every event in the canonical catalog.
