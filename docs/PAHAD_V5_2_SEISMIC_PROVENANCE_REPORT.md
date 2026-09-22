# PARVAT NETRA / PAHAD AI — PHASE V5.2
# SEISMIC TELEMETRY PROVENANCE & TECTONIC CONTEXT REPORT

**Document ID:** `PN-DOC-V5.2-SEISMIC-PROV`  
**Phase:** `V5.2`  
**Status:** `AUDITED & COMPLIANT`

---

## 1. Context & Invariant Mandate
The North-Eastern Region (NER) of India is situated in Seismic Zone V, traversed by the Main Boundary Thrust (MBT), Main Central Thrust (MCT), and Kopili Fault zones. Strong ground motion degrades hillslope shear strength and triggers co-seismic landslides or creates micro-fissures that accelerate subsequent rainfall-induced failure.

**Phase V5.2 Anti-Relabeling Directive:**
Under no circumstances may United States Geological Survey (USGS) earthquake hazard feeds be labeled as National Center for Seismology (NCS) telemetry.

---

## 2. Operational Seismology Chain

```
[Seismic Query for NER BBox]
             |
             v
Check NCS_API_BASE_URL in .env
             |
             +---> [Configured] ---> Query NCS REST API ---> Tag: [LIVE / NCS]
             |
             +---> [Missing/Empty] -> Fallback: USGS FDSNws -> Tag: [LIVE / USGS]
```

### 2.1 Mathematical Application
When a seismic trigger occurs within $150\text{ km}$ of a monitored sector:
1. **Epicentral Distance ($R_{\text{epi}}$) and Hypocentral Distance ($R_{\text{hypo}}$)** are calculated.
2. **Peak Ground Acceleration (PGA)** is estimated via regional Himalayan Ground Motion Prediction Equations (GMPE).
3. **Pseudo-Static Acceleration ($k_h$):**
   $$k_h = \min\left(0.15, \frac{\text{PGA}}{g} \times 0.5\right)$$
   Directly injected into the infinite-slope Mohr-Coulomb equation:
   $$\text{FoS} = \frac{c' + (\gamma z \cos^2\beta - u - \gamma z k_h \sin\beta \cos\beta) \tan\phi'}{\gamma z \sin\beta \cos\beta + \gamma z k_h \cos^2\beta}$$

All seismic triggers are strictly logged with source attribution, magnitude, and focal depth.
