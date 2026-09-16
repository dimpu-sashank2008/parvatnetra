# PARVAT NETRA • PAHAD AI — PHASE 12D GIS DEMO & STABILITY REPORT

**Audit Date**: 2026-09-16T07:42:12.013979+00:00  
**Git Commit**: `dd9e57dc6452e0a70ad98731de0c536af8e50cb0`  
**Test Suite**: `tests/test_ner_gis_default_view.py` (`9/9 PASSED`)  

---

## 1. Regional Northeast India (NER) Default Extent

The GIS map initializes with a comprehensive regional view spanning all 8 Northeastern states:
- **Arunachal Pradesh**
- **Assam**
- **Manipur**
- **Meghalaya**
- **Mizoram**
- **Nagaland**
- **Sikkim**
- **Tripura**

### 1.1 Verified Bounding Box Invariants
- `window.NER_BOUNDS = L.latLngBounds([[21.8, 88.0], [29.5, 97.5]])`
- Default regional fit applied via `map.fitBounds(window.NER_BOUNDS, { padding: [20, 20] })`.
- **Zero Auto-Zoom Prohibited Tropes Verified**:
  - The map DOES NOT auto-zoom to Bhalukpong.
  - The map DOES NOT auto-zoom to NH-10.
  - The map DOES NOT auto-zoom to highest-risk corridor on initial load.
  - The map DOES NOT auto-zoom to first marker or cluster.
  - The map DOES NOT auto-zoom to user GPS location.

### 1.2 View State Tracking & Viewport Stability
- View states tracked via `window.pahadMapViewState`:
  1. `INITIAL_VIEW`: Applied on DOM ready.
  2. `NER_OVERVIEW`: Restored whenever user clicks the "Reset" button.
  3. `CORRIDOR_VIEW`: Applied only on explicit user corridor selection.
- **Background Polling Isolation**: The 10-second polling cycle calls `onCorridorSelectionChanged(sectorId, false)`. Passing `shouldZoom=false` completely eliminates viewport jumping or map repositioning during live operations.

### 1.3 Risk Evolution vs Risk Evaluation Separation
- **Risk Evolution**: Integrated as an on-map temporal animation controller (`static/js/pahad_gis_animation.js`) rendering historical halo expansions without changing zoom.
- **Risk Evaluation**: Rendered as a distinct analytical slide-out modal for geotechnical engineering stress analysis. The two functions are strictly unmerged.
