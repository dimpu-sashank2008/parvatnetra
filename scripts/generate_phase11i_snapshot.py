#!/usr/bin/env python3
"""
scripts/generate_phase11i_snapshot.py
Authoritative Runtime Snapshot Generator for Phase 11I.
Evaluates all 26 canonical corridors across the 8 NER states via /api/pahad/highest-risk-corridor.
Saves reports/PHASE11I_RUNTIME_SNAPSHOT.json.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    print("[PHASE 11I] Initializing Flask test client...")
    from app import app

    client = app.test_client()
    print("[PHASE 11I] Calling /api/pahad/highest-risk-corridor?force_refresh=1 ...")
    start_t = time.time()
    res = client.get('/api/pahad/highest-risk-corridor?force_refresh=1')
    elapsed = time.time() - start_t
    print(f"[PHASE 11I] Response received in {elapsed:.2f}s, status={res.status_code}")

    if res.status_code != 200:
        print(f"[ERROR] API returned status {res.status_code}: {res.data.decode('utf-8')}")
        return

    data = res.get_json()
    top = data.get("highest_risk_corridor", {})
    ranked = data.get("ranked_corridors", [])

    print(f"[PHASE 11I] Evaluated {len(ranked)} canonical corridors.")
    print(f"[PHASE 11I] Top Corridor: {top.get('id')} ({top.get('name')})")
    print(f"            State: {top.get('state')}, CRI: {top.get('cri')}, Band: {top.get('risk_band')}")
    print(f"            FoS: {top.get('fos')}, Rain 24h: {top.get('rainfall_24h')} mm, P(event): {top.get('event_probability')}")
    print(f"            Provenance: {top.get('provenance')}, Data Quality: {top.get('data_quality_level')}")

    print("\n--- ALL 26 CANONICAL CORRIDORS RANKED BY HAZARD (CRI desc, FoS asc, ID asc) ---")
    corridor_snapshot = []
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
            "risk_trend": c.get("risk_trend"),
            "authority_action": c.get("authority_action"),
            "provenance": c.get("provenance", "[LIVE / MODELLED]")
        }
        corridor_snapshot.append(item)
        print(f"{rank:2d}. {c['id']:<16} | CRI: {c.get('cri', 0):>5.2f} ({c.get('risk_band',''):<9}) | FoS: {c.get('fos', 0):>6.4f} | Rain: {c.get('rainfall_24h', 0):>5.1f}mm | P(ev): {c.get('event_probability', 0):>5.4f} | {c.get('state')}")

    snapshot_report = {
        "metadata": {
            "report_phase": "PHASE 11I",
            "standard": "SIH 2026 Pre-Submission Hardening",
            "classification": "AUTHORITATIVE RUNTIME SNAPSHOT",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_canonical_corridors": len(ranked),
            "ranking_strategy": "highest_cri_desc, lowest_fos_asc, alphabetical_id",
            "top_corridor_id": top.get("id"),
            "top_corridor_cri": top.get("cri"),
            "top_corridor_band": top.get("risk_band"),
            "top_corridor_fos": top.get("fos")
        },
        "highest_risk_corridor": top,
        "ranked_corridors": corridor_snapshot
    }

    out_path = os.path.join("reports", "PHASE11I_RUNTIME_SNAPSHOT.json")
    os.makedirs("reports", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_report, f, indent=2)

    print(f"\n[PHASE 11I] Authoritative snapshot written successfully to {out_path} ({len(json.dumps(snapshot_report))} bytes)")

if __name__ == "__main__":
    main()
