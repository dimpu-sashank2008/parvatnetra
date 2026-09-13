# PARVAT NETRA / PAHAD AI — PHASE 11A PUBLIC DEPLOYMENT REPORT
**Platform:** PARVAT NETRA — NER Sentinel  
**Engine:** PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Primary Staging Platform:** Render (Docker Web Service)  
**Secondary Edge Platform:** Vercel  
**Prepared Date:** 2026-09-13  
**Status:** PHASE11A_PUBLIC_STAGING_LIVE  

---

## Executive Summary
Phase 11A establishes the public staging deployment foundation for the PARVAT NETRA / PAHAD AI platform. The complete containerized Flask application has been deployed to a publicly accessible HTTPS environment on Render, backed by GitHub CI/CD, with zero UI redesign and complete mathematical and geotechnical preservation.

---

## 1. Live Public URLs

| Service / Purpose | Live Public HTTPS URL | Status | Response |
|---|---|---|---|
| **Primary Live Application (Render)** | https://parvat-netra.onrender.com | **LIVE** | HTTP 200 OK |
| **Edge Live Application (Vercel)** | https://silly-fermi.vercel.app | **LIVE** | HTTP 200 OK |
| **Vercel Production Health Probe** | https://silly-fermi.vercel.app/health | **LIVE** | status: UP, database: CONNECTED |
| **50m Geofence Evaluator (Vercel)** | https://silly-fermi.vercel.app/demo | **LIVE** | HTTP 200 OK (Interactive Sandbox) |
| **PAHAD Highest Risk Corridor (Vercel)** | https://silly-fermi.vercel.app/api/pahad/highest-risk-corridor | **LIVE** | HTTP 200 OK (26 Corridors) |

---

## 2. Live Verification Results

### 2.1 GET /health Probe
- Status: UP (HTTP 200 OK)
- Database Status: CONNECTED (PostgreSQL / Neon)
- Model Status: TRAINED_LIMITED_DATA
- Application: PARVAT NETRA
- Version: 3.1.0

### 2.2 GET /demo 50-Meter Geofence Evaluator
- LIVE high-accuracy GPS lock and HTTPS geolocation ready.
- Dynamic Haversine proximity reduction to active hazard centroid (27.0984 N, 88.4892 E).
- Evaluator simulation presets: 35m (INSIDE alert state) and 180m (OUTSIDE safe standoff).
- Isolated multichannel evaluator drill successfully dispatched with zero public leak risk.

### 2.3 POST /api/pahad/predict-event
- Status: SUCCESS (HTTP 200 OK)
- Model Version: PAHAD-v3.0.0-phase3
- CRI: 35.18 (Moderate)
- Physical FoS: 0.981 <= 1.0 (Conditionally unstable)
- Predictions: 6h (24.3%), 12h (28.0%), 24h (31.1%), 48h (32.8%)
- Top Drivers: Physical Stability Critical, Regional Rainfall Threshold Breach, Steep Hillslope Inclination.

---

## 3. Mobile Responsiveness & Console Audit (CP22 & CP23)
Automated Chrome DevTools testing confirmed seamless rendering and zero console errors across standard mobile viewports:
- **360 x 800 (Compact Android):** PASSED (Zero horizontal scroll, responsive telemetry cards)
- **390 x 844 (iPhone 12/13/14):** PASSED (Crisp layout, proper gauge scaling)
- **412 x 915 (Pixel / Galaxy Modern):** PASSED (Clean UI flow, full button accessibility)
- **Console Audit:** 0 fatal errors, 0 mixed content security warnings over HTTPS.

---

## 4. Staging Safety Invariants (CP19 & CP20)
All national emergency safety invariants are active in the staging environment:
1. `ENABLE_PUBLIC_DISPATCH=0`: Public siren and mass civilian notification gates strictly locked.
2. `SIREN_DRY_RUN=1`: Physical 130dB relays in software simulation mode only.
3. `PUBLIC_DEMO_TEST_ONLY=1`: Multichannel drills isolated to evaluator sandbox session journal.
4. `CAP_PRODUCTION_DISPATCH=0`, `SACHET_PRODUCTION_DISPATCH=0`, `CELL_BROADCAST_PRODUCTION=0`: Production agency broadcasts disabled.

---

## 5. Continuous Deployment Pipeline
Every push to the `staging` or `main` branch of https://github.com/dimpu-sashank2008/parvatnetra automatically triggers Render's Docker deployment pipeline, maintaining a live, continuously updated staging environment.
