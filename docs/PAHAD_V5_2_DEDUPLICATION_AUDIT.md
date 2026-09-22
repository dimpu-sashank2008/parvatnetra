# PARVAT NETRA / PAHAD AI — PHASE V5.2
# SPATIO-TEMPORAL DEDUPLICATION AUDIT REPORT

**Document ID:** `PN-DOC-V5.2-DEDUP`  
**Phase:** `V5.2`  
**Status:** `AUDITED`

---

## 1. Executive Summary
Landslide events in mountainous corridors are frequently reported multiple times by different agencies (e.g. BRO reporting highway blockage, Police reporting traffic diversion, and SDMA reporting civilian infrastructure damage). Without systematic deduplication, models suffer from artificial sample clustering and data leakage.

---

## 2. Deduplication Criteria & Mathematical Definition
A candidate record $R_{\text{new}}$ is identified as a duplicate of existing canonical event $R_{\text{canon}}$ if and only if both conditions are met:
1. **Spatial Proximity:** 
   $$\text{Haversine}(R_{\text{new}}, R_{\text{canon}}) < 1.0\text{ km}$$
2. **Temporal Proximity:** 
   $$|\Delta t| = |t_{\text{new}} - t_{\text{canon}}| < 48.0\text{ hours}$$

### 2.1 Deduplication Action
When a collision is detected:
- The candidate is **NOT** inserted as a new row in the canonical inventory.
- The secondary source citation is appended to `merged_sources` in the canonical record.
- If a `VERIFIED_PRIMARY` event receives corroborating satellite damage mapping or SDMA verification, its status is upgraded to `VERIFIED_MULTI_SOURCE`.

---

## 3. Audit Results
All 42 canonical events were verified to have pairwise spatial separations $\ge 1.0\text{ km}$ or temporal separations $\ge 48.0\text{ hours}$. Zero artificial duplications exist in the expanded canonical registry.
