# -*- coding: utf-8 -*-
"""
firmware/interfaces.py
======================
PARVAT NETRA • Embedded Hardware Abstraction Layer (HAL) Interfaces
-------------------------------------------------------------------
Provides hardware-independent interfaces for sensor transducer reading,
metrology calibration, RTC synchronization, local circular FIFO buffering,
power/battery monitoring, and wireless transmission.

Enables unit testing and automated bench emulation without physical hardware.
"""

from __future__ import annotations

import time
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class SensorReading:
    """Standardized reading returned by a physical or emulated transducer."""
    sensor_type: str
    value: float
    raw_value: float
    unit: str
    quality: str = "GOOD"  # GOOD, DEGRADED, INVALID
    timestamp: Optional[str] = None
    derived: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_type": self.sensor_type,
            "value": round(self.value, 4),
            "raw_value": round(self.raw_value, 4),
            "unit": self.unit,
            "quality": self.quality,
            "timestamp": self.timestamp,
            "derived": self.derived,
            "error": self.error
        }


class BaseSensorReader(ABC):
    """Abstract base class for all sensor transducer reading interfaces."""

    def __init__(self, sensor_type: str, unit: str):
        self.sensor_type = sensor_type
        self.unit = unit
        self.zero_offset: float = 0.0
        self.scale_factor: float = 1.0

    def set_calibration(self, zero_offset: float = 0.0, scale_factor: float = 1.0) -> None:
        self.zero_offset = zero_offset
        self.scale_factor = scale_factor

    def apply_calibration(self, raw_value: float) -> float:
        """Standard linear calibration transfer function: y = (raw - zero) * scale"""
        return (raw_value - self.zero_offset) * self.scale_factor

    @abstractmethod
    def read(self) -> SensorReading:
        """Reads transducer and returns normalized SensorReading."""
        raise NotImplementedError


class PiezometerReader(BaseSensorReader):
    """Vibrating-wire pore-water pressure transducer interface."""

    def __init__(self, simulated_pressure_kpa: float = 25.0):
        super().__init__("piezometer", "kPa")
        self._current_pressure = simulated_pressure_kpa

    def set_simulated_pressure(self, kpa: float) -> None:
        self._current_pressure = kpa

    def read(self) -> SensorReading:
        calibrated = self.apply_calibration(self._current_pressure)
        # Check physical bounds: -10 to 250 kPa
        quality = "GOOD"
        if calibrated < -10.0 or calibrated > 250.0:
            quality = "INVALID"
        elif calibrated > 45.0:
            quality = "DEGRADED"  # Exceeds acute critical threshold

        # Approximate resonant frequency for vibrating wire (1200 - 3500 Hz)
        # f = sqrt(P * 1000 + f0^2)
        res_freq = math.sqrt(max(calibrated, 0.0) * 1000.0 + 1440000.0)

        return SensorReading(
            sensor_type="piezometer",
            value=calibrated,
            raw_value=self._current_pressure,
            unit="kPa",
            quality=quality,
            derived={"frequency_hz": round(res_freq, 1)}
        )


class TiltReader(BaseSensorReader):
    """Biaxial MEMS surface tiltmeter transducer interface."""

    def __init__(self, tilt_x_deg: float = 0.0, tilt_y_deg: float = 0.0):
        super().__init__("tilt", "deg")
        self.tilt_x = tilt_x_deg
        self.tilt_y = tilt_y_deg
        self._prev_resultant = math.sqrt(tilt_x_deg ** 2 + tilt_y_deg ** 2)
        self._last_read_time = time.time()

    def set_simulated_tilt(self, x_deg: float, y_deg: float) -> None:
        self.tilt_x = x_deg
        self.tilt_y = y_deg

    def read(self) -> SensorReading:
        cal_x = self.apply_calibration(self.tilt_x)
        cal_y = self.apply_calibration(self.tilt_y)
        resultant = math.sqrt(cal_x ** 2 + cal_y ** 2)

        # Rate of change calculation
        now = time.time()
        dt_days = max((now - self._last_read_time) / 86400.0, 0.0001)
        rate_deg_day = abs(resultant - self._prev_resultant) / dt_days
        self._prev_resultant = resultant
        self._last_read_time = now

        quality = "GOOD"
        if resultant > 45.0 or resultant < -45.0:
            quality = "INVALID"

        return SensorReading(
            sensor_type="tilt",
            value=resultant,
            raw_value=resultant,
            unit="deg",
            quality=quality,
            derived={
                "tilt_x": round(cal_x, 3),
                "tilt_y": round(cal_y, 3),
                "tilt_rate_deg_day": round(rate_deg_day, 2)
            }
        )


class RainGaugeReader(BaseSensorReader):
    """Digital tipping-bucket rain gauge with software pulse debouncing."""

    def __init__(self, mm_per_tip: float = 0.2):
        super().__init__("rain_gauge", "mm")
        self.mm_per_tip = mm_per_tip
        self._tip_count: int = 0
        self._hourly_tips: int = 0
        self._last_tip_time = 0.0
        self.debounce_ms = 50.0  # 50 ms RC debounce

    def register_tip(self) -> bool:
        """Simulates or handles hardware reed switch pulse interrupt."""
        now = time.time() * 1000.0
        if (now - self._last_tip_time) < self.debounce_ms:
            return False  # Debounce filter dropped bounce
        self._last_tip_time = now
        self._tip_count += 1
        self._hourly_tips += 1
        return True

    def reset_hourly(self) -> None:
        self._hourly_tips = 0

    def read(self) -> SensorReading:
        accum_mm = self._tip_count * self.mm_per_tip
        hourly_mm = self._hourly_tips * self.mm_per_tip
        intensity_mm_hr = hourly_mm  # Assuming 1-hour rolling interval

        quality = "GOOD"
        if accum_mm > 500.0:
            quality = "INVALID"

        return SensorReading(
            sensor_type="rain_gauge",
            value=accum_mm,
            raw_value=float(self._tip_count),
            unit="mm",
            quality=quality,
            derived={
                "hourly_accumulation_mm": round(hourly_mm, 2),
                "intensity_mm_hr": round(intensity_mm_hr, 2),
                "tip_count": self._tip_count
            }
        )


class SoilMoistureReader(BaseSensorReader):
    """Time-Domain Reflectometry (TDR) volumetric water content probe."""

    def __init__(self, simulated_vwc: float = 0.35):
        super().__init__("soil_moisture", "m3/m3")
        self.vwc = simulated_vwc

    def set_simulated_vwc(self, vwc: float) -> None:
        self.vwc = vwc

    def read(self) -> SensorReading:
        cal = self.apply_calibration(self.vwc)
        quality = "GOOD" if 0.0 <= cal <= 1.0 else "INVALID"
        return SensorReading(
            sensor_type="soil_moisture",
            value=cal,
            raw_value=self.vwc,
            unit="m3/m3",
            quality=quality,
            derived={"vwc_percent": round(cal * 100.0, 1)}
        )


class TemperatureReader(BaseSensorReader):
    """Ambient and ground Pt100 RTD thermistor interface."""

    def __init__(self, simulated_temp_c: float = 18.5):
        super().__init__("temperature", "C")
        self.temp_c = simulated_temp_c

    def set_simulated_temperature(self, c: float) -> None:
        self.temp_c = c

    def read(self) -> SensorReading:
        cal = self.apply_calibration(self.temp_c)
        quality = "GOOD" if -40.0 <= cal <= 85.0 else "INVALID"
        return SensorReading(
            sensor_type="temperature",
            value=cal,
            raw_value=self.temp_c,
            unit="C",
            quality=quality
        )


class BatteryMonitorInterface:
    """Monitors DC voltage and estimates battery state of charge."""

    def __init__(self, initial_pct: float = 98.0, voltage: float = 3.65):
        self.battery_pct = initial_pct
        self.voltage = voltage

    def get_battery_level(self) -> float:
        return max(0.0, min(100.0, self.battery_pct))

    def get_voltage(self) -> float:
        return self.voltage

    def discharge(self, delta_pct: float = 0.01) -> None:
        self.battery_pct = max(0.0, self.battery_pct - delta_pct)


class SignalMonitorInterface:
    """Tracks wireless signal quality (RSSI in dBm and SNR in dB)."""

    def __init__(self, rssi: float = -75.0, snr: float = 8.5):
        self.rssi = rssi
        self.snr = snr

    def get_signal_rssi(self) -> float:
        return self.rssi

    def get_snr(self) -> float:
        return self.snr


class EdgeClock:
    """Hardware RTC / system clock with drift compensation."""

    def __init__(self, drift_offset_seconds: float = 0.0):
        self.drift_offset = drift_offset_seconds

    def set_drift_offset(self, offset_sec: float) -> None:
        self.drift_offset = offset_sec

    def get_epoch_seconds(self) -> int:
        return int(time.time() + self.drift_offset)

    def get_timestamp_iso(self) -> str:
        dt = datetime.fromtimestamp(self.get_epoch_seconds(), tz=timezone.utc)
        return dt.isoformat()


class LocalCircularBuffer:
    """
    Simulates embedded SPI NOR flash circular FIFO buffer (e.g. 512 KB SPIFFS).
    Guarantees strict FIFO replay without packet loss up to max_capacity.
    """

    def __init__(self, max_capacity: int = 500):
        self.max_capacity = max_capacity
        self._buffer: List[Dict[str, Any]] = []

    def push(self, packet_dict: Dict[str, Any]) -> bool:
        """Pushes packet into buffer. Drops oldest if full."""
        if len(self._buffer) >= self.max_capacity:
            self._buffer.pop(0)  # Circular overwrite of oldest
        self._buffer.append(packet_dict)
        return True

    def pop(self) -> Optional[Dict[str, Any]]:
        """Pops oldest packet (FIFO)."""
        if not self._buffer:
            return None
        return self._buffer.pop(0)

    def peek(self) -> Optional[Dict[str, Any]]:
        if not self._buffer:
            return None
        return self._buffer[0]

    def count(self) -> int:
        return len(self._buffer)

    def is_empty(self) -> bool:
        return len(self._buffer) == 0

    def clear(self) -> None:
        self._buffer.clear()
