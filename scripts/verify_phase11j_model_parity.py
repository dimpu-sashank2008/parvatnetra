#!/usr/bin/env python3
"""
scripts/verify_phase11j_model_parity.py
Verifies bit-for-bit SHA-256 parity of all model artifacts against Phase 11I baseline.
Saves reports/PHASE11J_MODEL_ARTIFACT_PARITY.json.
"""

import os
import json
import hashlib
from datetime import datetime, timezone

BASELINE_HASHES = {
    "fos_predictor.pkl": "21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c",
    "pahad_event_calibrator.pkl": "f3a72b9eb9340990a4b4585799f438d27158d09002b948728f5eae41dbc1b1f8",
    "pahad_event_model.pkl": "d2094eae9ee6906f5197af5b2fdeb671d6a571080c7f63985b92b95c82ede938",
    "pahad_event_model_6h.pkl": "e864b26edb1e708aac4ec5c2d95d8c3088ba6310a3b9e79586a093c70e06270e",
    "pahad_event_model_12h.pkl": "04c2eb5469c4b8a14d0e99cb71380430c695f858cb7e349e78658f335ab24698",
    "pahad_event_model_24h.pkl": "84cd808a6196cdd5f330756a6b4007234bd9ae7a73d9505cd428ac7589545831",
    "pahad_event_model_48h.pkl": "61e1f8aff5f3f954560bbeb88cd8ae94e27134ec2e9cfc18a5004bf419f86093",
    "pahad_fos_model.pkl": "d1b9e91db79d3292fd318c73aaba4b3d5caf0a1119e5a698b24f68a19e1de673",
    "pahad_event_metadata.json": "9f408b7acb5c77f1a124fcad5e1898cdc42549f855ac4c45e44d89aebc62e77f",
    "pahad_event_metrics.json": "8bc174735d5362dd1662b84b918b261a4da720c0be5a27847f5e161fe034d44d"
}

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    models_dir = os.path.join(root, "models")
    results = {}
    all_pass = True

    print(f"[PHASE 11J] Verifying {len(BASELINE_HASHES)} model artifacts against baseline...")
    for filename, expected_hash in BASELINE_HASHES.items():
        filepath = os.path.join(models_dir, filename)
        if not os.path.exists(filepath):
            results[filename] = {"status": "MISSING", "expected": expected_hash, "actual": None}
            all_pass = False
            print(f"  [MISSING] {filename}")
            continue

        size = os.path.getsize(filepath)
        with open(filepath, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()

        match = (actual_hash == expected_hash)
        if not match:
            all_pass = False
            print(f"  [MISMATCH] {filename}")
        else:
            print(f"  [MATCH] {filename} ({size:,} bytes)")

        results[filename] = {
            "size_bytes": size,
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "match": match,
            "status": "VERIFIED_BIT_FOR_BIT_PARITY" if match else "HASH_MISMATCH"
        }

    report = {
        "metadata": {
            "phase": "PHASE 11J",
            "standard": "SIH 2026 Pre-Submission Hardening",
            "audit_type": "MODEL ARTIFACT RELEASE INTEGRITY",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "all_artifacts_match": all_pass,
            "total_artifacts_verified": len(BASELINE_HASHES)
        },
        "artifacts": results
    }

    out_path = os.path.join(root, "reports", "PHASE11J_MODEL_ARTIFACT_PARITY.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[PHASE 11J] Parity report saved to {out_path}")
    print(f"[PHASE 11J] Overall Model Integrity Verdict: {'PASS (100% PARITY)' if all_pass else 'FAIL'}")

if __name__ == "__main__":
    main()
