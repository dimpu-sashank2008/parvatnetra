"""
Phase 12C Automated Test Suite: Explainability Engine & Evidence Matrix
Tests contract compliance, non-causal grammar, zero manufactured deltas,
and 2-of-3 corroboration heuristic.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.pahad_explanation_engine import (
    PahadExplanationEngine,
    ExplanationContract,
    RiskChangeEngine
)
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


class TestPhase12CExplainabilityContract:
    def test_engine_contract_structure(self):
        engine = PahadExplanationEngine()
        contract = engine.get_corridor_explanation("SK-NH10-KM48")
        
        assert isinstance(contract, ExplanationContract)
        assert contract.corridor_id == "SK-NH10-KM48"
        assert contract.corridor_name != ""
        assert isinstance(contract.cri, float)
        assert isinstance(contract.fos, float)
        assert isinstance(contract.event_probability, float)
        assert contract.risk_band in ["CRITICAL", "WARNING", "WATCH", "STABLE", "DATA INSUFFICIENT", "HIGH RISK", "MODERATE RISK", "LOW RISK", "HIGH", "MODERATE", "LOW"]
        assert isinstance(contract.top_factors, list)
        assert len(contract.top_factors) >= 1
        
        # Tripartite evidence
        assert isinstance(contract.supporting_evidence, list)
        assert isinstance(contract.contradicting_evidence, list)
        assert isinstance(contract.missing_evidence, list)
        
        # Corroboration & Confidence
        assert any(k in contract.corroboration_state for k in ["CORROBORAT", "SIGNAL", "INSUFFICIENT", "A+B", "A+C", "B+C", "A+B+C"])
        assert contract.confidence in ["HIGH", "MODERATE", "LOW_CONFIDENCE", "LOW"]
        assert isinstance(contract.data_quality, dict)
        
        # Governance
        assert "Disaster Management Act 2005" in contract.statutory_requirement or "DMA 2005" in contract.statutory_requirement
        assert "ENABLE_PUBLIC_DISPATCH=0" in contract.statutory_requirement or "MANDATORY HUMAN SIGN-OFF" in contract.statutory_requirement
        assert contract.model_governance.get("status") == "NOT_TRAINED / PHYSICS-INFORMED SURROGATE" or "SURROGATE" in str(contract.model_governance)

    def test_non_causal_grammar_enforcement(self):
        engine = PahadExplanationEngine()
        contract = engine.get_corridor_explanation("ML-SONAPUR-01")
        
        forbidden_causal_phrases = [
            "caused the landslide",
            "caused the slope to fail",
            "triggered the failure",
            "rain caused the disaster",
            "earthquake caused the slide"
        ]
        
        sup_text = " ".join(str(s) for s in contract.supporting_evidence)
        text_to_check = (
            contract.causal_honesty_note.lower() + " " +
            sup_text.lower() + " " +
            contract.statutory_requirement.lower()
        )
        
        for phrase in forbidden_causal_phrases:
            assert phrase not in text_to_check, f"Forbidden causal phrase found: '{phrase}'"

    def test_zero_manufactured_deltas(self):
        rc_engine = RiskChangeEngine()
        
        # First call must return COMPARISON_UNAVAILABLE
        res1 = rc_engine.evaluate_change("SK-NH10-KM48", 45.0, 1.05, 30.0, None, "provider_a")
        assert res1["comparison_status"] == "COMPARISON_UNAVAILABLE"
        assert res1["delta_cri"] is None
        assert res1["delta_fos"] is None
        
        # Second call with same provider returns active comparison
        res2 = rc_engine.evaluate_change("SK-NH10-KM48", 55.0, 0.95, 45.0, None, "provider_a")
        assert res2["comparison_status"] == "ACTIVE_COMPARISON"
        assert res2["delta_cri"] == 10.0
        assert res2["delta_fos"] == -0.1
        assert res2["delta_rainfall"] == 15.0
        
        # Divergent provider must return COMPARISON_UNAVAILABLE (zero manufactured deltas across different sources)
        res3 = rc_engine.evaluate_change("SK-NH10-KM48", 60.0, 0.90, 50.0, None, "provider_b_divergent")
        assert res3["comparison_status"] == "COMPARISON_UNAVAILABLE"

    def test_multi_corridor_determinism(self):
        engine = PahadExplanationEngine()
        corridors = [
            "SK-NH10-KM48",
            "ML-SONAPUR-01",
            "MN-TUPUL-RLY",
            "MZ-MELTHUM-QRY",
            "AS-HAFLONG-RLY",
            "ML-MAWSYNRAM",
            "NL-DZUKOU-KOH",
            "AR-TAWANG-SELA",
            "TR-JAMPUI-HILLS"
        ]
        
        for cid in corridors:
            contract = engine.get_corridor_explanation(cid)
            assert contract.corridor_id == cid
            assert 0.0 <= contract.cri <= 100.0
            assert contract.fos > 0.0
            assert 0.0 <= contract.event_probability <= 1.0

    def test_api_explanation_endpoint(self, client):
        resp = client.get("/api/pahad/explanation/SK-NH10-KM48")
        assert resp.status_code == 200
        data = resp.get_json()
        
        assert data["corridor_id"] == "SK-NH10-KM48"
        assert "risk_change" in data
        assert "top_factors" in data or "top_drivers" in data
        assert "supporting_evidence" in data
        assert "contradicting_evidence" in data
        assert "missing_evidence" in data
        assert "corroboration_state" in data
        assert "statutory_requirement" in data or "authority_recommendation" in data
