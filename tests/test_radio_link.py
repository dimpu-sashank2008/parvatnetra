# -*- coding: utf-8 -*-
"""
tests/test_radio_link.py
========================
Unit tests for LoRa radio link benchmark, RF propagation thresholds,
and SQLite test logging.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.test_radio_link import evaluate_rf_metrics, run_radio_test


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_radio.db")


def test_evaluate_rf_metrics_optimal_pass():
    verdict, rationale = evaluate_rf_metrics(rssi=-85.0, snr=8.0, pdr=0.98, latency_ms=250.0)
    assert verdict == "PASS"
    assert "Optimal LoRa link quality" in rationale


def test_evaluate_rf_metrics_marginal_degraded():
    verdict, rationale = evaluate_rf_metrics(rssi=-110.0, snr=-8.0, pdr=0.82, latency_ms=1200.0)
    assert verdict == "DEGRADED"
    assert "Marginal RF link quality" in rationale


def test_evaluate_rf_metrics_severe_attenuation_fail():
    verdict, rationale = evaluate_rf_metrics(rssi=-124.0, snr=-15.0, pdr=0.50, latency_ms=4500.0)
    assert verdict == "FAIL"
    assert "Excessive attenuation" in rationale


def test_evaluate_rf_metrics_packet_loss_fail():
    verdict, rationale = evaluate_rf_metrics(rssi=-95.0, snr=2.0, pdr=0.60, latency_ms=300.0)
    assert verdict == "FAIL"
    assert "Unacceptable packet loss" in rationale


def test_run_radio_test_persists_to_db(temp_db):
    res = run_radio_test(
        device_id="SN-PIEZ-TEST-01",
        gateway_id="GW-NH10-01",
        corridor_id="CORR-NH10-SIKKIM-KM48",
        num_packets=10,
        rssi_input=-90.0,
        snr_input=5.0,
        pdr_input=0.95,
        latency_input=310.0,
        db_path=temp_db
    )
    assert res["verdict"] == "PASS"
    assert res["device_id"] == "SN-PIEZ-TEST-01"
    assert res["details"]["packets_received"] == 10
    assert os.path.exists(temp_db)
