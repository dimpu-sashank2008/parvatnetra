# -*- coding: utf-8 -*-
"""
tests/test_phase12d_failure_drills.py
=====================================
PARVAT NETRA • PAHAD AI — Phase 12D Outage & Resilience Failure Drill Suite
---------------------------------------------------------------------------
Simulates a live multi-stage failure sequence:
1. Normal operation
2. Weather outage (Open-Meteo failure -> IMD climatology fallback)
3. Seismic outage (USGS failure -> BIS Zone V regional baseline)
4. Primary database outage (PostgreSQL failure -> SQLite master registry)
5. Sensor outage (LoRaWAN IoT failure -> Coupled infiltration model)
6. Network outage (Full internet loss -> Local EOC vector cache)
7. Telemetry & network recovery (Full resynchronization)

Verifies:
- Zero unsafe escalation.
- Zero fabricated live data.
- Zero fake delivery receipts.
- Intact safety gates and audit chain.
"""

import os
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.pahad_adversarial_defense import FailureDrillOrchestrator


class TestPhase12DFailureDrills:

    def test_complete_seven_stage_drill(self):
        """Execute full 7-stage outage drill and verify clean pass."""
        report = FailureDrillOrchestrator.run_complete_drill()
        assert report["verdict"] == "FAILSAFE_DRILL_PASSED"
        assert report["total_stages"] == 7
        assert report["passed_stages"] == 7
        assert report["zero_unsafe_escalation"] is True
        assert report["zero_fake_delivery_receipts"] is True
        assert report["zero_corrupted_audit_records"] is True

    def test_stage_safety_states_preserved(self):
        """Every drill stage must maintain disarmed dry-run safety state."""
        report = FailureDrillOrchestrator.run_complete_drill()
        for stage in report["stages"]:
            assert stage["safety_state"] == "DISARMED_DRY_RUN", f"Unsafe safety state in {stage['stage']}"

    def test_weather_and_seismic_fallbacks(self):
        """Weather and seismic outage stages must engage explicit fallbacks and flag provenance."""
        report = FailureDrillOrchestrator.run_complete_drill()
        stages = {s["stage"]: s for s in report["stages"]}

        weather_stage = stages["STAGE_2_WEATHER_OUTAGE"]
        assert weather_stage["health"] == "DEGRADED"
        assert weather_stage["provenance"] == "[CACHED]"

        seismic_stage = stages["STAGE_3_SEISMIC_OUTAGE"]
        assert seismic_stage["health"] == "DEGRADED"
        assert seismic_stage["provenance"] == "[CACHED]"

    def test_database_and_sensor_resilience(self):
        """Database and sensor outage stages must fallback to SQLite and modeled infiltration."""
        report = FailureDrillOrchestrator.run_complete_drill()
        stages = {s["stage"]: s for s in report["stages"]}

        db_stage = stages["STAGE_4_DATABASE_OUTAGE"]
        assert "SQLite" in db_stage["fallback_engaged"]
        assert db_stage["zero_data_loss"] is True

        sensor_stage = stages["STAGE_5_SENSOR_OUTAGE"]
        assert sensor_stage["provenance"] == "[MODELLED]"

    def test_network_blackout_and_recovery(self):
        """Full network blackout must use offline cache without fabricating live feeds; recovery must restore health."""
        report = FailureDrillOrchestrator.run_complete_drill()
        stages = {s["stage"]: s for s in report["stages"]}

        net_stage = stages["STAGE_6_NETWORK_OUTAGE"]
        assert net_stage["health"] == "OFFLINE_AUSTERE"
        assert net_stage["fake_live_generated"] is False

        rec_stage = stages["STAGE_7_RECOVERY"]
        assert rec_stage["health"] == "HEALTHY"
        assert rec_stage["audit_chain_intact"] is True
