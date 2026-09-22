# -*- coding: utf-8 -*-
"""
tests/test_v5_2_source_status.py
================================
Phase V5.2 Test Suite: External Data Source Classification & Honest Status Audit
"""

import pytest
from engine.external_data_engine import ExternalDataEngine, STATUS_LIVE, STATUS_AUTH_REQUIRED, STATUS_UNAVAILABLE, STATUS_CACHED


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


class TestV52SourceStatus:
    """Verifies honest status classification of all 12 institutional and telemetry data sources."""

    def test_total_sources_audited(self, engine):
        sources = engine.list_sources()
        assert len(sources) == 12

    def test_live_sources_are_truly_open(self, engine):
        live_srcs = [s for s in engine.list_sources() if s["status"] == STATUS_LIVE]
        live_ids = {s["source_id"] for s in live_srcs}
        assert "SRC-OPEN-METEO" in live_ids
        assert "SRC-USGS-FDSNWS" in live_ids

    def test_auth_required_sources_not_falsely_marked_live(self, engine):
        auth_srcs = [s for s in engine.list_sources() if s["status"] == STATUS_AUTH_REQUIRED]
        auth_ids = {s["source_id"] for s in auth_srcs}
        assert "SRC-IMD-NOWCAST" in auth_ids
        assert "SRC-NCS-SEISMIC" in auth_ids
        assert "SRC-ISRO-NRSC-BHOONIDHI" in auth_ids
        assert "SRC-ESA-COPERNICUS-CDSE" in auth_ids

    def test_physical_iot_marked_unavailable(self, engine):
        src = engine.get_source("SRC-PHYSICAL-IOT-KM48")
        assert src is not None
        assert src["status"] == STATUS_UNAVAILABLE
        assert "PHYSICAL_TELEMETRY_PENDING" in src.get("notes", "") or "pending" in src.get("notes", "").lower()
