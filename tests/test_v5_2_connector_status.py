# -*- coding: utf-8 -*-
"""
tests/test_v5_2_connector_status.py
===================================
Phase V5.2 Test Suite: Credentialed Connector Status & Fallback Identification
"""

import pytest
from engine.external_data_engine import (
    ExternalDataEngine,
    STATUS_LIVE,
    STATUS_CONNECTED,
    STATUS_AUTH_REQUIRED,
    STATUS_CACHED,
    STATUS_UNAVAILABLE
)


@pytest.fixture
def engine():
    return ExternalDataEngine.get_instance()


class TestV52ConnectorStatus:
    """Verifies that connectors truthfully report authentication and operational states."""

    def test_audit_all_connectors_returns_summary(self, engine):
        res = engine.audit_all_connectors()
        assert "audited_at" in res
        assert "total_connectors_audited" in res
        assert res["total_connectors_audited"] >= 8
        assert "status_counts" in res
        assert "connector_results" in res

    def test_imd_reports_auth_required_without_secrets(self, engine):
        imd_res = engine._audit_imd_credentials()
        assert imd_res["source_id"] == "SRC-IMD-NOWCAST"
        assert imd_res["status"] in {STATUS_AUTH_REQUIRED, STATUS_CONNECTED}
        assert imd_res["fallback_active"] is True
        assert "Open-Meteo" in imd_res["fallback_provider"]
        # Ensure fallback is never relabeled as IMD
        assert imd_res["fallback_provider"] != "SRC-IMD-NOWCAST"

    def test_ncs_reports_auth_required_without_secrets(self, engine):
        ncs_res = engine._audit_ncs_credentials()
        assert ncs_res["source_id"] == "SRC-NCS-SEISMIC"
        assert ncs_res["status"] in {STATUS_AUTH_REQUIRED, STATUS_CONNECTED}
        assert ncs_res["fallback_active"] is True
        assert "USGS" in ncs_res["fallback_provider"]

    def test_bhoonidhi_and_copernicus_auth_states(self, engine):
        bhoo = engine._audit_bhoonidhi_credentials()
        assert bhoo["source_id"] == "SRC-ISRO-NRSC-BHOONIDHI"
        assert bhoo["status"] in {STATUS_AUTH_REQUIRED, STATUS_CONNECTED}

        cop = engine._audit_copernicus_cdse()
        assert cop["source_id"] == "SRC-ESA-COPERNICUS-CDSE"
        assert cop["status"] in {STATUS_AUTH_REQUIRED, STATUS_CONNECTED}

    def test_physical_iot_is_strictly_unavailable(self, engine):
        audit = engine.audit_all_connectors()
        iot = audit["connector_results"]["SRC-PHYSICAL-IOT-KM48"]
        assert iot["status"] == STATUS_UNAVAILABLE
        assert iot["physical_sensors_verified"] == 0
        assert iot["borehole_casings_installed"] == 0
        assert iot["live_telemetry_observations"] == 0
