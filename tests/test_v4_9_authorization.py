# -*- coding: utf-8 -*-
"""
tests/test_v4_9_authorization.py
================================
Phase V4.9 Test Suite: Operator vs Authorized Acceptance & Placeholder Token Demotion
"""

import pytest
from engine.sensor_acceptance_engine import (
    SensorAcceptanceEngine,
    STATE_TELEMETRY_VALIDATED,
    STATE_FIELD_COMMISSIONED
)


@pytest.fixture
def acceptance_engine(tmp_path):
    p_file = str(tmp_path / "test_auth_ledger.json")
    return SensorAcceptanceEngine(persistence_path=p_file)


class TestAuthorizationAuditing:
    """Verifies that authorization placeholder strings are demoted and genuine credentials enforced."""

    def test_placeholder_token_classified_as_authorization_unverified(self, acceptance_engine):
        audit = acceptance_engine.audit_authorization_credentials("BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026")
        assert audit["token_present"] is True
        assert audit["status"] == "AUTHORIZATION_UNVERIFIED"
        assert audit["is_valid_credential"] is False
        assert audit["classification"] == "PLACEHOLDER_STRING"
        assert "placeholder" in audit["notes"].lower()

    def test_missing_token_classified_as_missing(self, acceptance_engine):
        audit = acceptance_engine.audit_authorization_credentials(None)
        assert audit["token_present"] is False
        assert audit["status"] == "MISSING"
        assert audit["is_valid_credential"] is False

    def test_placeholder_token_cannot_field_commission_sensor(self, acceptance_engine):
        s_id = "PIEZO-AUTH-TEST"
        acceptance_engine.register_planned_sensor(s_id)
        acceptance_engine._states[s_id] = STATE_TELEMETRY_VALIDATED

        # Try to use the placeholder token
        success, msg, trans = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_FIELD_COMMISSIONED,
            operator="OperatorBob",
            evidence_reference="DOC-SIGNOFF",
            reason="Attempting commissioning with placeholder",
            authorization_token="BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026"
        )
        assert success is False
        assert "Software-only commissioning is prohibited" in msg
        assert "AUTHORIZATION_UNVERIFIED" in msg
        assert acceptance_engine.get_sensor_state(s_id) == STATE_TELEMETRY_VALIDATED

    def test_cryptographic_pki_token_allows_commissioning_with_authorized_role(self, acceptance_engine):
        s_id = "INCL-AUTH-TEST"
        acceptance_engine.register_planned_sensor(s_id)
        acceptance_engine._states[s_id] = STATE_TELEMETRY_VALIDATED

        success, msg, trans = acceptance_engine.execute_transition(
            sensor_id=s_id,
            target_state=STATE_FIELD_COMMISSIONED,
            operator="Col_Sharma",
            evidence_reference="DOC-BRO-OFFICIAL-SIGNOFF",
            reason="Multi-agency physical commissioning certified",
            authorization_token="AUTH-PKI-BRO-2026-X889",
            metadata={"inspector_role": "BRO_PROJECT_DIRECTOR"}
        )
        assert success is True
        assert acceptance_engine.get_sensor_state(s_id) == STATE_FIELD_COMMISSIONED
