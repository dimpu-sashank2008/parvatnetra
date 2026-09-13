# PARVAT NETRA / PAHAD AI — Phase 5E Mobile Architecture & API Integration Audit

**Document**: `PHASE5E_MOBILE_AUDIT.md`  
**Phase**: Phase 5E — Flutter Mobile Field + Authority Application  
**Date**: 2026-09-10  
**Authority**: PARVAT NETRA / PAHAD AI Core Engineering Team  
**Problem Statement**: SIH ID 26001 (Ministry of Development of North Eastern Region)

---

## 1. Executive Summary

This audit evaluates the current state of the `parvat_netra_mobile/` Flutter application, its local database layer, offline capabilities, synchronization mechanisms, and its integration alignment with the canonical Phase 5B/5C/5D PAHAD AI backend APIs.

The mobile application is strictly an **operational field client** of the centralized PAHAD AI platform. It does not compute independent machine learning predictions or rewrite physics algorithms locally.

---

## 2. Mobile File Audit Status

| Component | File Path | Current Status | Findings & Implementation Actions |
| :--- | :--- | :--- | :--- |
| **Dependencies** | `pubspec.yaml` | **WORKING** | Contains modern dependencies: `flutter_map: ^6.1.0`, `sqflite: ^2.3.0`, `path_provider: ^2.1.2`, `connectivity_plus: ^5.0.2`, `geolocator: ^11.0.0`, `http: ^1.2.0`, `cached_network_image: ^3.3.1`, `latlong2: ^0.9.0`. Dart SDK >=3.0.0 <4.0.0. |
| **Database Manager** | `lib/database_helper.dart` | **WORKING** | SQLite v2 schema implemented: `field_reports`, `cached_snapshots`, `cached_alerts`, legacy `offline_reports`. Thread-safe CRUD and queue metrics (`getQueueCounts`) operational. |
| **Sync Engine** | `lib/sync_service.dart` | **PARTIAL** | Implements exponential backoff with jitter and network connectivity detection. Currently targets legacy `/api/sync/field-reports`; requires alignment with canonical `/api/sync/push` and `/api/sync/pull`. |
| **Offline Tiles** | `lib/offline_map_provider.dart` | **WORKING** | Implements `CachedTileProvider` utilizing `flutter_cache_manager` disk LRU cache for zero-network tile viewing and transparent placeholders. |
| **API Client** | `lib/services/api_client.dart` | **PARTIAL** | Implements HTTP client with timeouts and error wrapping. Needs typed methods for `/api/pahad/live-inference`, `/api/pahad/forecast`, `/api/pahad/data-status`, `/api/pahad/observations/latest`, and `/api/sync/*`. |
| **Data Models** | `lib/models/` | **PARTIAL** | `FieldReport`, `AlertModel`, `PahadRiskSnapshot`, and `ShelterModel` exist. Missing typed models for `Forecast`, `DataStatus`, `SyncStatus`, `RouteModel`, and `SectorSnapshot`. |
| **User Screens** | `lib/screens/` | **PARTIAL** | `field_operations_screen.dart`, `authority_mode_screen.dart`, `citizen_mode_screen.dart`, `edge_test_screen.dart`, `demo_mode_screen.dart` exist. Role-aware authentication, dedicated Forecast horizon screen, Explanation viewer, and Data Status dashboard need formalization. |
| **Localization** | `lib/services/localization_service.dart` | **WORKING** | Full support for 6 Himalayan languages: English (`en`), Hindi (`hi`), Nepali (`ne`), Bhutia (`bh`), Lepcha (`lp`), and Assamese (`as`). Key dictionary includes UI and hazard terms. |
| **Location Telemetry**| `lib/services/location_service.dart` | **WORKING** | GPS integration via `geolocator` with accuracy thresholds, mock coordinate detection, and fallback to pilot centroid (NH-10 Km 48). |
| **Push Notification**| `lib/services/push_notification_service.dart` | **WORKING (STUB)**| Notification abstraction layer with clear disclaimer that live FCM/APNs requires registered device tokens. |

---

## 3. Backend API Contract Alignment Audit

| Endpoint | Method | Backend Status | Mobile Status | Gap / Required Action |
| :--- | :--- | :--- | :--- | :--- |
| `/api/pahad/live-inference` | `GET`, `POST` | **WORKING** | **MISSING** | Mobile must consume live multimodal inference (FoS, event probability, CRI, confidence, provenance) for the current user location. |
| `/api/pahad/forecast` | `GET`, `POST` | **WORKING** | **MISSING** | Mobile must consume multi-horizon predictions (6h, 12h, 24h, 48h) without locally simulating forecast probabilities. |
| `/api/pahad/data-status` | `GET` | **WORKING** | **MISSING** | Mobile must query live telemetry stream states (`weather`, `seismic`, `satellite`, `terrain`, `iot`) and provenance summary. |
| `/api/pahad/observations/latest` | `GET` | **WORKING** | **MISSING** | Mobile should display latest verified sensor observations (rain, pore pressure, tilt) per sector. |
| `/api/sync/push` | `POST` | **WORKING** | **PARTIAL** | Mobile `SyncService` must push queued `FieldReport` payloads and receive server sync envelopes with acknowledgements. |
| `/api/sync/pull` | `GET` | **WORKING** | **MISSING** | Mobile must pull server-authoritative alerts, critical sector risk updates, road blockages, and shelters upon reconnection. |
| `/api/sync/status` | `GET` | **WORKING** | **MISSING** | Mobile should verify backend sync health, reconciled count, and offline bundle version. |

---

## 4. Role-Aware Permission Matrix Audit

| Role | Incident Reporting | View Risk & Forecast | View Alerts | Acknowledge Alerts | Verify Citizen Incidents | Safe Evacuation Routing | System Data Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **PUBLIC** | Yes | Yes (General) | Yes (Active) | No | No | Yes | No |
| **FIELD_OPERATOR**| Yes | Yes (Detailed) | Yes | Yes | Yes | Yes | Yes |
| **AUTHORITY** | Yes | Yes (Full) | Yes | Yes | Yes (Approve/Reject) | Yes | Yes |
| **ADMIN** | Yes | Yes (Full) | Yes | Yes | Yes (All) | Yes | Yes |

---

## 5. Summary Audit Classification

- **Overall Working Components**: 6
- **Partial Components Requiring Update**: 4
- **Missing API Integrations / Screens**: 3
- **Primary Phase 5E Focus**:
  1. Add typed data models: `Forecast`, `DataStatus`, `SyncStatus`, `RouteModel`, `SectorSnapshot`.
  2. Upgrade `ApiClient` to consume canonical Phase 5B/5C/5D endpoints (`/api/pahad/live-inference`, `/api/pahad/forecast`, `/api/pahad/data-status`, `/api/sync/push`, `/api/sync/pull`).
  3. Integrate role-aware authentication (`AuthService`) with secure local session state (PUBLIC, FIELD_OPERATOR, AUTHORITY, ADMIN).
  4. Build modular mobile views: Primary PAHAD Risk Dashboard, Multi-Horizon Forecast view, Active Alerts triage with expiry suppression, Safe Routing with `[OFFLINE ROUTE]` handling, Incident Verification for officers, and Data Status dashboard.
  5. Expand Dart unit tests in `test/test_mobile_core.dart` and verify contract compatibility with Python test suites.
