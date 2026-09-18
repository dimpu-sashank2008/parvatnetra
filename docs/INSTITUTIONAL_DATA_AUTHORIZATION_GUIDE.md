# PARVAT NETRA • PAHAD AI — Institutional Data Authorization & Onboarding Guide

**Document ID**: `PN-GOV-AUTH-2026-V1`  
**Classification**: National Disaster Intelligence / Official Institutional Onboarding  
**Platform**: PARVAT NETRA (NER Sentinel) • PAHAD AI  

---

## 1. Executive Summary & Authorization Architecture

PARVAT NETRA operates on a **Multimodal Evidence Fusion** architecture combining:
1. **Atmospheric Telemetry**: High-resolution precipitation and radar nowcasting from the **India Meteorological Department (IMD)**.
2. **Lithological & Geological Baseline**: 1:250,000 Geological Quadrangle Maps (GQMs), fault tectonics, and live landslide bulletins from the **Geological Survey of India (GSI)**.
3. **Earth Observation & InSAR Telemetry**: Interferometric Synthetic Aperture Radar (InSAR) Line-of-Sight deformation and CartoDEM digital elevation models from the **National Remote Sensing Centre (NRSC / ISRO)** via **Bhuvan** and **Bhoonidhi**.
4. **Hydrometric River Telemetry**: River gauge stages, discharge rates, and toe-scour alerts from the **Central Water Commission (CWC)**.
5. **Seismotectonics**: Focal depth, hypocenter, and peak ground acceleration (PGA) from the **National Center for Seismology (NCS)**.

To transition from prototype/shadow-mode operations to sovereign real-time deployment, specific institutional access permissions, MOUs, and API keys are required from each nodal government agency.

---

## 2. Institutional Authorization Status & Degradation Fallback Matrix

| Agency | Data Asset Required | Upstream Portal / Gateway | Current Prototype Status | Live Degradation Fallback Mode | Statutory Prerequisite for Live Production |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IMD** | Real-time AWS (15-min), Gridded 0.25° Rain, DWR Radar Reflectivity | IMD Data Supply Portal (`dsp.imdpune.gov.in`) | `AUTH_REQUIRED` | Cached high-res monsoon telemetry & Open-Meteo Global Ensembles | Institutional Recommendation Letter signed by Head of Institute / VC |
| **GSI** | National Landslide Forecasting Centre (NLFC) Live Bulletins, Bhukosh Shapefiles | GSI Bhoomi & Bhukosh Portals (`bhukosh.gsi.gov.in`) | `CACHED / REPOSITORIED` | 10 Official GSI 1:250k Geological Quadrangle Maps (GQMs) + 17 Ground Truth Events | Formal Request to Additional Director General, GSI LSMD Kolkata |
| **NRSC / ISRO** | Sentinel-1 & NISAR InSAR SLC stacks, CartoDEM 10m/30m, Bhuvan Thematic WMS | ISRO Bhuvan & Bhoonidhi Hub (`bhuvan.nrsc.gov.in`, `bhoonidhi.nrsc.gov.in`) | `PROXIED / CACHED` | 3-Tier Proxy (`/api/isro/wms-proxy`), Authoritative InSAR PS Stacks (Teesta & NH-10) | Academic / SIH Institutional MOU for Bhoonidhi High-Bandwidth API |
| **CWC** | Real-time river stages, discharge, high flood level (HFL) warnings | CWC Flood Forecast Portal (`ffs.india-water.gov.in`) | `OPERATIONAL / CACHED` | Teesta River hydro stations (Singtam, Dikchu, Melli) with 15-min gauge cache | Inter-agency data sharing agreement under NDMA aegis |
| **NCS** | Real-time NER earthquake origin time, hypocenter, magnitude, ShakeMap | NCS Earthquake API (`seismo.gov.in`) | `LIVE / STAGING` | Local resilient staging gateway (`scripts/ncs_staging_gateway.py` port 20888) + USGS/Global | Open access via standard NCS API credentials |

---

## 3. Turnkey Institutional Permission Letter for IMD API Access

Based on the official India Meteorological Department institutional authorization protocol (Ref: Ministry of Earth Sciences, New Delhi), the following document is pre-filled and ready to be printed on your university/institute letterhead, signed by your Director/Dean/Principal, and submitted to the Director General of Meteorology:

```text
[ON THE OFFICIAL LETTERHEAD OF THE INSTITUTE / UNIVERSITY]

Ref. No.: ________________________                                Date: ____________________

PERMISSION / RECOMMENDATION FOR ACCESS TO IMD APIs

To
The Director General of Meteorology
India Meteorological Department (IMD)
Ministry of Earth Sciences, Government of India
Mausam Bhawan, Lodhi Road,
New Delhi – 110003

SUBJECT: Recommendation and Permission for API Access for Research & Disaster Early Warning System (PARVAT NETRA / PAHAD AI)

Respected Sir,

This is to certify that the project team comprising:
1. [Name of Team Lead / Scholar], [Enrollment/Roll No.], [Department/Programme]
2. [Name of Team Member], [Enrollment/Roll No.], [Department/Programme]
3. [Name of Team Member], [Enrollment/Roll No.], [Department/Programme]
of [Department of Computer Science / Civil Engineering / Earth Sciences], [Name of Institute / University], is/are undertaking the project titled:

"PARVAT NETRA: Multimodal Predictive AI & Hillslope Telemetry Early-Warning System for the North-Eastern Region (PAHAD AI)"

under the academic supervision and guidance of [Name & Designation of Faculty / Project Guide], [Department Name].

The project details and specific technical requirements for IMD API access are detailed below:

+---------------------+---------------------------------------------------------------------------------------------+
| Particular          | Details                                                                                     |
+---------------------+---------------------------------------------------------------------------------------------+
| Project Objective   | To construct an autonomous, physics-grounded early-warning system that ingests real-time    |
|                     | meteorological telemetry, models geotechnical Factor of Safety (FoS) and hillslope         |
|                     | destabilization risk, and provides early warnings with up to 24-hour lead time across       |
|                     | critical highway corridors in the North-Eastern Region (NER).                               |
+---------------------+---------------------------------------------------------------------------------------------+
| IMD APIs Required   | 1. Real-time Automated Weather Station (AWS) 15-minute precipitation & temperature telemetry |
|                     | 2. High-resolution Gridded Daily/Hourly Rainfall Data (0.25° x 0.25° resolution)             |
|                     | 3. Doppler Weather Radar (DWR) composite reflectivity products (Agartala, Mohanbari, Sohra) |
|                     | 4. District-level Severe Weather & Flash Flood / Nowcast Advisories                         |
+---------------------+---------------------------------------------------------------------------------------------+
| Inputs              | IMD API telemetry combined with GSI 1:250k geological quadrangle baselines, InSAR ground   |
|                     | deformation vectors, and CWC river stage hydrometry.                                        |
+---------------------+---------------------------------------------------------------------------------------------+
| Methodology         | Mohr-Coulomb Infinite Slope stability physics coupled with calibrated Gradient Boosted       |
|                     | event classifiers, Antecedent Precipitation Index (API-24h / API-72h) threshold curves,     |
|                     | and 2-of-3 multimodal confirmation gating before alert dispatch.                           |
+---------------------+---------------------------------------------------------------------------------------------+
| Expected Outputs    | Real-time Composite Risk Index (CRI) geospatial dashboards, OASIS CAP v1.2 warning feeds,   |
|                     | evacuation routing intelligence for SDRF/NDRF, and automated SitRep generation.             |
+---------------------+---------------------------------------------------------------------------------------------+
| Project Timeline    | [Start Date, e.g., October 2024] to [End Date / Standing Academic Research]                 |
+---------------------+---------------------------------------------------------------------------------------------+

The Institute hereby grants permission and strongly recommends the above-mentioned project team for obtaining access to the required IMD APIs, solely for the purpose of the stated national disaster-intelligence project and for the duration indicated above.

The Institute undertakes that the IMD APIs, if access is granted:
1. Shall be used strictly and exclusively for the stated non-commercial research and early warning project;
2. API credentials, secret tokens, and raw telemetric datasets shall not be shared with any unauthorized person, third party, or commercial vendor;
3. All terms, conditions, rate limits, and data-security requirements prescribed by IMD / MoES shall be strictly complied with;
4. The data shall not be redistributed or commercialized under any circumstances;
5. Due acknowledgment to the India Meteorological Department (IMD), Ministry of Earth Sciences, Government of India, shall be prominently displayed in all publications, technical presentations, and system interfaces.


Sincerely,

Authorized Signatory: _________________________________________
Name:                 [Prof. / Dr. Name of Head of Institute]
Designation:          Director / Dean (R&D) / Principal / Head of Institute
Institute/University: [Name of Institute / University]
Official Email:       [official.email@institute.ac.in]
Contact Number:       [+91-XXXXXXXXXX]

[ OFFICIAL INSTITUTIONAL SEAL ]
```

---

## 4. GSI (Geological Survey of India) Authorization & Data Integration

### 4.1 What GSI Provides:
1. **National Landslide Susceptibility Mapping (NLSM)**: 1:50,000 macro-zonation polygons covering all hilly terrains of India.
2. **National Landslide Forecasting Centre (NLFC)**: Experimental daily regional landslide forecast bulletins issued for Sikkim, Kalimpong, Nilgiris, and Uttarakhand.
3. **Geological Quadrangle Maps (GQMs)**: 1:250,000 degree sheets establishing lithological formations, thrust faults, strike-slip shear zones, and dip angles.

### 4.2 GSI Data Integration in PARVAT NETRA:
PARVAT NETRA has ingested **10 official GSI 1:250,000 GQMs** directly into its physics and telemetry core:
- **Sheet 78M**: Tawang Quadrangle (Se La Group migmatites, Bomdila Group, MCT)
- **Sheet 83I**: Lower Siang Quadrangle (Siwaliks, MBT, HFT, Tipi Thrust, Bomdila Thrust, Kimin, Harmoti, Ziro)
- **Sheet 83E**: Subansiri Quadrangle (Papum Pare / Itanagar)
- **Sheet 78O**: Shillong Quadrangle (Shillong Group quartzites, Dawki Fault, Kulsi Fault)
- **Sheet 78K**: Tura Quadrangle (AMGC crystalline complex, Dapsi Thrust)
- **Sheet 78J**: Goalpara Quadrangle (Assam / Bhutan Foothills transition)
- **Sheet 83D**: Silchar Quadrangle (Surma Group, Bhuban & Bokabil shales)
- **Sheet 83H**: Imphal Quadrangle (Disang Group splintery flysch shales, Noney/Tupul)
- **Sheet 83G**: Peren Quadrangle (Barail Range massive arenites, NH-29 corridor)
- **Sheet 83J**: Sibsagar Quadrangle (Nagaland / Schuppen Belt, Naga Thrust)

### 4.3 Required Formal Request to GSI:
To integrate GSI NLFC's live bulletin API:
- **Addressee**: Additional Director General & Head, Landslide Studies & Management Division (LSMD), Geological Survey of India, Central Headquarters, 27 J.L. Nehru Road, Kolkata – 700016.
- **Request Scope**: Read-only JSON/GeoJSON access to the experimental NLFC Daily Landslide Bulletin feed for NER states (Sikkim, Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram).

---

## 5. NRSC / ISRO (Bhuvan & Bhoonidhi) Authorization

### 5.1 Clarifying Bhuvan vs. Bhoonidhi:
- **ISRO Bhuvan (`bhuvan.nrsc.gov.in`)**:
  - Web Map Service (WMS) / Tile Map Service (TMS) portal for thematic layers (Landslide Susceptibility Zonation, Land Use / Land Cover, Geomorphology).
  - *Current Status in PARVAT NETRA*: The platform's backend proxy (`/api/isro/wms-proxy`) securely queries Bhuvan WMS endpoints. If upstream ISRO servers return 404, rate limit, or require internal S-band tokens, the proxy returns a transparent $1\times 1$ PNG tile without breaking the Leaflet GIS canvas.
- **ISRO Bhoonidhi (`bhoonidhi.nrsc.gov.in`)**:
  - Open data hub for satellite optical and SAR products (CartoDEM 30m, Resourcesat-2, Sentinel-1, NISAR).
  - *Current Status in PARVAT NETRA*: Persistent Scatterer InSAR stacks for the Teesta Basin and NH-10 corridors are archived in the PostGIS database and local authoritative fallback storage.
  - *Production Onboarding*: Requires an Academic / Research Data Agreement with National Remote Sensing Centre (NRSC), ISRO, Dept. of Space, Balanagar, Hyderabad – 500037 for batch InSAR Single Look Complex (SLC) downloads.

---

## 6. How to Deploy Credentials in PARVAT NETRA Once Received

Once official approval letters are signed and API credentials are issued, **zero code modification is needed**. The administrator simply updates `.env`:

```bash
# ------------------------------------------------------------------------------
# INSTITUTIONAL LIVE CREDENTIALS CONFIGURATION
# ------------------------------------------------------------------------------

# India Meteorological Department (IMD)
IMD_API_BASE_URL="https://dsp.imdpune.gov.in/api/v1"
IMD_API_TOKEN="YOUR_OFFICIAL_IMD_TOKEN_HERE"

# Geological Survey of India (GSI)
GSI_BHUKOSH_API_URL="https://bhukosh.gsi.gov.in/api/nlfc"
GSI_API_KEY="YOUR_GSI_ACCESS_KEY_HERE"

# National Remote Sensing Centre (NRSC / ISRO)
ISRO_BHUVAN_TOKEN="YOUR_BHUVAN_MAP_TOKEN_HERE"
NRSC_BHOONIDHI_USER="YOUR_INSTITUTIONAL_USERNAME"
NRSC_BHOONIDHI_KEY="YOUR_INSTITUTIONAL_SECRET"

# Central Water Commission (CWC)
CWC_HYDRO_API_URL="https://ffs.india-water.gov.in/api/realtime"
CWC_API_KEY="YOUR_CWC_TELEMETRY_KEY"

# National Center for Seismology (NCS)
NCS_SEISMO_API_URL="https://seismo.gov.in/api/v1/events"
NCS_API_KEY="YOUR_NCS_SECRET_KEY"
```

The system automatically detects the credentials on boot, switches from `[SIMULATED] / CACHED` to `[LIVE]` provenance badges, and connects to live national pipelines while preserving all fail-closed safety interlocks.
