# -*- coding: utf-8 -*-
"""
tests/test_hardware_bom.py
==========================
Verifies hardware BOM service, unit economics, power budget calculations, and pinout integrity.
"""

import pytest
from services.hardware_bom_service import get_hardware_bom_data

def test_hardware_bom_data_structure():
    data = get_hardware_bom_data()
    assert data["status"] == "success"
    assert data["total_cost_inr"] > 0
    assert data["total_cost_inr"] < 25000  # Must be affordable indigenous node
    assert data["cost_savings_pct"] > 90.0  # Must achieve > 90% cost savings vs imported
    assert len(data["bom_items"]) >= 10
    
def test_power_budget_autonomy():
    data = get_hardware_bom_data()
    power = data["power_budget"]
    assert power["autonomy_days_zero_sunlight"] >= 10.0  # Must survive at least 10 days fog
    assert power["daily_energy_consumption_wh"] < 1.0
    assert power["solar_panel_wattage"] == 15.0

def test_regulatory_in865_compliance():
    data = get_hardware_bom_data()
    reg = data["regulatory_compliance"]
    assert "865.0 - 867.0 MHz" in reg["frequency_band_mhz"]
    assert reg["system_tx_power_dbm"] <= reg["max_permitted_erp_dbm"]
    assert "AES-128" in reg["encryption"]

def test_pinout_matrix():
    data = get_hardware_bom_data()
    pinouts = data["pinout_matrix"]
    assert any("LoRa SPI" in p["function"] for p in pinouts)
    assert any("Inclinometer" in p["function"] for p in pinouts)
    assert any("Piezometer" in p["function"] for p in pinouts)
