# PARVAT NETRA / PAHAD AI — PHASE V5.2
# EARTH OBSERVATION, INSAR & REMOTE SENSING DATA PROVENANCE REPORT

**Document ID:** `PN-DOC-V5.2-EO-PROV`  
**Phase:** `V5.2`  
**Status:** `AUDITED & COMPLIANT`

---

## 1. Executive Summary
Earth Observation (EO) layers supply the spatial morphological predisposition factors (elevation, slope, aspect, profile curvature) and slow kinetic deformation trends (InSAR line-of-sight velocities).

---

## 2. Ingested Remote Sensing Layers

### 2.1 Copernicus GLO-30 Digital Elevation Model
- **Resolution:** $30\text{ meters}$
- **Source:** European Space Agency (ESA) Copernicus Programme
- **Format:** Cloud-Optimized GeoTIFF (COG)
- **Extracted Geomorphic Indices:**
  - Hillslope Angle ($\beta$) in degrees ($0^\circ\text{--}75^\circ$)
  - Aspect (orientation with respect to monsoonal moisture fronts)
  - Surface curvature (convergent hollows vs divergent ridges)

### 2.2 Sentinel-1 InSAR Kinematics
- **Satellite:** Sentinel-1A / 1B C-band Synthetic Aperture Radar (SAR)
- **Product Mode:** Interferometric Wide Swath (IW) Single Look Complex (SLC)
- **Cadence:** 12-day orbital revisit
- **Attributes:** Line-of-sight (LOS) ground displacement rate ($mm/\text{year}$) and cumulative displacement ($mm$). Used to detect chronic creep prior to rapid failure.

### 2.3 ISRO CartoDEM & Landslide Susceptibility Mapping (NLSM)
- **Agency:** National Remote Sensing Centre (NRSC) / Geological Survey of India (GSI)
- **Role:** Baseline macroscopic landslide susceptibility zonation (Low, Moderate, High, Very High) validated across all 8 NER states.
