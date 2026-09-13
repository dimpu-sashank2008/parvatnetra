# PARVAT NETRA • PAHAD AI — PHASE 7H OFFLINE OPERATION REPORT
**Autonomous Offline Capabilities, Edge Buffering, Field Responders & Tactical Routing**
**Corridor**: `CORR-NH10-SIKKIM-KM48` (Pakyong District, Sikkim Lifeline)
**Evaluation Date**: September 11, 2026
**Operational Status**: `FIELD_RESILIENCE_VERIFIED`

---

## 1. Zero-Connectivity Operating Model

In high-relief Himalayan terrain, continuous broadband connectivity is a statistical exception rather than a rule. Monsoon deluges, landslides, and seismic events regularly sever fiber backhauls, topple microwave towers, and overload cellular base stations.

Phase 7H validates that **PARVAT NETRA** and **PAHAD AI** maintain complete operational capability when entirely cut off from the cloud and external internet.

```
                    ┌──────────────────────────────────────────────┐
                    │            INTERNET BLACKOUT ZONE            │
                    │                                              │
┌──────────────┐    │   ┌────────────────┐    ┌────────────────┐   │
│  In-Situ     │    │   │  Edge Gateway  │    │  Mobile Client │   │
│ Geotechnical │───►│   │  (EdgeStore    │◄──►│  (Flutter      │   │
│ Telemetry    │RF  │   │   SQLite DB)   │LoRa│   Offline DB)  │   │
└──────────────┘    │   └────────────────┘    └────────────────┘   │
                    │           │                      │           │
                    │           ▼                      ▼           │
                    │   ┌────────────────┐    ┌────────────────┐   │
                    │   │ Local Physics  │    │ Offline Vector │   │
                    │   │ Mohr-Coulomb   │    │ Road Routing   │   │
                    │   │ FoS Classifier │    │ (NH-10/NH-717A)│   │
                    │   └────────────────┘    └────────────────┘   │
                    └──────────────────────────────────────────────┘
                                        │
                         WAN RESTORED   │ Idempotent Sync
                                        ▼
                    ┌──────────────────────────────────────────────┐
                    │    PARVAT NETRA CENTRAL CLOUD PLATFORM       │
                    │    (PostgreSQL / ObservationStore / EOC)     │
                    └──────────────────────────────────────────────┘
```

---

## 2. Edge Gateway Autonomous Buffering (CP 7H-01, 7H-02, 7H-09)

### 2.1 Storage & Schema Persistence
- **Local Database**: Persistent embedded SQLite database (`data/edge/edge_store.db`).
- **Telemetry Ingestion**: Decoded in-situ sensor frames (piezometer pore pressure, borehole inclinometer tilt, rain gauge intensity) are written synchronously to local disk before RF ACK is emitted.
- **Sync Queue**: Each observation registers a pending upload record in `edge_sync_queue`.
- **Integrity**: 16-bit CRC checksum validated on every incoming LoRaWAN/RF packet.

### 2.2 Storage Boundary & Quarantine Policy
- **Capacity**: 100 MB dedicated circular edge partition (~200,000 compressed telemetry packets).
- **Overflow Policy**: `OLDEST_DROP_WITH_QUARANTINE`. If the gateway remains disconnected past 50,000 queued packets, oldest uncritical heartbeats roll over into quarantine log to preserve high-severity anomaly telemetry.
- **Power Telemetry**: Tracks battery state (`NORMAL`, `BATTERY_LOW`, `BATTERY_CRITICAL`, `SHUTDOWN`, `RECOVERED`). Under critical battery ($<10\%$), the gateway executes a clean SQLite flush and safe hibernation.

---

## 3. Mobile Field Client Offline Autonomy (CP 7H-03)

### 3.1 Pre-Packaged Offline Manifest
Field officers and disaster response teams (BRO, SDRF, NDRF) cache local offline bundles containing:
1. **Critical Sector Geo-Boundary**: 8 critical Himalayan corridors with spatial polygons.
2. **Emergency Relief Hubs**: Geocoded shelter locations, capacities, and helipad facilities.
3. **Arterial Highway Corridors**: Strategic bypass networks with Gross Vehicle Weight (GVW) tiers.
4. **Active Evacuation Alerts**: Server-authoritative advisory bulletins cached with timestamps.

### 3.2 Offline Field Report Submission
- Responders record field observations (tension cracks, rockfall, culvert blockages) completely offline.
- Reports generate deterministic client-side UUIDs (`PN-MOBILE-OFFLINE-XXXX`).
- GPS coordinates are validated against the North-Eastern Himalayan bounding box ($20.0^\circ\text{N} - 30.0^\circ\text{N}$, $87.0^\circ\text{E} - 98.0^\circ\text{E}$).
- Reports remain locally queued until network reconnection.

### 3.3 Idempotent Reconciliation Protocol
- On backhaul reconnection, mobile batches upload via `POST /api/sync/field-reports`.
- Server deduplicates using client tokens (`local_id`). Re-transmissions report `"duplicate": true` without creating redundant server incidents.

---

## 4. Offline Map Caching & Tactical Routing (CP 7H-04, 7H-05, 7H-19)

### 4.1 Vector Road Network & Routing Engine
`OfflineRoutingService` operates deterministically with zero third-party map APIs:
- **Corridor Profiles**:
  - `FASTEST`: Optimizes for emergency transit time along primary highways.
  - `SHORTEST`: Minimizes road distance using steep rural links where passable.
  - `SAFEST`: Hazard-aware cost optimization applying severe time penalties near active landslide zones and degrading safety scores.
- **Severed Lifeline Bypass**:
  - NH-10 blockage at Km 48 triggers automatic detour via **NH-717A Strategic Bypass** (Bagrakote - Labha - Algarah - Reshi - Rhenock - Pakyong).
  - Bridge closure on Teesta axis triggers fail-safe destination unreachable alert (`UNREACHABLE`), guiding responders to the nearest local high-ground emergency relief hub.
- **Data Freshness Tagging**:
  - Routes generated during blackouts carry explicit provenance badges: `[OFFLINE ROUTE / CACHED]` or `[OFFLINE ROUTE / STALE]`.

### 4.2 Multilingual Field UI Resilience
Frontend localization (`static/js/i18n.js`) provides 100% offline parity across 6 Himalayan languages:
- **English** (`en`)
- **हिन्दी** (`hi`)
- **नेपाली** (`ne`)
- **ལྷོ་སྐད / Bhutia** (`bh`)
- **རོང་རིང / Lepcha** (`lp`)
- **অসমীয়া / Assamese** (`as`)
