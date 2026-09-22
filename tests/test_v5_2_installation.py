# -*- coding: utf-8 -*-
"""
tests/test_v5_2_installation.py
===============================
Phase V5.2 Test Suite: Physical Installation & Lifecycle Stage Governance
Verifies the 7-stage Sensor Status Matrix and strictly rejects stage skipping.
"""

import pytest
from engine.physical_deployment_engine import (
    GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE,
    CANONICAL_V5_STAGES,
    STAGE_PLANNED,
    STAGE_BENCH_ACCEPTED,
    STAGE_FIELD_COMMISSIONED,
    STAGE_LIVE_MONITORING
)


def test_seven_stage_matrix_definition():
    assert len(CANONICAL_V5_STAGES) == 7
    assert CANONICAL_V5_STAGES[0] == STAGE_PLANNED
    assert CANONICAL_V5_STAGES[1] == STAGE_BENCH_ACCEPTED
    assert CANONICAL_V5_STAGES[-2] == STAGE_FIELD_COMMISSIONED
    assert CANONICAL_V5_STAGES[-1] == STAGE_LIVE_MONITORING


def test_zero_sensors_marked_installed_without_evidence():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    audits = engine.audit_sensor_hardware_provenance()
    for sensor_id, a in audits.items():
        assert a.installation_status != "INSTALLED", (
            f"Sensor {sensor_id} cannot be marked INSTALLED without physical field evidence."
        )


def test_stage_skipping_strictly_prohibited():
    engine = GLOBAL_PHYSICAL_DEPLOYMENT_ENGINE
    # Validates that a node cannot jump directly from PLANNED to LIVE_MONITORING
    valid_transition, msg = engine.validate_stage_transition(
        current_stage=STAGE_PLANNED,
        target_stage=STAGE_LIVE_MONITORING
    )
    assert valid_transition is False, "Direct transition from PLANNED to LIVE_MONITORING must be rejected."
