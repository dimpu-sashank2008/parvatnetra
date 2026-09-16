# -*- coding: utf-8 -*-
"""
scripts/train_temporal_lstm.py
==============================
PARVAT NETRA • PAHAD AI — Deep Temporal Sequence Model Training Stub
---------------------------------------------------------------------
Phase 12B: Rigorous gatekeeping entrypoint for LSTM / GRU recurrent models.

Constitutional Invariant:
  This script REFUSES to train deep sequence models unless the repository
  satisfies the Phase 12B Training Eligibility Gate (DATA_COLLECTION_REQUIRED -> TRAINING_ELIGIBLE).
  Under no circumstances will it fabricate data or train on small-sample snapshots.

Usage:
  python scripts/train_temporal_lstm.py                 # Evaluates gate; refuses training if targets unmet
  python scripts/train_temporal_lstm.py --audit-only   # Prints detailed readiness diagnosis without exit error
"""

from __future__ import annotations

import os
import sys
import json
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TRAIN_TEMPORAL_LSTM")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_temporal_gate import PahadTemporalGate, TemporalReadinessError, GateStatus, PROJECT_TARGETS


def run_training_stub(audit_only: bool = False, allow_demo: bool = False) -> int:
    logger.info("=" * 70)
    logger.info("PARVAT NETRA • PAHAD AI — Deep Temporal Sequence Training Entrypoint")
    logger.info("Standard: SIH 26001 / Project Constitution Section 12 & 32")
    logger.info("=" * 70)

    # 1. Evaluate Gate
    readiness = PahadTemporalGate.evaluate_current_repository()
    gate_status = readiness["gate_status"]

    logger.info("Gate Status: %s", gate_status)
    logger.info("Recommended Action: %s", readiness["recommended_action"])
    logger.info("Active Operational Model: %s", readiness["active_temporal_model"])

    # Print check matrix
    logger.info("-" * 70)
    logger.info("%-35s %-12s %-12s %-6s", "Prerequisite Check", "Actual", "Target", "Result")
    logger.info("-" * 70)
    for k, v in readiness["actual_vs_target"].items():
        logger.info("%-35s %-12s %-12s %-6s", k, str(v["actual"]), str(v["target"]), v["status"])
    logger.info("-" * 70)

    if audit_only:
        logger.info("Audit-only mode requested. Exiting without training.")
        return 0

    # 2. Enforce Hard Guard
    try:
        PahadTemporalGate.enforce_training_guard(allow_demo_override=allow_demo)
    except TemporalReadinessError as tre:
        logger.error(str(tre))
        logger.error(
            "TRAINING REFUSED BY SAFETY GATE. "
            "To train a valid deep sequence model, real continuous telemetry data must first be collected."
        )
        return 1

    # If training was authorized (future state):
    logger.info("All readiness criteria satisfied. Initializing PyTorch sequence trainer...")
    # Training code will execute here in future production phase
    return 0


def main():
    parser = argparse.ArgumentParser(description="PAHAD AI Temporal LSTM Training Entrypoint")
    parser.add_argument("--audit-only", action="store_true", help="Print gate readiness audit and exit 0")
    parser.add_argument("--force-demo", action="store_true", help="Allow demo-only stub if PAHAD_DEMO_MODE=1")
    args = parser.parse_args()

    sys.exit(run_training_stub(audit_only=args.audit_only, allow_demo=args.force_demo))


if __name__ == "__main__":
    main()
