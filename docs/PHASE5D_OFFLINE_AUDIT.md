# PARVAT NETRA / PAHAD AI — Phase 5D Offline Architecture Audit

**Document**: `PHASE5D_OFFLINE_AUDIT.md`  
**Phase**: Phase 5D — Offline-First Maps + Resilient Synchronization  
**Date**: 2026-09-10  
**Status**: AUDIT COMPLETE  
**Auditor**: PARVAT NETRA / PAHAD AI Core Engineering Team  

---

## 1. Executive Summary

This audit evaluates the offline resilience, caching policies, local storage, geospatial packaging, and synchronization capabilities across the PARVAT NETRA web platform and mobile subsystem.

### Overall Readiness Classification

| Component | Target Location | Status | Summary |
| :--- | :--- | :--- | :--- |
| **Static Offline Cache** | `static/pahad_offline_cache.json` | **WORKING** | 817 lines; 18 critical sectors, highway corridors, 10 shelters, emergency contacts. |
| **Pre-bundled Core GIS** | `static/data/offline_core_package.json` | **WORKING** | 2,103 lines, 66 features (admin boundaries, strategic roads, hydrology, sectors, shelters, landslides). |
| **PWA Service Worker** | `static/sw.js` | **WORKING** | Pre-caching, Cache-First static, Stale-While-Revalidate GIS, Network-First API fallback, auth bypass. |
| **Web App Manifest** | `static/manifest.json` | **WORKING** | PWA standalone mode, dark theme `#070B10`, icons 192/512, category declarations. |
| **Network State Machine** | `static/js/network_state.js` | **WORKING** | 4-state engine (`ONLINE`, `DEGRADED`, `OFFLINE`, `SYNCING`), heartbeat `/api/health`, data age calculation. |
| **IndexedDB Local Store** | `static/js/local_store.js` | **PARTIAL** | Stores snapshots, weather, seismic, map packages, sync queue. Needs versioned schema migration & Phase 5B snapshot schema. |
| **Client Sync Manager** | `static/js/sync_manager.js` | **WORKING** | Offline report queue, idempotent UUID generation, auto-sync on reconnect, exponential backoff. |
| **Offline Package Mgr** | `static/js/offline_manager.js` | **WORKING** | Offline manifest discovery, SHA-256 verification, IndexedDB package install/delete. |
| **Server Sync Service** | `services/sync_service.py` | **PARTIAL** | Deduplication and batch sync working; lacks canonical push/pull sync endpoints and telemetry delta sync. |
| **Sync REST APIs** | `app.py` (`/api/sync/*`) | **PARTIAL** | `POST /api/sync/field-reports` exists; `/api/sync/push`, `/api/sync/pull`, `/api/sync/status` are **MISSING**. |
| **Geospatial Manifest** | `engine/geospatial_registry.py` | **PARTIAL** | `GET /api/geospatial/offline-manifest` works; needs Section 15 bundle versioning & checksum envelope. |
| **Offline Routing** | `engine/pahad_routing.py` | **PARTIAL** | Mountain corridors and bypass matrix exist; needs dedicated offline routing endpoint and client runner. |
| **Mobile SQLite & Sync** | `parvat_netra_mobile/` | **WORKING** | SQLite schema v2 (`field_reports`, `cached_snapshots`, `cached_alerts`), `sync_service.dart` with backoff. |
| **Alert Expiry Guard** | Web & API | **PARTIAL** | Alerts are stored; explicit offline marking of expired warnings needs formal enforcement. |

---

## 2. Detailed Component Breakdown

### 2.1 Static Offline Cache (`static/pahad_offline_cache.json`)
- **Status**: `WORKING`
- **Contents**:
  - `critical_sectors`: 18 monitored sectors (e.g. `SK-NH10-KM48`, `SK-SINGTAM-01`, `MZ-HUNTHAR-01`, `MN-TUPUL-RLY`) with coordinates, geology, hazard rating, and instrumentation.
  - `strategic_corridors`: NH-10, NH-717A, NH-29, NH-06, NH-13, NH-37 with bypass options and jurisdiction.
  - `emergency_shelters`: 10 shelters with GPS coordinates, capacities (450–4,000 people), helipad availability, and emergency satellite phone lines.
  - `emergency_contacts`: 24/7 control rooms (NDRF, BRO Swastik/Sewak/Pushpak/Vartak, SDMAs).

### 2.2 Pre-bundled Core Geospatial Package (`static/data/offline_core_package.json`)
- **Status**: `WORKING`
- **Features**: 66 vector GeoJSON features across 6 layers:
  - 8 State Administrative Boundary Polygons (Sikkim, Meghalaya, Assam, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura).
  - 7 Strategic Highway Lines (NH-10, NH-717A, NH-29, NH-6, NH-102, NH-37, NH-8).
  - 4 Major Himalayan River Polylines (Teesta, Rangeet, Brahmaputra, Barak).
  - 20 PAHAD AI Hill Sectors.
  - 10 Emergency Evacuation Shelters.
  - 17 Historical Landslide Scars & Ground Truth Validation Points.
- **Licensing Compliance**: Vector geometry derived from public administrative records and Survey of India boundary approximations. Zero copyrighted raster tiles.

### 2.3 PWA Service Worker (`static/sw.js`)
- **Status**: `WORKING`
- **Cache Strategies**:
  - `CACHE-FIRST`: Static assets, fonts, CSS, JS, `/static/data/offline_core_package.json`.
  - `STALE-WHILE-REVALIDATE`: Geospatial manifest and historical metadata.
  - `NETWORK-FIRST`: Dynamic prediction and telemetry endpoints (`/api/pahad/*`, `/api/weather/*`, `/api/seismic/*`, `/api/alerts/*`).
  - `BYPASS`: Auth, login, logout, decision authorization (`/api/decisions/*/authorize`), and siren dispatch.
- **Enhancement Needed**: Add Phase 5C endpoints (`/api/pahad/observations/*`) and new Phase 5D sync endpoints to appropriate cache/bypass rules.

### 2.4 IndexedDB Local Storage (`static/js/local_store.js`)
- **Status**: `PARTIAL`
- **Current Stores**: `pahad_snapshots`, `weather_cache`, `seismic_cache`, `active_alerts`, `map_packages`, `sync_queue`, `user_preferences`.
- **Gaps Identified**:
  1. No versioned database schema migration mechanism if stores change.
  2. The snapshot schema must explicitly store Phase 5B/5C attributes: `sector_id, timestamp, CRI, risk_band, FoS, event_probability, confidence, model_version, data_quality, source_status`.
  3. Alert records must store expiry timestamps and evaluate whether an alert has expired.

### 2.5 Server Synchronization Engine & Endpoints
- **Status**: `PARTIAL`
- **Existing**: `services/sync_service.py` has `sync_single_report()` and `sync_batch_reports()` with memory registry deduplication. `app.py` has `POST /api/sync/field-reports`.
- **Gaps Identified**:
  1. Missing standard `POST /api/sync/push` endpoint returning the formal envelope (`sync_id`, `started_at`, `completed_at`, `records_uploaded`, `records_failed`, `status`, `acknowledgements`).
  2. Missing `GET /api/sync/pull` endpoint allowing clients to pull server-authoritative state changes (alerts, snapshots, road blockages) since a timestamp.
  3. Missing `GET /api/sync/status` returning operational sync metrics.

### 2.6 Offline Routing Engine
- **Status**: `PARTIAL`
- **Existing**: `engine/pahad_routing.py` has corridor status, bypass calculations (with GVW limits), and nearest shelter calculations via Haversine.
- **Gaps Identified**:
  1. No client-side offline route runner in JavaScript for zero-network execution in the browser.
  2. No unified API endpoint explicitly returning `[OFFLINE ROUTE]` or `OFFLINE ROUTE` provenance when running in offline or degraded mode.

---

## 3. Required Action Plan for Phase 5D

1. **`docs/PHASE5D_SYNC_POLICY.md`**: Create authoritative conflict resolution specification.
2. **`services/sync_service.py` & `app.py`**:
   - Implement `POST /api/sync/push`, `GET /api/sync/pull`, `GET /api/sync/status`.
   - Support bidirectional delta sync with exponential backoff and audit logs.
3. **`engine/geospatial_registry.py`**:
   - Extend `export_manifest()` with `bundle_version`, `source_versions`, `dataset_versions`, `model_version`, and SHA-256 checksums.
4. **`services/offline_routing_service.py` & `static/js/offline_routing.js`**:
   - Implement offline routing engine using local vector road network and shelters.
   - Tag all offline-calculated paths as `OFFLINE ROUTE`.
5. **`static/js/local_store.js`**:
   - Upgrade IndexedDB schema to Version 2 with explicit migration handlers.
   - Enforce Phase 5B snapshot schema and alert expiry checks.
6. **Testing Suite**:
   - Implement all 7 requested test suites covering web, storage, sync, APIs, routing, resilience, and mobile contracts.
