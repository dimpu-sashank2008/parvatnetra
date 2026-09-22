# PARVAT NETRA • PAHAD AI — PHASE V5.3
# 3D FAILURE DEGRADATION & ERROR BOUNDARY REPORT

**Document ID**: `PN-DOC-V5_3-006`  
**Classification**: Resilience & Error Handling Specification  
**Version**: `5.3.0`  
**Date**: `2026-09-21`  

---

## 1. Failure Modes & Degradation Hierarchy

The God's Eye 3D implementation isolates all WebGL and network hazards to prevent cascading failure in the operational 2D dashboard:

```
+──────────────────────────────────────────────────────────+
│ Failure Scenario 1: CDN Unavailable / Offline Mode       │
├──────────────────────────────────────────────────────────┤
│ Catch: script.onerror catches failed CesiumJS fetch      │
│ UI Response: Renders polite error overlay with 1-click   │
│              button: "← Return to Standard 2D Map"      │
│ Result: 2D Leaflet map continues running unaffected.    │
+──────────────────────────────────────────────────────────+
│ Failure Scenario 2: WebGL Context Creation Failure       │
├──────────────────────────────────────────────────────────┤
│ Catch: Try/catch block wraps Cesium.Viewer initialization│
│ UI Response: Displays WebGL requirement warning.         │
│ Result: Automatically redirects user back to 2D Leaflet. │
+──────────────────────────────────────────────────────────+
│ Failure Scenario 3: Missing 3D Tiles Credentials         │
├──────────────────────────────────────────────────────────┤
│ Detection: Empty GOOGLE_MAPS_API_KEY                     │
│ Graceful Fallback: Activates OPEN_TERRAIN_FALLBACK       │
│ Result: Clean 3D globe with truthful provider badge.     │
+──────────────────────────────────────────────────────────+
```

---

## 2. Leaflet Viewport Invalidation Resilience

When exiting 3D mode back to 2D:
- The Leaflet container `#map` is restored to `display: block`.
- An immediate `map.invalidateSize()` call executes.
- A secondary deferred `map.invalidateSize()` call executes at $150\text{ ms}$ to allow browser layout recalculations to finalize.
- Verified: Zero blank tiles or distorted vector layers observed upon return.
