# -*- coding: utf-8 -*-
"""
tests/test_phase7_disaster_recovery.py
======================================
Tests for Phase 7K Disaster Recovery, Backup & Integrity Verification.
"""

import os
import sqlite3
import pytest
from scripts.backup_restore import (
    compute_sha256,
    check_sqlite_integrity,
    create_backup_archive,
    restore_backup_archive
)

@pytest.fixture
def sample_sqlite_db(tmp_path):
    db_path = str(tmp_path / "test_sample.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, msg TEXT);")
    cur.execute("INSERT INTO records (msg) VALUES ('disaster recovery record 1');")
    conn.commit()
    conn.close()
    return db_path

def test_sqlite_integrity_check(sample_sqlite_db):
    assert check_sqlite_integrity(sample_sqlite_db) is True
    assert check_sqlite_integrity("non_existent_file.db") is False

def test_backup_and_restore_cycle(tmp_path, sample_sqlite_db):
    backup_zip = str(tmp_path / "test_backup.zip")
    restore_dir = str(tmp_path / "restore_target")

    # Create backup
    b_res = create_backup_archive(backup_zip, source_files=[sample_sqlite_db])
    assert b_res["status"] == "BACKUP_SUCCESS"
    assert os.path.exists(backup_zip)

    # Restore backup
    r_res = restore_backup_archive(backup_zip, restore_dir)
    assert r_res["status"] == "RESTORE_SUCCESS"
    assert r_res["integrity_verified"] is True

    # Verify restored sqlite database contents
    rel_name = os.path.basename(sample_sqlite_db)
    restored_db_path = os.path.join(restore_dir, rel_name)
    assert os.path.exists(restored_db_path)

    conn = sqlite3.connect(restored_db_path)
    cur = conn.cursor()
    cur.execute("SELECT msg FROM records;")
    row = cur.fetchone()
    conn.close()
    assert row[0] == "disaster recovery record 1"
