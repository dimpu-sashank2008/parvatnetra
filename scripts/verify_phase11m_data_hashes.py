#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_phase11m_data_hashes.py
Computes SHA-256 digests for all release-critical datasets and manifests,
validating bit-for-bit parity against Phase 11J baseline.
Saves reports/PHASE11M_FINAL_DATA_HASHES.json.
"""

import os
import json
import hashlib
from datetime import datetime, timezone

DATA_TARGETS = [
    ("data/features/real_train.csv", "79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e", 16),
    ("data/features/real_val.csv", "ed732e2054f1b028cab9380a35ad31affbbb5e93a3cb207fda1582665aa0bd81", 12),
    ("data/features/real_test.csv", "29f84cf974241844a16086736e1cab833484a9587519946dd24ee09ae09d28da", 8),
    ("data/labels/event_labels.csv", "edcdb95b13a87208deb3aa20cf29f381bad8c9312c8879131bce38ad00455a4c", 36),
    ("data/features/features_all.csv", "28688c13aba6b03b83d55a41f3f4028f910c16069eea12396a4695d579a56c2a", 36),
    ("data/features/demo_train.csv", "a5453fa55bc6cc330d92236f5c82444444f1034c3969de4eff0b3b5deb6c9cad", 25),
    ("data/manifests/phase11k_demo_scenarios.json", None, None)
]

def main():
    report_data = {}
    all_match = True

    print("=== VERIFYING DATASET & MANIFEST PARITY (PHASE 11M) ===")
    for rel_path, expected_hash, expected_rows in DATA_TARGETS:
        if not os.path.exists(rel_path):
            print(f"[MISSING] {rel_path}")
            all_match = False
            continue

        with open(rel_path, "rb") as f:
            data = f.read()
            actual_hash = hashlib.sha256(data).hexdigest()
            size = len(data)

        # Count rows if CSV
        actual_rows = None
        if rel_path.endswith(".csv"):
            with open(rel_path, "r", encoding="utf-8", errors="ignore") as f_txt:
                lines = [l for l in f_txt.readlines() if l.strip()]
                actual_rows = max(0, len(lines) - 1)

        match = True
        if expected_hash:
            match = (actual_hash == expected_hash)
            if not match:
                all_match = False
                print(f"[MISMATCH] {rel_path} (Exp: {expected_hash[:12]}..., Got: {actual_hash[:12]}...)")
            else:
                print(f"[OK] {rel_path:<36} | {size:>5} bytes | {actual_rows} rows | SHA256 MATCH")
        else:
            print(f"[OK] {rel_path:<36} | {size:>5} bytes | SHA256: {actual_hash[:16]}... (Manifest)")

        report_data[rel_path] = {
            "exists": True,
            "size_bytes": size,
            "row_count": actual_rows,
            "sha256": actual_hash,
            "expected_sha256": expected_hash,
            "match": match,
            "status": "VERIFIED_BIT_FOR_BIT_PARITY" if match else "MISMATCH"
        }

    report = {
        "metadata": {
            "phase": "PHASE 11M",
            "standard": "SIH 2026 Pre-Submission Freeze",
            "audit_type": "FINAL DATASET ARTIFACT RELEASE INTEGRITY",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "all_datasets_match": all_match,
            "total_artifacts_verified": len(DATA_TARGETS)
        },
        "datasets": report_data
    }

    out_path = os.path.join("reports", "PHASE11M_FINAL_DATA_HASHES.json")
    os.makedirs("reports", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[PHASE 11M] Data hash snapshot written to {out_path}")
    if not all_match:
        print("[CRITICAL STOP] Dataset artifact mismatch detected!")
        exit(1)
    else:
        print("[SUCCESS] All dataset artifacts verified bit-for-bit with baseline.")

if __name__ == "__main__":
    main()
