"""
engine/pahad_insar.py
=====================
PAHAD Phase 4 — NISAR InSAR & SAR Ground Deformation Engine
------------------------------------------------------------
Processes radar Line-of-Sight (LOS) velocity data from ISRO NISAR
(S-band) and Sentinel-1 (C-band) interferograms for hillslope
instability and creep acceleration analysis.

Key Geotechnical Formulations:
- Velocity: v = delta_d / delta_t (mm/day) & v_annual (mm/year)
- Acceleration: a = delta_v / delta_t (mm/day^2)
- Inverse-velocity: 1/v (Fukuzono 1985 / Voight 1988 tertiary creep)
- Creep States:
    v > 50 mm/year or a > 0.5 mm/day^2 -> TERTIARY_CREEP_ACCELERATION
    v > 15 mm/year                      -> STEADY_SECONDARY_CREEP
    Otherwise                           -> BASE_STABLE_OR_SETTLING
- Coherence validation threshold: >= 0.45

Author : PARVAT NETRA / PAHAD Engineering Team
Data   : [SIMULATED] ISRO NISAR S-band / Sentinel-1 InSAR feed
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

COHERENCE_THRESHOLD: float = 0.45
DAYS_PER_YEAR: float = 365.25


@dataclass
class InSARAnalysisResult:
    """Radar deformation processing result."""
    velocity_mm_day: float
    velocity_mm_year: float
    acceleration_mm_day2: float
    inverse_velocity: Optional[float]
    creep_status: str
    insar_anomaly_factor: float
    coherence: float
    coherence_reliable: bool
    reliability: str
    provenance: str = "[SIMULATED] ISRO NISAR S-band & Sentinel-1 InSAR"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "velocity_mm_day": round(self.velocity_mm_day, 4),
            "velocity_mm_year": round(self.velocity_mm_year, 2),
            "acceleration_mm_day2": round(self.acceleration_mm_day2, 5),
            "inverse_velocity": round(self.inverse_velocity, 4) if self.inverse_velocity is not None else None,
            "creep_status": self.creep_status,
            "insar_anomaly_factor": round(self.insar_anomaly_factor, 4),
            "coherence": round(self.coherence, 4),
            "coherence_reliable": self.coherence_reliable,
            "reliability": self.reliability,
            "provenance": self.provenance,
            "metadata": self.metadata,
        }


class InSARDeformationProcessor:
    """
    Radar Line-of-Sight deformation and creep analysis engine.
    Calibrated for Himalayan geotechnical formations.
    """

    def __init__(self, coherence_threshold: float = COHERENCE_THRESHOLD) -> None:
        self.coherence_threshold = coherence_threshold

    def analyze_slope_deformation(
        self,
        displacement_time_series_mm: List[float],
        time_intervals_days: List[float],
        coherence: float,
    ) -> Dict[str, Any]:
        """
        Analyze InSAR displacement time-series for velocity, acceleration,
        inverse-velocity (1/v), and tertiary creep transition.

        Parameters
        ----------
        displacement_time_series_mm : list[float]
            Cumulative or sequential Line-of-Sight displacements (mm).
        time_intervals_days : list[float]
            Cumulative days or per-interval step durations (days).
        coherence : float
            Interferometric coherence in range [0.0, 1.0].

        Returns
        -------
        dict
            Analysis output formatted per InSARAnalysisResult.
        """
        d_series = [float(x) for x in displacement_time_series_mm]
        t_series = [float(x) for x in time_intervals_days]
        coh = max(0.0, min(1.0, float(coherence)))

        if len(d_series) < 2 or len(t_series) < 2:
            # Fallback for insufficient sample length
            v_day = 0.0
            v_year = 0.0
            acc = 0.0
            inv_v = None
            creep = "BASE_STABLE_OR_SETTLING"
            a_factor = 0.05
        else:
            # Determine if time_intervals_days is cumulative or step-wise
            is_cumulative = all(t_series[i] < t_series[i + 1] for i in range(len(t_series) - 1))

            velocities: List[float] = []
            delta_times: List[float] = []

            for i in range(1, len(d_series)):
                delta_d = d_series[i] - d_series[i - 1]
                if is_cumulative:
                    delta_t = t_series[i] - t_series[i - 1]
                else:
                    delta_t = t_series[min(i - 1, len(t_series) - 1)]

                dt = max(delta_t, 0.001)
                delta_times.append(dt)
                velocities.append(delta_d / dt)

            # Latest velocity
            v_day = velocities[-1]
            v_year = v_day * DAYS_PER_YEAR

            # Acceleration (rate of velocity change)
            if len(velocities) >= 2:
                dt_acc = delta_times[-1]
                acc = (velocities[-1] - velocities[-2]) / max(dt_acc, 0.001)
            else:
                acc = 0.0

            # Inverse velocity (1/v) for Fukuzono / Voight tertiary creep estimation
            if v_day > 0.0001:
                inv_v = 1.0 / v_day
            else:
                inv_v = None

            # Creep State Evaluation
            # - Velocity > 50 mm/year or Acceleration > 0.5 mm/day^2 -> TERTIARY_CREEP_ACCELERATION
            # - Velocity > 15 mm/year                                -> STEADY_SECONDARY_CREEP
            # - Otherwise                                            -> BASE_STABLE_OR_SETTLING
            if v_year > 50.0 or acc > 0.5:
                creep = "TERTIARY_CREEP_ACCELERATION"
            elif v_year > 15.0:
                creep = "STEADY_SECONDARY_CREEP"
            else:
                creep = "BASE_STABLE_OR_SETTLING"

            # InSAR anomaly factor A_insar in range [0.0, 1.0] for CRI multi-modal fusion
            if creep == "TERTIARY_CREEP_ACCELERATION":
                base_factor = 0.80 + 0.20 * min(max(acc / 1.0, 0.0), 1.0)
            elif creep == "STEADY_SECONDARY_CREEP":
                base_factor = 0.40 + 0.38 * min(max((v_year - 15.0) / 35.0, 0.0), 1.0)
            else:
                base_factor = 0.35 * min(max(v_year / 15.0, 0.0), 1.0)

            a_factor = max(0.0, min(1.0, base_factor))

        # Coherence Reliability Assessment
        coherence_reliable = bool(coh >= self.coherence_threshold)
        reliability = "HIGH" if coherence_reliable else "LOW"

        result = InSARAnalysisResult(
            velocity_mm_day=v_day,
            velocity_mm_year=v_year,
            acceleration_mm_day2=acc,
            inverse_velocity=inv_v,
            creep_status=creep,
            insar_anomaly_factor=a_factor,
            coherence=coh,
            coherence_reliable=coherence_reliable,
            reliability=reliability,
            metadata={
                "displacement_samples": len(d_series),
                "coherence_threshold": self.coherence_threshold,
                "fukuzono_collapse_risk": bool(creep == "TERTIARY_CREEP_ACCELERATION" and inv_v is not None and inv_v < 0.1),
            },
        )
        return {
            "status": "SUCCESS",
            "data": result.to_dict(),
            "provenance": "[SIMULATED] ISRO NISAR S-band & Sentinel-1 InSAR",
        }
