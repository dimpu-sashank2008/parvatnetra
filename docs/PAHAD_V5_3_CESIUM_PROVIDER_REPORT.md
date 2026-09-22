# PARVAT NETRA • PAHAD AI — PHASE V5.3
# CESIUM 3D PROVIDER HIERARCHY & CREDENTIALED FALLBACK AUDIT

**Document ID**: `PN-DOC-V5_3-003`  
**Classification**: 3D Provider Architecture & Security Audit  
**Version**: `5.3.0`  
**Date**: `2026-09-21`  

---

## 1. Provider Selection Protocol

Under the Zero-Fabrication Directive, PARVAT NETRA never generates synthetic connectivity or displays mock credentials. The 3D engine evaluates terrain and 3D tile providers in strict order:

```
[User Selects God's Eye 3D]
               │
               ▼
   Is GOOGLE_MAPS_API_KEY Configured?
   ├── YES ──► Instantiate Google Photorealistic 3D Tileset
   │           Badge: [3D PROVIDER: GOOGLE PHOTOREALISTIC 3D TILES]
   │
   └── NO ──► Is CESIUM_ION_TOKEN Configured?
               ├── YES ──► Instantiate Cesium World Terrain + Sentinel-2
               │           Badge: [3D PROVIDER: CESIUM WORLD TERRAIN]
               │
               └── NO ──► Instantiate Open Terrain 3D Fallback (Ellipsoid + CartoDB)
                           Badge: [3D PROVIDER: TERRAIN 3D FALLBACK (AUTH_REQUIRED FOR GOOGLE 3D TILES)]
```

---

## 2. Current Provider Audit Ledger

| Provider Identifier | Capability | Requirement | Current Status | Active In V5.3 |
| :--- | :--- | :--- | :--- | :--- |
| `GOOGLE_PHOTOREALISTIC_3D` | 3D mesh building & topography | `GOOGLE_MAPS_API_KEY` | `AUTH_REQUIRED` | No |
| `CESIUM_WORLD_TERRAIN` | Global elevation model & water mask | `CESIUM_ION_TOKEN` | `AUTH_REQUIRED` | No |
| `OPEN_TERRAIN_FALLBACK` | CartoDB Dark on WGS84 Ellipsoid | None (Public Open Tiles) | `ACTIVE` | **YES** |

---

## 3. Seamless Key Injection

When deployment authorities obtain institutional Google Maps API keys or Cesium Ion tokens:
1. Populate `GOOGLE_MAPS_API_KEY` in `.env`.
2. Reload or restart the application.
3. `/api/gods-eye/config` automatically detects the key, updates `provider_status: CONFIGURED`, and activates Google 3D Tiles with zero code modification.
