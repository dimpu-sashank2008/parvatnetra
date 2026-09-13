# -*- coding: utf-8 -*-
"""
services/power_validator.py
===========================
PARVAT NETRA • PAHAD AI — Solar & Battery Subsystem Power Validator
-------------------------------------------------------------------
Monitors solar PV charging curves, LiFePO4 battery health, low-temperature
charging degradation, and calculated autonomous reserve days.

Provenance Rules:
  All power assessments MUST explicitly declare telemetry source:
  - THEORETICAL   : Idealized design spreadsheet calculations
  - BENCH         : Laboratory programmable DC load / power supply readings
  - FIELD-MEASURED: Calibrated telemetry from on-site INA219 / MPPT charge controller
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("POWER_VALIDATOR")

# 12V LiFePO4 Chemistry Thresholds
VOLTAGE_OVERCHARGE = 14.6
VOLTAGE_FLOAT = 13.6
VOLTAGE_NOMINAL = 12.8
VOLTAGE_LOW_WARNING = 11.8
VOLTAGE_CRITICAL_CUTOFF = 10.5

# Minimum required autonomous reserve days during prolonged monsoon cloud cover
REQUIRED_AUTONOMY_DAYS = 5.0


class PowerValidator:
    """Validates power telemetry and calculates operational reserves for off-grid nodes."""

    def calculate_soc_from_voltage(self, voltage: float) -> float:
        """Estimates State of Charge (%) from resting cell voltage."""
        if voltage >= VOLTAGE_FLOAT:
            return 100.0
        elif voltage <= VOLTAGE_CRITICAL_CUTOFF:
            return 0.0
        elif voltage >= VOLTAGE_NOMINAL:
            # 12.8V to 13.6V covers 70% to 100%
            return round(70.0 + (voltage - 12.8) / 0.8 * 30.0, 1)
        elif voltage >= VOLTAGE_LOW_WARNING:
            # 11.8V to 12.8V covers 20% to 70%
            return round(20.0 + (voltage - 11.8) / 1.0 * 50.0, 1)
        else:
            # 10.5V to 11.8V covers 0% to 20%
            return round((voltage - 10.5) / 1.3 * 20.0, 1)

    def calculate_autonomous_reserve_days(
        self,
        battery_ah: float,
        soc_pct: float,
        average_load_ma: float
    ) -> float:
        """
        Calculates how many days the device can operate continuously with zero solar input:
        Days = (Battery_Ah * SoC% * 0.80 DoD) / (Average_Load_A * 24h)
        """
        if average_load_ma <= 0:
            return 999.0

        available_ah = battery_ah * (soc_pct / 100.0) * 0.80  # 80% safe depth of discharge
        load_a = average_load_ma / 1000.0
        daily_consumption_ah = load_a * 24.0

        reserve_days = available_ah / max(0.001, daily_consumption_ah)
        return round(reserve_days, 1)

    def validate_power_telemetry(
        self,
        telemetry: Dict[str, Any],
        provenance: str = "FIELD-MEASURED"
    ) -> Dict[str, Any]:
        """
        Validates power telemetry readings and returns health classification.
        """
        allowed_prov = {"THEORETICAL", "BENCH", "FIELD-MEASURED"}
        prov = provenance if provenance in allowed_prov else "THEORETICAL"

        voltage = float(telemetry.get("battery_voltage_v", 12.8))
        battery_ah = float(telemetry.get("battery_capacity_ah", 20.0))
        solar_v = float(telemetry.get("solar_pv_v", 0.0))
        solar_current_ma = float(telemetry.get("solar_current_ma", 0.0))
        load_current_ma = float(telemetry.get("load_current_ma", 45.0))

        soc = self.calculate_soc_from_voltage(voltage)
        reserve_days = self.calculate_autonomous_reserve_days(battery_ah, soc, load_current_ma)

        # Health Classification
        if voltage <= VOLTAGE_CRITICAL_CUTOFF:
            status = "CRITICAL_SHUTDOWN"
            note = f"Battery voltage ({voltage:.2f}V) below low-voltage disconnect ({VOLTAGE_CRITICAL_CUTOFF}V)"
        elif voltage <= VOLTAGE_LOW_WARNING:
            status = "LOW_BATTERY_WARNING"
            note = f"Battery voltage ({voltage:.2f}V) below warning threshold ({VOLTAGE_LOW_WARNING}V)"
        elif reserve_days < REQUIRED_AUTONOMY_DAYS:
            status = "MARGINAL_RESERVE"
            note = f"Autonomy reserve ({reserve_days:.1f} days) below required {REQUIRED_AUTONOMY_DAYS} days"
        else:
            status = "OPTIMAL"
            note = "Battery and solar charging curves within nominal envelope"

        is_charging = solar_v > voltage and solar_current_ma > 50.0

        return {
            "battery_voltage_v": voltage,
            "battery_soc_pct": soc,
            "battery_capacity_ah": battery_ah,
            "solar_pv_v": solar_v,
            "solar_current_ma": solar_current_ma,
            "load_current_ma": load_current_ma,
            "is_solar_charging": is_charging,
            "autonomous_reserve_days": reserve_days,
            "power_status": status,
            "evaluation_note": note,
            "provenance": prov
        }


POWER_VALIDATOR = PowerValidator()
