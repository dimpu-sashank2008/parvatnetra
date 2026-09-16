# -*- coding: utf-8 -*-
"""
tests/test_phase12b_training_stub.py
=====================================
PARVAT NETRA • PAHAD AI — Phase 12B LSTM Training Stub & Safety Interlock Tests
"""

import os
import subprocess
import sys
import pytest

from scripts.train_temporal_lstm import run_training_stub


def test_training_stub_audit_only():
    """Verify that --audit-only mode completes successfully with code 0."""
    ret = run_training_stub(audit_only=True)
    assert ret == 0


def test_training_stub_refuses_training():
    """Verify that training mode refuses execution and returns code 1."""
    old_demo = os.environ.get("PAHAD_DEMO_MODE")
    if "PAHAD_DEMO_MODE" in os.environ:
        del os.environ["PAHAD_DEMO_MODE"]

    try:
        ret = run_training_stub(audit_only=False, allow_demo=False)
        assert ret == 1
    finally:
        if old_demo is not None:
            os.environ["PAHAD_DEMO_MODE"] = old_demo


def test_training_stub_cli_audit_only():
    """Execute scripts/train_temporal_lstm.py via CLI with --audit-only."""
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "train_temporal_lstm.py",
    )
    cmd = [sys.executable, script_path, "--audit-only"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    combined_output = res.stdout + res.stderr
    assert "Audit-only mode requested" in combined_output or "DATA_COLLECTION_REQUIRED" in combined_output


def test_training_stub_cli_refuses_execution():
    """Execute scripts/train_temporal_lstm.py via CLI without flags; must exit with code 1."""
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "train_temporal_lstm.py",
    )
    env = os.environ.copy()
    env.pop("PAHAD_DEMO_MODE", None)

    cmd = [sys.executable, script_path]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert res.returncode == 1
    combined_output = res.stdout + res.stderr
    assert "TRAINING REFUSED BY SAFETY GATE" in combined_output or "DATA_COLLECTION_REQUIRED" in combined_output
