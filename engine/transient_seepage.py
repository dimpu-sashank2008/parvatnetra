# -*- coding: utf-8 -*-
"""
engine/transient_seepage.py
============================
PAHAD AI — Transient Unsaturated Seepage & Pore-Water Pressure Engine
---------------------------------------------------------------------
Couples time-series precipitation infiltration with the van Genuchten (1980)
Soil-Water Characteristic Curve (SWCC) to compute dynamic matric suction loss,
wetting front propagation, and basal pore-water pressure accumulation (u_w(t))
along the potential Mohr-Coulomb failure surface.

Key Formulations:
1. van Genuchten (1980) SWCC:
     Theta(psi) = [1 + (alpha * |psi|)^n]^(-m),  m = 1 - 1/n
     theta(psi) = theta_r + (theta_s - theta_r) * Theta(psi)
     Effective Saturation: S_e = Theta(psi)

2. Hydraulic Conductivity Function:
     K(S_e) = K_sat * S_e^0.5 * [1 - (1 - S_e^(1/m))^m]^2

3. Unsaturated-Saturated Effective Normal Stress:
     sigma'* = (sigma_n - u_a) + S_e * (u_a - u_w)
     When u_w >= 0: sigma'* = sigma_n - u_w

4. Dynamic Factor of Safety (Lu & Likos 2004):
     FoS(t) = [c' + sigma'*(t) * tan(phi')] / [tau_driving]

Author: PARVAT NETRA / PAHAD Engineering Team
Standard: SIH Problem Statement ID: 26001 (MDoNER)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class SoilHydraulicParams:
    """Hydraulic and geotechnical properties of hillslope colluvium / residual soil."""
    theta_r: float = 0.08        # Residual volumetric water content (m^3/m^3)
    theta_s: float = 0.44        # Saturated volumetric water content (m^3/m^3)
    alpha_kpa: float = 0.12      # van Genuchten alpha parameter (1/kPa)
    n_index: float = 1.65        # van Genuchten pore size distribution parameter
    k_sat_m_s: float = 2.5e-5    # Saturated hydraulic conductivity (m/s) ~ 90 mm/h
    k_bedrock_drain_mm_h: float = 1.8    # Low-permeability bedrock basal drainage rate (mm/h)
    effective_cohesion_kpa: float = 6.5  # c' (kPa) for Himalayan colluvium / debris
    internal_friction_deg: float = 30.0   # phi' (deg)
    gamma_sat_kn_m3: float = 19.5         # Saturated soil unit weight (kN/m^3)
    gamma_w_kn_m3: float = 9.81           # Water unit weight (kN/m^3)

    @property
    def m_index(self) -> float:
        return 1.0 - (1.0 / max(1.05, self.n_index))


@dataclass
class TransientSeepageEpoch:
    """State of the soil column at a single hourly timestep."""
    hour: int
    rainfall_mm: float
    cumulative_rainfall_mm: float
    wetting_front_depth_m: float
    effective_saturation: float
    matric_suction_kpa: float
    pore_water_pressure_kpa: float
    perched_water_height_m: float
    effective_normal_stress_kpa: float
    shear_strength_kpa: float
    shear_stress_kpa: float
    factor_of_safety: float
    is_critical: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TransientSeepageResult:
    """Summary and trajectory of transient seepage analysis over a storm event."""
    sector_id: str
    slope_angle_deg: float
    slip_depth_m: float
    total_hours: int
    peak_rainfall_mmh: float
    total_storm_rainfall_mm: float
    min_factor_of_safety: float
    min_fos_hour: int
    initial_fos: float
    final_fos: float
    max_pore_pressure_kpa: float
    max_wetting_depth_m: float
    time_to_failure_hours: Optional[int]
    status: str
    epochs: List[TransientSeepageEpoch]
    provenance: str = "[PHYSICS] van Genuchten Transient Seepage Engine"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector_id": self.sector_id,
            "slope_angle_deg": round(self.slope_angle_deg, 1),
            "slip_depth_m": round(self.slip_depth_m, 2),
            "total_hours": self.total_hours,
            "peak_rainfall_mmh": round(self.peak_rainfall_mmh, 1),
            "total_storm_rainfall_mm": round(self.total_storm_rainfall_mm, 1),
            "min_factor_of_safety": round(self.min_factor_of_safety, 3),
            "min_fos_hour": self.min_fos_hour,
            "initial_fos": round(self.initial_fos, 3),
            "final_fos": round(self.final_fos, 3),
            "max_pore_pressure_kpa": round(self.max_pore_pressure_kpa, 2),
            "max_wetting_depth_m": round(self.max_wetting_depth_m, 2),
            "time_to_failure_hours": self.time_to_failure_hours,
            "status": self.status,
            "epoch_count": len(self.epochs),
            "provenance": self.provenance
        }


def van_genuchten_saturation(psi_kpa: float, alpha: float, n: float, m: float) -> float:
    """Computes effective saturation S_e from matric suction psi (kPa)."""
    if psi_kpa <= 0.0:
        return 1.0
    val = (1.0 + (alpha * psi_kpa) ** n) ** (-m)
    return max(0.0, min(1.0, float(val)))


def simulate_transient_seepage(
    rainfall_hourly_mm: List[float],
    slope_angle_deg: float,
    slip_depth_m: float = 2.0,
    initial_suction_kpa: float = 35.0,
    initial_volumetric_moisture: float = 0.36,
    soil_params: Optional[SoilHydraulicParams] = None,
    sector_id: str = "SK-NH10-KM48"
) -> TransientSeepageResult:
    """
    Simulates transient infiltration, suction loss, and pore-pressure dynamics
    across a multi-hour storm sequence.
    """
    params = soil_params or SoilHydraulicParams()
    beta_rad = math.radians(slope_angle_deg)
    phi_rad = math.radians(params.internal_friction_deg)
    cos_beta = math.cos(beta_rad)
    sin_beta = math.sin(beta_rad)

    # Static driving shear stress along slip plane: tau_d = gamma * z * sin(beta) * cos(beta)
    tau_driving = params.gamma_sat_kn_m3 * slip_depth_m * sin_beta * cos_beta
    if tau_driving <= 0.01:
        tau_driving = 0.01

    # Total normal stress on slip plane: sigma_n = gamma * z * cos^2(beta)
    sigma_total = params.gamma_sat_kn_m3 * slip_depth_m * (cos_beta ** 2)

    # Available moisture storage deficit (porosity minus antecedent moisture)
    delta_theta = max(0.04, params.theta_s - initial_volumetric_moisture)
    k_sat_mm_h = params.k_sat_m_s * 3600.0 * 1000.0  # mm/h

    current_wetting_depth = 0.4  # initial surface damp layer (m)
    current_suction = initial_suction_kpa
    perched_water_h = 0.0
    cum_rain = 0.0

    epochs: List[TransientSeepageEpoch] = []
    min_fos = float("inf")
    min_fos_hour = 0
    failure_hour = None

    for h_idx, rain in enumerate(rainfall_hourly_mm, start=1):
        cum_rain += rain

        # Infiltration capacity and wetting front descent rate
        # Green-Ampt infiltration rate
        infil_amount = min(rain, k_sat_mm_h)
        # Advance wetting front: dz = infil_amount / delta_theta (converted from mm to m)
        dz_m = (infil_amount / 1000.0) / delta_theta
        current_wetting_depth = min(slip_depth_m, current_wetting_depth + dz_m)

        # Matric suction dissipation as front approaches
        front_ratio = current_wetting_depth / slip_depth_m
        current_suction = max(0.0, initial_suction_kpa * (1.0 - front_ratio ** 1.8))

        se = van_genuchten_saturation(current_suction, params.alpha_kpa, params.n_index, params.m_index)

        # If wetting front has reached the basal slip boundary, perched positive pore pressure builds
        if current_wetting_depth >= slip_depth_m * 0.98:
            excess_water_m = max(0.0, (rain - params.k_bedrock_drain_mm_h) / 1000.0)
            perched_water_h = min(slip_depth_m, perched_water_h + excess_water_m / delta_theta)
            pore_pressure = params.gamma_w_kn_m3 * perched_water_h * (cos_beta ** 2)
            eff_normal = max(0.1, sigma_total - pore_pressure)
        else:
            perched_water_h = 0.0
            pore_pressure = -current_suction
            # Lu & Likos (2004) suction stress
            suction_stress = se * current_suction
            eff_normal = sigma_total + suction_stress

        # Mohr-Coulomb shear strength: tau_f = c' + sigma'* * tan(phi')
        shear_strength = params.effective_cohesion_kpa + eff_normal * math.tan(phi_rad)
        fos = shear_strength / tau_driving

        if fos < min_fos:
            min_fos = fos
            min_fos_hour = h_idx

        is_crit = fos < 1.0
        if is_crit and failure_hour is None:
            failure_hour = h_idx

        epochs.append(TransientSeepageEpoch(
            hour=h_idx,
            rainfall_mm=round(rain, 2),
            cumulative_rainfall_mm=round(cum_rain, 2),
            wetting_front_depth_m=round(current_wetting_depth, 3),
            effective_saturation=round(se, 3),
            matric_suction_kpa=round(current_suction, 2),
            pore_water_pressure_kpa=round(pore_pressure, 2),
            perched_water_height_m=round(perched_water_h, 3),
            effective_normal_stress_kpa=round(eff_normal, 2),
            shear_strength_kpa=round(shear_strength, 2),
            shear_stress_kpa=round(tau_driving, 2),
            factor_of_safety=round(fos, 3),
            is_critical=is_crit
        ))

    initial_fos = epochs[0].factor_of_safety if epochs else 1.5
    final_fos = epochs[-1].factor_of_safety if epochs else initial_fos
    max_pp = max(ep.pore_water_pressure_kpa for ep in epochs) if epochs else 0.0
    max_wd = max(ep.wetting_front_depth_m for ep in epochs) if epochs else 0.0
    peak_rain = max(rainfall_hourly_mm) if rainfall_hourly_mm else 0.0

    status = "CRITICAL_COLLAPSE" if min_fos < 1.0 else ("UNSTABLE_WATCH" if min_fos < 1.15 else "STABLE")

    return TransientSeepageResult(
        sector_id=sector_id,
        slope_angle_deg=slope_angle_deg,
        slip_depth_m=slip_depth_m,
        total_hours=len(rainfall_hourly_mm),
        peak_rainfall_mmh=peak_rain,
        total_storm_rainfall_mm=cum_rain,
        min_factor_of_safety=min_fos,
        min_fos_hour=min_fos_hour,
        initial_fos=initial_fos,
        final_fos=final_fos,
        max_pore_pressure_kpa=max_pp,
        max_wetting_depth_m=max_wd,
        time_to_failure_hours=failure_hour,
        status=status,
        epochs=epochs
    )
