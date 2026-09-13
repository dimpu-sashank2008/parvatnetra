# -*- coding: utf-8 -*-
"""
scripts/backup_restore.py
=========================
PARVAT NETRA • PAHAD AI — Disaster Recovery, Backup & Integrity Verification
Creates tamper-evident backups with SHA-256 checksums and performs automated restoration.
"""

from __future__ import annotations

import os
import sys
import json
import shutil
import zipfile
import hashlib
import sqlite3
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

logger = logging.getLogger("DISASTER_RECOVERY")

def compute_sha256(file_path: str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def check_sqlite_integrity(db_path: str) -> bool:
    """Runs PRAGMA integrity_check on an SQLite database."""
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check;")
        res = cur.fetchone()
        conn.close()
        return res is not None and res[0] == "ok"
    except Exception as e:
        logger.error(f"Integrity check failed for {db_path}: {e}")
        return False

def create_backup_archive(output_zip: str, source_files: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Creates a zip backup containing critical operational state and a manifest with checksums.
    """
    if source_files is None:
        source_files = [
            os.path.join(base_dir, "data", "observations", "pahad_observations.db"),
            os.path.join(base_dir, "data", "manifests", "canonical_event_inventory.json"),
            os.path.join(base_dir, "data", "features", "real_test.csv")
        ]

    os.makedirs(os.path.dirname(os.path.abspath(output_zip)), exist_ok=True)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backup_version": "1.0-phase7",
        "files": {}
    }

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath in source_files:
            if os.path.exists(fpath):
                try:
                    rel_name = os.path.relpath(fpath, base_dir)
                    if rel_name.startswith(".."):
                        rel_name = os.path.basename(fpath)
                except Exception:
                    rel_name = os.path.basename(fpath)
                arc_name = rel_name.replace("\\", "/")
                zf.write(fpath, arcname=arc_name)
                checksum = compute_sha256(fpath)
                manifest["files"][arc_name] = {
                    "sha256": checksum,
                    "size_bytes": os.path.getsize(fpath)
                }

        # Write manifest into zip
        zf.writestr("backup_manifest.json", json.dumps(manifest, indent=2))

    return {
        "status": "BACKUP_SUCCESS",
        "archive_path": output_zip,
        "archive_size_bytes": os.path.getsize(output_zip),
        "file_count": len(manifest["files"]),
        "manifest": manifest
    }

def restore_backup_archive(backup_zip: str, target_dir: str) -> Dict[str, Any]:
    """
    Restores files from a backup archive and validates SHA-256 and SQLite integrity.
    """
    if not os.path.exists(backup_zip):
        raise FileNotFoundError(f"Backup archive {backup_zip} does not exist.")

    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(backup_zip, "r") as zf:
        # Read manifest
        manifest_data = json.loads(zf.read("backup_manifest.json").decode("utf-8"))
        zf.extractall(target_dir)

    restored_status = {}
    all_valid = True

    for rel_name, meta in manifest_data["files"].items():
        restored_file = os.path.join(target_dir, rel_name)
        if not os.path.exists(restored_file):
            restored_status[rel_name] = "MISSING"
            all_valid = False
            continue

        chk = compute_sha256(restored_file)
        if chk != meta["sha256"]:
            restored_status[rel_name] = "CHECKSUM_MISMATCH"
            all_valid = False
            continue

        # Check SQLite integrity if db
        if restored_file.endswith(".db"):
            if not check_sqlite_integrity(restored_file):
                restored_status[rel_name] = "CORRUPTED_SQLITE"
                all_valid = False
                continue

        restored_status[rel_name] = "VERIFIED_OK"

    return {
        "status": "RESTORE_SUCCESS" if all_valid else "RESTORE_FAILED",
        "restored_files": restored_status,
        "integrity_verified": all_valid
    }

if __name__ == "__main__":
    out = os.path.join(base_dir, "data", "backups", "phase7_dr_test.zip")
    b_res = create_backup_archive(out)
    print("Backup Result:", json.dumps(b_res, indent=2))
