#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_phase11m_snapshot.py
Authoritative Runtime Snapshot Generator for Phase 11M (Pre-Submission Freeze).
Evaluates all 26 canonical corridors across the 8 NER states via /api/pahad/highest-risk-corridor.
Saves reports/PHASE11M_FINAL_RUNTIME_SNAPSHOT.json.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    print("[PHASE 11M] Initializing Flask test client...")
    from app import app

    client = app.test_client()
    print("[PHASE 11M] Calling /api/pahad/highest-risk-corridor?force_refresh=1 ...")
    start_t = time.time()
    res = client.get('/api/pahad/highest-risk-corridor?force_refresh=1')
    elapsed = time.time() - start_t
    print(f"[PHASE 11M] Response received in {elapsed:.2f}s, status={res.status_code}")

    if res.status_code != 200:
        print(f"[ERROR] API returned status {res.status_code}: {res.data.decode('utf-8')}")
        return

    data = res.get_json()
    top = data.get("highest_risk_corridor", {})
    ranked = data.get("ranked_corridors", [])

    print(f"[PHASE 11M] Evaluated {len(ranked)} canonical corridors.")
    print(f"[PHASE 11M] Top Corridor: {top.get('id')} ({top.get('name')})")
    print(f"            State: {top.get('state')}, District: {top.get('district')}")
    print(f"            CRI: {top.get('cri')}, Band: {top.get('risk_band')}, FoS: {top.get('fos')}")
    print(f"            Event Likelihood: {top.get('event_probability')}, Rain 24h: {top.get('rainfall_24h')} mm")
    print(f"            Provenance: {top.get('provenance')}, Data Quality: {top.get('data_quality_level')}")

    corridor_snapshot = []
    now_iso = datetime.now(timezone.utc).isoformat()
    for rank, c in enumerate(ranked, 1):
        item = {
            "rank": rank,
            "id": c.get("id"),
            "name": c.get("name"),
            "state": c.get("state"),
            "district": c.get("district"),
            "highway": c.get("highway"),
            "lat": c.get("lat"),
            "lon": c.get("lon"),
            "cri": c.get("cri"),
            "risk_band": c.get("risk_band"),
            "fos": c.get("fos"),
            "fos_status": c.get("fos_status"),
            "event_probability": c.get("event_probability"),
            "probability_level": c.get("probability_level"),
            "rainfall_24h": c.get("rainfall_24h"),
            "data_quality_level": c.get("data_quality_level"),
            "provenance": c.get("provenance", "[LIVE / MODELLED]"),
            "timestamp": now_iso
        }
        corridor_snapshot.append(item)

    snapshot_report = {
        "metadata": {
            "phase": "PHASE 11M",
            "standard": "Smart India Hackathon (SIH) 2026 Pre-Submission Freeze",
            "classification": "FINAL RELEASE CANDIDATE RUNTIME SNAPSHOT",
            "generated_at_utc": now_iso,
            "total_canonical_corridors": len(ranked),
            "ranking_strategy": "highest_cri_desc, lowest_fos_asc, alphabetical_id",
            "highest_risk_corridor_id": top.get("id"),
            "highest_risk_corridor_name": top.get("name"),
            "highest_risk_corridor_state": top.get("state"),
            "highest_risk_corridor_district": top.get("district"),
            "highest_risk_corridor_cri": top.get("cri"),
            "highest_risk_corridor_band": top.get("risk_band"),
            "highest_risk_corridor_fos": top.get("fos"),
            "highest_risk_corridor_event_probability": top.get("event_probability")
        },
        "highest_risk_corridor": top,
        "ranked_corridors": corridor_snapshot
    }

    out_path = os.path.join("reports", "PHASE11M_FINAL_RUNTIME_SNAPSHOT.json")
    os.makedirs("reports", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_report, f, indent=2)

    print(f"\n[PHASE 11M] Final runtime snapshot written successfully to {out_path} ({len(json.dumps(snapshot_report))} bytes)")

if __name__ == "__main__":
    main()
