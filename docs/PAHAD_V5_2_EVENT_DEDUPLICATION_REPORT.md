# PARVAT NETRA / PAHAD AI — PHASE V5.2
## DETERMINISTIC SPATIO-TEMPORAL EVENT DEDUPLICATION REPORT

**Document ID:** `PN-DOC-V5.2-EVENT-DEDUPLICATION`  
**Phase:** `V5.2 — External Data Expansion & Ground-Truth Ingestion`  
**Primary Corridor:** `CORR-NH10-SIKKIM-KM48`  
**Status:** `AUDITED & COLLISION-FREE`  
**Operating Boundary:** Strictly Localhost-Only (`127.0.0.1`)

---

### 1. The Deduplication Imperative
In mountain disaster informatics, major landslides generate numerous uncoordinated communiques across disaster authorities, border road engineers, news outlets, and police feeds over several days. Ingesting every communique as an independent positive label artificially inflates event density, creates geographic leakage, and distorts ML model calibration.

---

### 2. Spatio-Temporal Collision Boundary
Phase V5.2 implements a deterministic dual-threshold collision detection rule:

$$\Delta d = 2 R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)} \right) < 1.0 \text{ km}$$
$$\Delta t = |t_{\text{incoming}} - t_{\text{existing}}| < 48.0 \text{ hours}$$

If an incoming report satisfies both $\Delta d < 1.0 \text{ km}$ and $\Delta t < 48.0 \text{ hours}$ against an existing canonical event:
1. **No New Event Created**: The incoming report is flagged as `MERGED_DUPLICATE`.
2. **Lineage Preservation**: The report details (`duplicate_source`, `duplicate_reference`, `distance_km`, `time_diff_hours`) are appended to `merged_sources` of the parent canonical event.
3. **Corroboration Upgrade**: If the duplicate originates from an independent institutional authority (e.g., GSI primary + SDMA communique), the parent event's verification status upgrades to `VERIFIED_MULTI_SOURCE`.

---

### 3. Collision Audit Results
- **Candidate Reports Scanned**: 45
- **Unique Spatio-Temporal Landslide Events Admitted**: 42
- **Duplicate Communiques Merged**: 1 (SDMA follow-up on NH-10 Teesta Gorge incident)
- **Zero Double-Counting**: Total canonical event count remains strictly 42.
- **Distant Non-Duplicates Confirmed**: Events separated by $> 1.0 \text{ km}$ or $> 48 \text{ hours}$ (e.g., separate slope failures along NH-10 at Km 29, Km 42, and Km 48) remain appropriately distinct canonical events.
