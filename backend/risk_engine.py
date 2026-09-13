#!/usr/bin/env python3
"""
PARVAT NETRA -- Multimodal AI Risk Fusion Engine (Phase 12 / Sprint 2)
Physical Soil Mechanics & Hydrological Upgrades:
  1. van Genuchten (1980) Soil Water Characteristic Curve (SWCC) -> Matric Suction
  2. Green-Ampt Transient Infiltration Equation -> Wetting Front Penetration
  3. Extended Infinite-Slope Mohr-Coulomb Limit Equilibrium -> Factor of Safety (FS)
  4. Published Corridor-Specific Rainfall Threshold Ensemble (Pillar 4.2)
     - Mandal & Sarkar / GSI North Sikkim I-D Curve (I = 4.045 * D^-0.25)
     - Multi-Scale Antecedent Limits (24h: 130mm, 72h: 180mm, 15d: 250mm)
  5. Teesta Basin Hydrodynamic Toe Scour & Passive Resistance Degradation (Pillar 3.3)
     - Hydraulic Radius R, Basal Shear Stress tau_b, Critical Shear tau_c = 45 Pa
     - Degraded Toe Height h_toe and Passive Resistance Pp = 0.5 * gamma * h_toe^2 * Kp
     - Resisting Stress Deduction: (1.0 - (toe_loss_pct / 100.0) * 0.25)
  6. 5-Modality Evidence Fusion with Teesta Scour (+12) & Anthropogenic Hill Cuts (1.15x)
"""

import os
import sys
import math
import logging
from collections import namedtuple
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
import pandas as pd

# Safe console encoding for Windows cp1252
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PARVAT_NETRA_AI")


def load_env(filepath='.env'):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def get_db_connection():
    load_env()
    db_url = os.environ.get('NEON_DB_URL') or os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("NEON_DB_URL environment variable is missing.")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)


# =============================================================================
# SPRINT 1: GEOTECHNICAL SOIL MECHANICS & PHYSICAL FACTOR OF SAFETY
# =============================================================================

def vwc_to_suction(vwc_pct, theta_r=0.05, theta_s=0.42, alpha=0.03, n=1.45):
    """
    Converts Volumetric Water Content percentage (e.g. 48%) to matric suction in kPa
    using the inverted van Genuchten (1980) Soil Water Characteristic Curve (SWCC).
    """
    theta = float(vwc_pct) / 100.0
    denom = float(theta_s) - float(theta_r)
    if denom <= 0:
        denom = 0.001
    Se = (theta - float(theta_r)) / denom
    Se = max(0.001, min(0.999, Se))
    
    m = 1.0 - (1.0 / float(n))
    inner = (Se ** (-1.0 / m)) - 1.0
    inner = max(0.0, inner)
    
    matric_suction_kpa = (1.0 / float(alpha)) * (inner ** (1.0 / float(n)))
    return float(matric_suction_kpa)


def green_ampt_wetting_front(Ks=1e-5, psi_f=0.20, delta_theta=0.15, t_seconds=86400, max_iter=50):
    """
    Solves Green-Ampt cumulative infiltration F(t) iteratively:
      F = Ks * t
      For iteration:
        F_new = Ks * t + psi_f * delta_theta * ln(1 + F / (psi_f * delta_theta))
    Wetting front depth: Lf = F / delta_theta (meters).
    """
    if t_seconds <= 0:
        return 0.0
    F = float(Ks) * float(t_seconds)
    suction_term = float(psi_f) * float(delta_theta)
    for _ in range(max_iter):
        arg = 1.0 + F / max(suction_term, 1e-6)
        if arg <= 0:
            break
        F_new = float(Ks) * float(t_seconds) + suction_term * math.log(arg)
        if abs(F_new - F) < 1e-6:
            F = F_new
            break
        F = F_new
    Lf = F / max(float(delta_theta), 1e-4)
    return float(Lf)


def calculate_factor_of_safety(cohesion_kpa, phi_deg, gamma_kn_m3, depth_m, slope_beta_deg, suction_kpa, is_saturated=False, toe_resistance_loss_pct=0.0):
    """
    Implements the infinite-slope limit equilibrium model with unsaturated matric suction
    and hydrodynamic passive toe resistance degradation:
    
      beta_rad = radians(slope_beta_deg)
      phi_rad = radians(phi_deg)
      normal_stress = gamma_kn_m3 * depth_m * (cos(beta_rad) ** 2)
      
      If is_saturated is False:
        resisting_stress = cohesion_kpa + (normal_stress * tan(phi_rad)) + (suction_kpa * tan(phi_rad))
      Else:
        u_w = 9.81 * (depth_m * 0.5)  # Perched hydrostatic head
        resisting_stress = cohesion_kpa + ((normal_stress - u_w) * tan(phi_rad))
      
      If toe_resistance_loss_pct > 0.0:
        # Passive toe buttress loss reduces resisting shear capacity
        resisting_stress = resisting_stress * (1.0 - (toe_resistance_loss_pct / 100.0) * 0.25)
      
      driving_stress = gamma_kn_m3 * depth_m * sin(beta_rad) * cos(beta_rad)
      FS = resisting_stress / max(driving_stress, 0.001)
    
    Returns float FS value.
    """
    beta_rad = math.radians(float(slope_beta_deg))
    phi_rad = math.radians(float(phi_deg))
    normal_stress = float(gamma_kn_m3) * float(depth_m) * (math.cos(beta_rad) ** 2)

    if not is_saturated:
        resisting_stress = float(cohesion_kpa) + (normal_stress * math.tan(phi_rad)) + (float(suction_kpa) * math.tan(phi_rad))
    else:
        u_w = 9.81 * (float(depth_m) * 0.5)
        resisting_stress = float(cohesion_kpa) + ((normal_stress - u_w) * math.tan(phi_rad))

    if float(toe_resistance_loss_pct) > 0.0:
        deduction = (float(toe_resistance_loss_pct) / 100.0) * 0.25
        resisting_stress = resisting_stress * (1.0 - deduction)

    driving_stress = float(gamma_kn_m3) * float(depth_m) * math.sin(beta_rad) * math.cos(beta_rad)
    FS = resisting_stress / max(driving_stress, 0.001)
    return float(FS)


# =============================================================================
# SPRINT 2: CORRIDOR RAINFALL THRESHOLD ENSEMBLE (PILLAR 4.2)
# =============================================================================

def evaluate_rainfall_threshold_ensemble(intensity_mm_h, duration_h, rain_24h, rain_72h, rain_15d):
    """
    Evaluates the multi-scale corridor-specific rainfall threshold ensemble
    combining the Mandal & Sarkar / GSI intensity-duration curve with antecedent
    cumulative rainfall limits (Froehlich et al., Sengupta et al.).
    
    1. Primary I-D Curve (North Sikkim Corridor, Mandal & Sarkar / GSI baseline):
       threshold_intensity = 4.045 * (max(duration_h, 1.0) ** -0.25)
       is_id_breached = intensity_mm_h >= threshold_intensity
       is_id_watch = intensity_mm_h >= (0.5 * threshold_intensity)
       
    2. Antecedent Cumulative Limits:
       is_cum_24h_breached = rain_24h >= 130.0  (Froehlich et al.)
       is_cum_72h_breached = rain_72h >= 180.0
       is_cum_15d_breached = rain_15d >= 250.0  (Lanta Khola, Sengupta et al.)
       
    3. Dual OR-Trigger Evaluation:
       If is_id_breached OR is_cum_24h_breached OR is_cum_72h_breached OR is_cum_15d_breached:
         trigger_status = "WARNING_BREACH"
       Elif is_id_watch OR rain_24h >= 65.0:
         trigger_status = "WATCH_ELEVATED"
       Else:
         trigger_status = "NORMAL"
    """
    dur = max(float(duration_h), 1.0)
    threshold_intensity = 4.045 * (dur ** -0.25)
    is_id_breached = float(intensity_mm_h) >= threshold_intensity
    is_id_watch = float(intensity_mm_h) >= (0.5 * threshold_intensity)

    is_cum_24h_breached = float(rain_24h) >= 130.0
    is_cum_72h_breached = float(rain_72h) >= 180.0
    is_cum_15d_breached = float(rain_15d) >= 250.0

    if is_id_breached or is_cum_24h_breached or is_cum_72h_breached or is_cum_15d_breached:
        trigger_status = "WARNING_BREACH"
    elif is_id_watch or float(rain_24h) >= 65.0:
        trigger_status = "WATCH_ELEVATED"
    else:
        trigger_status = "NORMAL"

    return {
        "trigger_status": trigger_status,
        "threshold_intensity": round(threshold_intensity, 3),
        "intensity_mm_h": round(float(intensity_mm_h), 3),
        "duration_h": float(dur),
        "is_id_breached": is_id_breached,
        "is_id_watch": is_id_watch,
        "is_cum_24h_breached": is_cum_24h_breached,
        "is_cum_72h_breached": is_cum_72h_breached,
        "is_cum_15d_breached": is_cum_15d_breached,
        "rain_24h": float(rain_24h),
        "rain_72h": float(rain_72h),
        "rain_15d": float(rain_15d)
    }


# =============================================================================
# SPRINT 2: TEESTA BASAL SHEAR STRESS & PASSIVE TOE EROSION (PILLAR 3.3)
# =============================================================================

class ToeErosionResult(namedtuple('ToeErosionResult', ['h_toe', 'resistance_loss_pct', 'Pp_degraded'])):
    """
    Dual representation supporting both tuple unpacking (h_toe, resistance_loss_pct, Pp_degraded)
    and dictionary key / attribute access for pipeline integration.
    """
    def __new__(cls, h_toe, resistance_loss_pct, Pp_degraded, effective_toe_height_m=None,
                toe_resistance_loss_pct=None, passive_resistance_kn=None, initial_passive_resistance_kn=None,
                basal_shear_pa=0.0, excess_shear=0.0, scour_factor=0.0):
        obj = super().__new__(cls, h_toe, resistance_loss_pct, Pp_degraded)
        obj.effective_toe_height_m = effective_toe_height_m if effective_toe_height_m is not None else h_toe
        obj.toe_resistance_loss_pct = toe_resistance_loss_pct if toe_resistance_loss_pct is not None else resistance_loss_pct
        obj.passive_resistance_kn = passive_resistance_kn if passive_resistance_kn is not None else Pp_degraded
        obj.initial_passive_resistance_kn = initial_passive_resistance_kn
        obj.basal_shear_pa = basal_shear_pa
        obj.excess_shear = excess_shear
        obj.scour_factor = scour_factor
        return obj

    def __getitem__(self, item):
        if isinstance(item, str):
            return getattr(self, item)
        return super().__getitem__(item)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def to_dict(self):
        return {
            'h_toe': self.h_toe,
            'effective_toe_height_m': self.effective_toe_height_m,
            'resistance_loss_pct': self.resistance_loss_pct,
            'toe_resistance_loss_pct': self.toe_resistance_loss_pct,
            'Pp_degraded': self.Pp_degraded,
            'passive_resistance_kn': self.passive_resistance_kn,
            'initial_passive_resistance_kn': self.initial_passive_resistance_kn,
            'basal_shear_pa': self.basal_shear_pa,
            'excess_shear': self.excess_shear,
            'scour_factor': self.scour_factor
        }


def calculate_toe_erosion_degradation(water_level_m, danger_level_m, discharge_cusecs, river_distance_m,
                                      initial_toe_height_m=5.0, phi_deg=32.0, gamma_kn_m3=19.0):
    """
    Couples Teesta riverbed hydrodynamic basal shear stress to passive toe resistance degradation.
    
    Formulation:
      Hydraulic radius R = max(water_level_m * 0.35, 1.0)
      Energy slope S = 0.008 (steep mountain gorge)
      Basal shear stress tau_b = 1000.0 * 9.81 * R * S (Pa)
      Critical shear stress tau_c = 45.0 Pa (loose aggraded post-GLOF silt/talus)
      excess_shear = max((tau_b - tau_c) / tau_c, 0.0)
      stage_ratio = min(max(water_level_m / max(danger_level_m, 1.0), 0.5), 1.5)
      scour_factor = min(excess_shear * 0.15 * stage_ratio, 0.80)  # max 80% toe reduction
      
      Degraded toe height:
        h_toe = initial_toe_height_m * (1.0 - scour_factor)
      
      Passive Earth Resistance (Rankine):
        Kp = tan(45 + phi/2)^2
        Pp_initial = 0.5 * gamma * (h_initial^2) * Kp
        Pp_degraded = 0.5 * gamma * (h_toe^2) * Kp
        resistance_loss_pct = ((Pp_initial - Pp_degraded) / Pp_initial) * 100.0
    
    Returns ToeErosionResult with h_toe, resistance_loss_pct, Pp_degraded.
    """
    phi_rad = math.radians(float(phi_deg))
    Kp = math.tan(math.radians(45.0 + float(phi_deg) / 2.0)) ** 2
    Pp_initial = 0.5 * float(gamma_kn_m3) * (float(initial_toe_height_m) ** 2) * Kp

    if float(river_distance_m) > 250.0:
        return ToeErosionResult(
            h_toe=float(initial_toe_height_m),
            resistance_loss_pct=0.0,
            Pp_degraded=round(Pp_initial, 2),
            effective_toe_height_m=float(initial_toe_height_m),
            toe_resistance_loss_pct=0.0,
            passive_resistance_kn=round(Pp_initial, 2),
            initial_passive_resistance_kn=round(Pp_initial, 2),
            basal_shear_pa=0.0,
            excess_shear=0.0,
            scour_factor=0.0
        )

    # Channel Hydraulics
    R = max(float(water_level_m) * 0.35, 1.0)
    S = 0.008  # Steep mountain river slope
    tau_b = 1000.0 * 9.81 * R * S  # Pascals
    tau_c = 45.0  # Critical shear stress for aggraded sediment (Pa)

    excess_shear = max((tau_b - tau_c) / tau_c, 0.0)
    dl = max(float(danger_level_m), 1.0)
    stage_ratio = min(max(float(water_level_m) / dl, 0.5), 1.5)
    scour_factor = min(excess_shear * 0.15 * stage_ratio, 0.80)

    h_toe = float(initial_toe_height_m) * (1.0 - scour_factor)
    Pp_degraded = 0.5 * float(gamma_kn_m3) * (h_toe ** 2) * Kp
    resistance_loss_pct = ((Pp_initial - Pp_degraded) / max(Pp_initial, 0.001)) * 100.0

    return ToeErosionResult(
        h_toe=round(h_toe, 3),
        resistance_loss_pct=round(resistance_loss_pct, 2),
        Pp_degraded=round(Pp_degraded, 2),
        effective_toe_height_m=round(h_toe, 3),
        toe_resistance_loss_pct=round(resistance_loss_pct, 2),
        passive_resistance_kn=round(Pp_degraded, 2),
        initial_passive_resistance_kn=round(Pp_initial, 2),
        basal_shear_pa=round(tau_b, 2),
        excess_shear=round(excess_shear, 3),
        scour_factor=round(scour_factor, 3)
    )


# =============================================================================
# MULTIMODAL AI RISK FUSION ENGINE WITH HYDRAULIC TOE COUPLING
# =============================================================================

class LandslideRiskEngine5M:
    """
    PARVAT NETRA Multimodal Evidence Fusion Engine with Physical Geotechnical
    Soil Mechanics (SWCC + Green-Ampt + Mohr-Coulomb FoS), Multi-Scale Rainfall
    Threshold Ensemble (Pillar 4.2), and Teesta Basin Hydrodynamic Toe Scour (Pillar 3.3).
    """
    def __init__(self):
        load_env()
        self.db_url = os.environ.get('NEON_DB_URL') or os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("NEON_DB_URL environment variable is missing.")

    def get_connection(self, max_retries=3):
        import time
        for attempt in range(max_retries):
            try:
                return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor, connect_timeout=15)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1.0 * (attempt + 1))

    def fetch_fused_geodata(self, conn=None):
        """
        Executes a PostGIS spatial join fusing Static Terrain, Rainfall, 
        nearest IoT VWC Sensor, nearest PS-InSAR Satellite Point,
        nearest Teesta Waterways reach, and nearest Anthropogenic Cut site.
        """
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        cur = conn.cursor()
        
        query = """
        SELECT 
            t.id AS terrain_id,
            t.region_name,
            t.slope_angle::float AS slope_deg,
            t.soil_type,
            COALESCE(r.rainfall_mm::float, 50.0) AS rainfall_mm,
            COALESCE(s.vwc_pct::float, 45.0) AS vwc_pct,
            COALESCE(s.sensor_name, 'Regional Average') AS vwc_source,
            COALESCE(i.los_velocity::float, -5.0) AS insar_los_velocity,
            COALESCE(i.insar_location, 'Regional Scatterer') AS insar_source,
            COALESCE(tw.reach_name, 'No River Reach') AS river_reach_name,
            COALESCE(tw.scour_risk_level, 'LOW') AS river_scour_risk,
            COALESCE(tw.water_level_m, 0.0) AS river_water_level_m,
            COALESCE(tw.danger_level_m, 220.0) AS river_danger_level_m,
            COALESCE(tw.discharge_cusecs, 0.0) AS river_discharge_cusecs,
            COALESCE(tw.river_dist_m, 9999.0) AS river_dist_m,
            COALESCE(ac.cut_name, 'No Cut') AS cut_location_name,
            COALESCE(ac.cut_angle_deg, 0.0) AS cut_angle_deg,
            COALESCE(ac.cut_height_m, 0.0) AS cut_height_m,
            COALESCE(ac.has_retaining_wall, true) AS cut_has_wall,
            COALESCE(ac.cut_activity, 'NONE') AS cut_activity_type,
            COALESCE(ac.cut_dist_m, 9999.0) AS cut_dist_m
        FROM static_terrain t
        -- 1. Rainfall match (district / name)
        LEFT JOIN LATERAL (
            SELECT rainfall_mm 
            FROM raw_rainfall 
            WHERE t.region_name ILIKE '%' || district || '%'
            ORDER BY date DESC, id DESC LIMIT 1
        ) r ON TRUE
        -- 2. Nearest Soil Moisture VWC Sensor via PostGIS distance
        LEFT JOIN LATERAL (
            SELECT 
                st.value::float AS vwc_pct,
                sen.location_name AS sensor_name
            FROM iot_sensors sen
            JOIN sensor_telemetry st ON sen.sensor_id = st.sensor_id
            WHERE sen.sensor_type = 'SOIL_MOISTURE_VWC'
            ORDER BY ST_Distance(t.geom::geography, sen.geom::geography) ASC, st.recorded_at DESC
            LIMIT 1
        ) s ON TRUE
        -- 3. Nearest PS-InSAR Satellite Deformation Point via PostGIS distance
        LEFT JOIN LATERAL (
            SELECT 
                ins.los_velocity_mm_yr::float AS los_velocity,
                ins.location_name AS insar_location
            FROM insar_deformation ins
            ORDER BY ST_Distance(t.geom::geography, ins.geom::geography) ASC
            LIMIT 1
        ) i ON TRUE
        -- 4. Nearest Teesta Waterways reach via PostGIS distance
        LEFT JOIN LATERAL (
            SELECT 
                w.reach_name,
                w.water_level_m::float AS water_level_m,
                w.danger_level_m::float AS danger_level_m,
                w.discharge_cusecs::float AS discharge_cusecs,
                w.scour_risk_level,
                ST_Distance(t.geom::geography, w.geom::geography)::float AS river_dist_m
            FROM teesta_waterways w
            ORDER BY ST_Distance(t.geom::geography, w.geom::geography) ASC
            LIMIT 1
        ) tw ON TRUE
        -- 5. Nearest Anthropogenic Cut excavation site via PostGIS distance
        LEFT JOIN LATERAL (
            SELECT 
                c.location_name AS cut_name,
                c.cut_angle_deg::float AS cut_angle_deg,
                c.height_meters::float AS cut_height_m,
                c.has_retaining_wall,
                c.activity_type AS cut_activity,
                c.destabilization_index::float AS cut_destab_idx,
                ST_Distance(t.geom::geography, c.geom::geography)::float AS cut_dist_m
            FROM anthropogenic_cuts c
            ORDER BY ST_Distance(t.geom::geography, c.geom::geography) ASC
            LIMIT 1
        ) ac ON TRUE;
        """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        if should_close:
            conn.close()
        return rows

    def evaluate_5m_risk(self, rows):
        """
        Evaluates physical Factor of Safety (FS) alongside the 5-modality evidence fusion.
        Sprint 2 Integration:
          - Multi-scale rainfall threshold ensemble (I-D curve + 24h/72h/15d antecedent limits)
          - Teesta hydrodynamic toe erosion degradation (basal shear tau_b -> Pp loss)
          - Deducts resisting capacity based on passive toe resistance degradation %
        """
        results = []
        for r in rows:
            slope_val = float(r['slope_deg'])
            rain_val = float(r['rainfall_mm'])
            vwc_val = float(r['vwc_pct'])
            insar_val = float(r['insar_los_velocity'])

            # -----------------------------------------------------------------
            # 1. CORRIDOR RAINFALL THRESHOLD ENSEMBLE (SPRINT 2 - PILLAR 4.2)
            # -----------------------------------------------------------------
            intensity_mm_h = rain_val / 24.0
            duration_h = 24.0
            rain_24h = rain_val
            rain_72h = rain_val * 1.6  # Standard regional API hydrograph expansion
            rain_15d = rain_val * 2.8  # Deep regolith cumulative infiltration

            rain_ensemble = evaluate_rainfall_threshold_ensemble(
                intensity_mm_h=intensity_mm_h,
                duration_h=duration_h,
                rain_24h=rain_24h,
                rain_72h=rain_72h,
                rain_15d=rain_15d
            )
            rf_status = rain_ensemble['trigger_status']

            # -----------------------------------------------------------------
            # 2. TEESTA HYDRODYNAMIC TOE EROSION (SPRINT 2 - PILLAR 3.3)
            # -----------------------------------------------------------------
            river_dist = float(r['river_dist_m'])
            scour_level = str(r['river_scour_risk'])
            water_level = float(r.get('river_water_level_m') or 0.0)
            danger_level = float(r.get('river_danger_level_m') or 220.0)
            discharge = float(r.get('river_discharge_cusecs') or 0.0)

            if river_dist <= 250.0 and scour_level == 'CRITICAL':
                toe_data = calculate_toe_erosion_degradation(
                    water_level_m=water_level,
                    danger_level_m=danger_level,
                    discharge_cusecs=discharge,
                    river_distance_m=river_dist,
                    initial_toe_height_m=5.0,
                    phi_deg=32.0,
                    gamma_kn_m3=19.0
                )
                toe_scour_factor = 12.0
                toe_scour_desc = f"Teesta River Hydraulic Surge (+12.0) [{r['river_reach_name']} {r['river_scour_risk']} Scour]"
            else:
                toe_data = calculate_toe_erosion_degradation(
                    water_level_m=0.0,
                    danger_level_m=220.0,
                    discharge_cusecs=0.0,
                    river_distance_m=9999.0,
                    initial_toe_height_m=5.0,
                    phi_deg=32.0,
                    gamma_kn_m3=19.0
                )
                toe_scour_factor = 0.0
                toe_scour_desc = None

            toe_loss_pct = float(toe_data.toe_resistance_loss_pct)
            h_toe = float(toe_data.h_toe)
            pp_degraded = float(toe_data.passive_resistance_kn)

            # -----------------------------------------------------------------
            # 3. PHYSICAL GEOTECHNICAL SOIL MECHANICS & COUPLED FACTOR OF SAFETY
            # -----------------------------------------------------------------
            cohesion_kpa = 12.0     # Effective cohesion c' = 12.0 kPa
            phi_deg = 32.0          # Internal friction angle phi' = 32.0 deg
            gamma_kn_m3 = 19.0      # Total unit weight gamma = 19.0 kN/m^3
            depth_z_m = 3.5         # Shear slip depth z = 3.5 m

            # van Genuchten SWCC suction
            suction_kpa = vwc_to_suction(vwc_val)

            # Green-Ampt wetting front infiltration
            rain_duration_sec = 86400 if rain_val >= 50.0 else int(86400 * (rain_val / 50.0))
            lf_m = green_ampt_wetting_front(t_seconds=rain_duration_sec)
            is_saturated = bool(lf_m >= depth_z_m)

            # Compute coupled Factor of Safety with passive toe resistance loss
            fs = calculate_factor_of_safety(
                cohesion_kpa=cohesion_kpa,
                phi_deg=phi_deg,
                gamma_kn_m3=gamma_kn_m3,
                depth_m=depth_z_m,
                slope_beta_deg=slope_val,
                suction_kpa=suction_kpa,
                is_saturated=is_saturated,
                toe_resistance_loss_pct=toe_loss_pct
            )

            # Operational risk mapping from Physical FS:
            if fs < 1.0:
                fs_operational_level = 'RED'
            elif fs < 1.3:
                fs_operational_level = 'ORANGE'
            elif fs < 1.6:
                fs_operational_level = 'YELLOW'
            else:
                fs_operational_level = 'GREEN'

            # -----------------------------------------------------------------
            # 4. 5-MODALITY EVIDENCE FUSION CORE
            # -----------------------------------------------------------------
            slope_factor = float(np.clip(slope_val / 60.0, 0.0, 1.0))
            rain_factor = float(np.clip(rain_val / 100.0, 0.0, 1.0))
            vwc_factor = float(np.clip((vwc_val - 20.0) / 40.0, 0.0, 1.0))
            insar_factor = float(np.clip(abs(min(0.0, insar_val)) / 25.0, 0.0, 1.0))

            soil_str = str(r['soil_type']).lower()
            if 'sand' in soil_str or 'silt' in soil_str:
                soil_mult = 1.25
            elif 'alluvial' in soil_str or 'regolith' in soil_str:
                soil_mult = 1.10
            else:
                soil_mult = 1.0

            weighted_core = (0.25 * slope_factor) + (0.30 * rain_factor) + (0.20 * vwc_factor) + (0.15 * insar_factor)
            raw_score = weighted_core * soil_mult * 100.0
            raw_score += toe_scour_factor

            # Anthropogenic Hill-Cut Multiplier (1.15x if unreinforced cut > 60 deg within 300m)
            cut_dist = float(r['cut_dist_m'])
            cut_angle = float(r['cut_angle_deg'])
            cut_wall = bool(r['cut_has_wall'])
            if cut_dist <= 300.0 and cut_angle > 60.0 and not cut_wall:
                anthro_cut_factor = 1.15
                raw_score *= anthro_cut_factor
                anthro_cut_desc = f"Anthro Hill Cut Destabilization (1.15x) [{r['cut_location_name']} {cut_angle:.1f} deg]"
            else:
                anthro_cut_factor = 1.0
                anthro_cut_desc = None

            risk_index = float(np.clip(raw_score, 0.0, 100.0))

            # Severity classification: govern by the most critical of physical FS, rainfall threshold, or composite score
            if fs_operational_level == 'RED' or rf_status == 'WARNING_BREACH' or risk_index >= 75.0:
                severity = 'RED'
            elif fs_operational_level == 'ORANGE' or rf_status == 'WATCH_ELEVATED' or risk_index >= 50.0:
                severity = 'ORANGE'
            elif fs_operational_level == 'YELLOW' or risk_index >= 25.0:
                severity = 'YELLOW'
            else:
                severity = 'GREEN'

            # Diagnostic Explainability String
            why_parts = [
                f"Physical FoS: {fs:.3f} [{fs_operational_level}] (Suction: {suction_kpa:.1f}kPa, Lf: {lf_m:.2f}m)",
                f"Rain Threshold: {rf_status} (I-D Thresh: {rain_ensemble['threshold_intensity']:.2f}mm/h, Actual: {rain_ensemble['intensity_mm_h']:.2f}mm/h)",
                f"Slope(25%): {r['slope_deg']} deg",
                f"Rain(30%): {r['rainfall_mm']}mm",
                f"VWC(20%): {r['vwc_pct']}% [{r['vwc_source']}]",
                f"InSAR(15%): {r['insar_los_velocity']}mm/yr [{r['insar_source']}]",
                f"Soil(10%): {r['soil_type']} [x{soil_mult}]"
            ]
            if toe_scour_desc:
                why_parts.append(toe_scour_desc)
            if toe_loss_pct > 0.0:
                why_parts.append(f"Teesta Toe Scour: -{toe_loss_pct:.1f}% Passive Resistance (h_toe: {h_toe:.2f}m, Pp: {pp_degraded:.1f}kN/m)")
            if anthro_cut_desc:
                why_parts.append(anthro_cut_desc)

            why = " | ".join(why_parts)

            results.append({
                'region_name': r['region_name'],
                'base_fused_score': round(weighted_core * soil_mult * 100.0, 2),
                'risk_index': round(risk_index, 2),
                'final_risk_score': round(risk_index, 2),
                'severity_label': severity,
                'factor_of_safety': round(fs, 3),
                'fs_operational_level': fs_operational_level,
                'suction_kpa': round(suction_kpa, 2),
                'wetting_front_m': round(lf_m, 2),
                'is_saturated': is_saturated,
                'rainfall_threshold_status': rf_status,
                'rainfall_threshold_intensity': rain_ensemble['threshold_intensity'],
                'is_id_breached': rain_ensemble['is_id_breached'],
                'is_cum_24h_breached': rain_ensemble['is_cum_24h_breached'],
                'toe_resistance_loss_pct': round(toe_loss_pct, 2),
                'effective_toe_height_m': round(h_toe, 3),
                'passive_resistance_kn': round(pp_degraded, 2),
                'slope_factor': round(slope_factor, 3),
                'rain_factor': round(rain_factor, 3),
                'vwc_factor': round(vwc_factor, 3),
                'insar_factor': round(insar_factor, 3),
                'soil_multiplier': soil_mult,
                'toe_scour_factor': toe_scour_factor,
                'toe_scour_surge': toe_scour_factor,
                'anthro_cut_factor': anthro_cut_factor,
                'anthro_cut_multiplier': anthro_cut_factor,
                'river_distance_m': round(river_dist, 1),
                'cut_distance_m': round(cut_dist, 1),
                'explainability_why': why
            })
        return results

    def persist_results(self, evaluations, conn=None):
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        cur = conn.cursor()
        
        # Ensure audit columns exist
        cur.execute("ALTER TABLE ml_risk_scores ADD COLUMN IF NOT EXISTS factor_of_safety NUMERIC;")
        cur.execute("ALTER TABLE ml_risk_scores ADD COLUMN IF NOT EXISTS rainfall_threshold_status TEXT;")
        cur.execute("ALTER TABLE ml_risk_scores ADD COLUMN IF NOT EXISTS toe_resistance_loss_pct NUMERIC;")
        
        for ev in evaluations:
            cur.execute("""
                INSERT INTO ml_risk_scores 
                (region_name, risk_index, severity_label, slope_factor, rain_factor, vwc_factor, insar_factor, soil_multiplier,
                 toe_scour_factor, anthro_cut_factor, explainability_why, factor_of_safety, rainfall_threshold_status, toe_resistance_loss_pct)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                ev['region_name'],
                ev['risk_index'],
                ev['severity_label'],
                ev['slope_factor'],
                ev['rain_factor'],
                ev['vwc_factor'],
                ev['insar_factor'],
                ev['soil_multiplier'],
                ev['toe_scour_factor'],
                ev['anthro_cut_factor'],
                ev['explainability_why'],
                ev.get('factor_of_safety'),
                ev.get('rainfall_threshold_status'),
                ev.get('toe_resistance_loss_pct')
            ))
        conn.commit()
        cur.close()
        if should_close:
            conn.close()
        logger.info(f"Persisted {len(evaluations)} evaluations with physical FoS, rainfall thresholds & toe scour into ml_risk_scores.")


def run_risk_fusion_pipeline(conn=None):
    engine = LandslideRiskEngine5M()
    data = engine.fetch_fused_geodata(conn=conn)
    if data:
        evals = engine.evaluate_5m_risk(data)
        engine.persist_results(evals, conn=conn)
        return evals
    return []


if __name__ == "__main__":
    print("=" * 78)
    print("PARVAT NETRA -- MULTIMODAL AI RISK FUSION ENGINE (SPRINT 2)")
    print("Hydrological & Geotechnical Coupling:")
    print("  * van Genuchten SWCC + Green-Ampt Infiltration")
    print("  * Mandal & Sarkar / GSI North Sikkim Rainfall Threshold Ensemble (Pillar 4.2)")
    print("  * Teesta Basin Hydrodynamic Toe Scour & Passive Resistance Degradation (Pillar 3.3)")
    print("=" * 78)
    
    engine = LandslideRiskEngine5M()
    data = engine.fetch_fused_geodata()
    
    if data:
        evals = engine.evaluate_5m_risk(data)
        for ev in evals:
            badge = f"[{ev['severity_label']}]"
            print(f"\n{badge} Region: {ev['region_name']}")
            print(f"   Physical Factor of Safety (FS) : {ev['factor_of_safety']} [{ev['fs_operational_level']}]")
            print(f"   Rainfall Threshold Status     : {ev['rainfall_threshold_status']} (Thresh: {ev['rainfall_threshold_intensity']} mm/h)")
            print(f"   Teesta Toe Passive Loss       : -{ev['toe_resistance_loss_pct']}% (h_toe: {ev['effective_toe_height_m']}m, Pp: {ev['passive_resistance_kn']} kN/m)")
            print(f"   Matric Suction (van Genuchten): {ev['suction_kpa']} kPa")
            print(f"   Wetting Front (Green-Ampt)    : {ev['wetting_front_m']} m (Saturated: {ev['is_saturated']})")
            print(f"   Composite Risk Score          : {ev['risk_index']} / 100 [{ev['severity_label']}]")
            print(f"   Diagnostic 'Why'              : {ev['explainability_why']}")
        
        engine.persist_results(evals)
        print("\n" + "=" * 78)
        print("ALL SPRINT 2 EVALUATIONS SUCCESSFULLY PERSISTED TO POSTGIS")
        print("=" * 78)
    else:
        print("No spatial geodata returned for fusion.")
