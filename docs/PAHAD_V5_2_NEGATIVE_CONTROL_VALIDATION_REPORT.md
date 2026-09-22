# PARVAT NETRA / PAHAD AI — PHASE V5.2
# NEGATIVE CONTROL STABILITY & NON-OVERLAP VALIDATION REPORT

**Document ID:** `PN-DOC-V5.2-CONTROLS`  
**Phase:** `V5.2`  
**Status:** `VALIDATED & VERIFIED`

---

## 1. Executive Summary
Supervised binary landslide prediction requires negative controls (non-events) that are scientifically defensible rather than randomly assumed stable. Random points in time or space may contain unrecorded micro-slides or colluvial movements. 

Phase V5.2 validates twenty (20) canonical negative control windows certified by continuous highway logs, weather records, and district communique archives.

---

## 2. Control Selection Criteria
Every negative control must satisfy:
1. **Absence of Failure Evidence:** Documented proof from BRO road logs or district authorities confirming 0 carriageway breaches, tension cracks, or slope closures during the observation window.
2. **Precipitation Stress:** Windows include both dry quiescent periods and moderate monsoon rainfall windows (up to $185.0\text{ mm}$ 72h accumulation) where slopes remained stable, teaching classifiers that rain does not always trigger failure.
3. **Temporal Duration:** Exactly 168 hours (7 days) continuous observation.
4. **Spatial Non-Overlap:** Verification that no documented landslide failure occurred within a $2.0\text{ km}$ spatial radius during the active window.

---

## 3. Inventory Summary
- **Canonical Controls:** 20 records (`CTRL-01` through `CTRL-20`)
- **Corridors Covered:** NH-10 KM48 Pakyong, Mangan, Noney, Aizawl, Dima Hasao, Mawsynram, Kohima, Tawang
- **Stability Status:** 100% `VERIFIED_STABLE`
- **Hash Verification:** 20/20 controls equipped with deterministic SHA-256 control hashes.
