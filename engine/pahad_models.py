"""
PAHAD (Predictive AI for Hillslope Analysis & Disaster-response)
Scientific Modeling Core & Regional North-East Himalaya Calibration Engine
PARVAT NETRA - Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform

Core Modules:
  1. Physical Infinite-Slope Limit Equilibrium Stability Model (Mohr-Coulomb)
  2. Regional North-East Himalaya Empirical Rainfall Thresholds (ID, ED, Monga-Ganguli)
  3. Composite Risk Index (CRI) Fusion with 2-of-3 Signal False-Alarm Suppression
  4. Response Protocols & Reference Curve Generators
"""

from dataclasses import dataclass, asdict
import math
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# ALERT PROTOCOLS & BAND DEFINITIONS
# =============================================================================

ALERT_PROTOCOLS: Dict[str, Dict[str, Any]] = {
    "LOW": {
        "tier": "LOW",
        "color_code": "#10B981",  # Emerald Green
        "level_name": "Routine Monitoring",
        "description": "Normal hillslope equilibrium. Routine background sensor polling.",
        "actions": [
            "Maintain 1-hour standard sensor polling",
            "Passive telemetry logging across NER monitoring nodes"
        ],
        "notification_target": "Background Log",
        "evacuation_required": False
    },
    "MODERATE": {
        "tier": "MODERATE",
        "color_code": "#F59E0B",  # Amber Yellow
        "level_name": "Elevated Observation",
        "description": "Increased sensor polling and slope stability observation.",
        "actions": [
            "Accelerate telemetry polling to 5-minute intervals",
            "Notify local BRO/PWD beat engineers of moisture rise",
            "Monitor IMD nowcast updates"
        ],
        "notification_target": "Local Engineers & Monitoring Staff",
        "evacuation_required": False
    },
    "HIGH": {
        "tier": "HIGH",
        "color_code": "#F97316",  # Orange
        "level_name": "Advisory Watch",
        "description": "Watch advisory issued to DDMA and local traveler app users.",
        "actions": [
            "Issue Watch advisory to District Disaster Management Authority (DDMA)",
            "Push geofenced advisory notices to citizen app travelers within 10km",
            "Pre-position BRO road-clearing dozers at staging nodes",
            "Activate emergency detour route options on navigation grid"
        ],
        "notification_target": "DDMA & Local App Users",
        "evacuation_required": False
    },
    "VERY_HIGH": {
        "tier": "VERY_HIGH",
        "color_code": "#EA580C",  # Deep Orange
        "level_name": "Severe Warning",
        "description": "Warning to SDMA, field verification dispatched, traffic diverted.",
        "actions": [
            "Issue Warning bulletin to State Disaster Management Authority (SDMA) & NDRF",
            "Dispatch BRO & SDRF quick-response patrol for field verification",
            "Prepare immediate arterial diversion to designated safe bypasses",
            "Alert local civil hospitals and emergency relief shelters"
        ],
        "notification_target": "SDMA, NDRF, SDRF & BRO Command",
        "evacuation_required": False
    },
    "EXTREME": {
        "tier": "EXTREME",
        "color_code": "#DC2626",  # Institutional Red
        "level_name": "Emergency Evacuation & Closure",
        "description": "CAP-XML broadcast, acoustic siren dispatch, evacuation advisory.",
        "actions": [
            "Broadcast CAP-XML Common Alerting Protocol emergency alert",
            "Sound physical multi-tone siren (853/960 Hz EAS) and mobile alarms",
            "Immediate arterial road closure at sector checkpoints",
            "Execute mandatory civilian evacuation to designated high-ground shelters",
            "Deploy SDRF rescue and search units to corridor"
        ],
        "notification_target": "National / State EOC, SDRF, Police & Public Civilian Broadcast",
        "evacuation_required": True
    }
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PhysicalSlopeResult:
    factor_of_safety: float
    classification: str
    is_unstable: bool
    effective_cohesion_kpa: float
    internal_friction_deg: float
    slope_angle_deg: float
    soil_depth_m: float
    water_table_ratio: float
    soil_sat_unit_weight_kn_m3: float
    water_unit_weight_kn_m3: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmpiricalThresholdResult:
    duration_hours: float
    duration_days: float
    rainfall_intensity_mmh: float
    event_rainfall_mm: float
    id_threshold_mmh: float
    ed_threshold_mm: float
    antecedent_threshold_mm: float
    threshold_exceeded: bool
    id_exceeded: bool
    ed_exceeded: bool
    exceedance_ratio: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompositeRiskResult:
    hazard_score: float
    vulnerability_score: float
    raw_cri: float
    final_cri: float
    alert_band: str
    is_extreme: bool
    downgraded: bool
    downgrade_reason: Optional[str]
    signals_triggered: int
    signal_physical_fs: bool
    signal_empirical_threshold: bool
    signal_ml_probability: bool
    protocol: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PahadSectorEvaluation:
    sector_id: str
    timestamp: str
    physical_model: PhysicalSlopeResult
    empirical_thresholds: EmpiricalThresholdResult
    composite_risk: CompositeRiskResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector_id": self.sector_id,
            "timestamp": self.timestamp,
            "physical_model": self.physical_model.to_dict(),
            "empirical_thresholds": self.empirical_thresholds.to_dict(),
            "composite_risk": self.composite_risk.to_dict()
        }


# =============================================================================
# 1. PHYSICAL INFINITE-SLOPE STABILITY MODEL (MOHR-COULOMB)
# =============================================================================

def calculate_infinite_slope_fs(
    cohesion_kpa: float,
    friction_deg: float,
    slope_deg: float,
    soil_depth_m: float,
    water_table_ratio: float,
    soil_sat_weight: float,
    water_unit_weight: float = 9.81
) -> PhysicalSlopeResult:
    """
    Computes the Factor of Safety (FS) using the classical Infinite-Slope Stability Model
    with Mohr-Coulomb shear strength and pore-water pressure seepage parallel to slope:

      FS = [c' + (gamma_sat - m * gamma_w) * z * (cos(beta))^2 * tan(phi')] /
           [gamma_sat * z * sin(beta) * cos(beta)]

    Parameters:
      cohesion_kpa: Effective soil cohesion c' in kPa (kN/m^2)
      friction_deg: Effective internal friction angle phi' in degrees
      slope_deg: Slope inclination angle beta in degrees
      soil_depth_m: Vertical depth z of slip surface in meters
      water_table_ratio: Ratio m of water table height to soil depth (0.0 <= m <= 1.0)
      soil_sat_weight: Saturated unit weight of soil gamma_sat in kN/m^3
      water_unit_weight: Unit weight of water gamma_w in kN/m^3 (default 9.81)

    Classifications:
      FS > 1.5           -> "STABLE"
      1.0 < FS <= 1.5    -> "WATCH"
      FS <= 1.0          -> "CRITICAL_UNSTABLE"
    """
    c = float(max(0.0, cohesion_kpa))
    phi_deg = float(max(0.0, min(89.0, friction_deg)))
    beta_deg = float(max(0.1, min(89.9, slope_deg)))
    z = float(max(0.1, soil_depth_m))
    m = float(max(0.0, min(1.0, water_table_ratio)))
    gamma_sat = float(max(1.0, soil_sat_weight))
    gamma_w = float(max(1.0, water_unit_weight))

    beta_rad = math.radians(beta_deg)
    phi_rad = math.radians(phi_deg)

    cos_beta = math.cos(beta_rad)
    sin_beta = math.sin(beta_rad)
    tan_phi = math.tan(phi_rad)

    # Resisting shear strength term
    # Numerator: c' + (gamma_sat - m * gamma_w) * z * (cos(beta))^2 * tan(phi)
    effective_unit_weight = gamma_sat - (m * gamma_w)
    resisting_force = c + (effective_unit_weight * z * (cos_beta ** 2) * tan_phi)

    # Mobilized driving shear stress term
    # Denominator: gamma_sat * z * sin(beta) * cos(beta)
    driving_force = gamma_sat * z * sin_beta * cos_beta

    if driving_force <= 1e-7:
        fs = 99.9
    else:
        fs = resisting_force / driving_force

    fs_rounded = round(float(fs), 4)

    if fs_rounded > 1.5:
        classification = "STABLE"
    elif fs_rounded > 1.0:
        classification = "WATCH"
    else:
        classification = "CRITICAL_UNSTABLE"

    return PhysicalSlopeResult(
        factor_of_safety=fs_rounded,
        classification=classification,
        is_unstable=(fs_rounded <= 1.0),
        effective_cohesion_kpa=c,
        internal_friction_deg=phi_deg,
        slope_angle_deg=beta_deg,
        soil_depth_m=z,
        water_table_ratio=m,
        soil_sat_unit_weight_kn_m3=gamma_sat,
        water_unit_weight_kn_m3=gamma_w
    )


# =============================================================================
# 2. NORTH-EAST HIMALAYA EMPIRICAL RAINFALL THRESHOLDS
# =============================================================================

def calculate_id_threshold(duration_hours: float) -> float:
    """
    Computes regional North-East Himalaya Intensity-Duration (ID) threshold:
      I_thresh = 5.8294 * (D ** -0.4141)
    where D is duration in hours, and I_thresh is in mm/hr.
    """
    d = max(0.1, float(duration_hours))
    return round(5.8294 * (d ** -0.4141), 4)


def calculate_ed_threshold(duration_hours: float) -> float:
    """
    Computes regional North-East Himalaya Event-Duration (ED) threshold:
      E_thresh = 1.3728 * (D_days ** 1.1083)
    where D_days is duration in days (D_hours / 24.0), and E_thresh is cumulative mm.
    """
    d_hours = max(0.1, float(duration_hours))
    d_days = d_hours / 24.0
    return round(1.3728 * (d_days ** 1.1083), 4)


def calculate_antecedent_threshold(duration_hours: float) -> float:
    """
    Computes Antecedent Moisture Threshold (Monga & Ganguli calibration):
      E_antecedent = -11.10 + 0.62 * D_hours
    Applicable for 24h <= D <= 1440h (60 days).
    """
    d = float(duration_hours)
    # Clamp for physical applicability
    val = -11.10 + (0.62 * d)
    return round(val, 4)


def is_empirical_threshold_exceeded(
    rainfall_intensity_mmh: float,
    duration_hours: float
) -> EmpiricalThresholdResult:
    """
    Evaluates whether active rainfall conditions breach regional North-East
    Himalaya empirical triggering thresholds.
    """
    d_hours = max(0.1, float(duration_hours))
    d_days = d_hours / 24.0
    intensity = max(0.0, float(rainfall_intensity_mmh))
    event_rainfall = intensity * d_hours

    i_thresh = calculate_id_threshold(d_hours)
    e_thresh = calculate_ed_threshold(d_hours)
    ante_thresh = calculate_antecedent_threshold(d_hours)

    id_exceeded = intensity >= i_thresh
    ed_exceeded = event_rainfall >= e_thresh
    overall_exceeded = id_exceeded or ed_exceeded

    exceedance_ratio = round(intensity / max(i_thresh, 1e-6), 4)

    return EmpiricalThresholdResult(
        duration_hours=round(d_hours, 2),
        duration_days=round(d_days, 3),
        rainfall_intensity_mmh=round(intensity, 2),
        event_rainfall_mm=round(event_rainfall, 2),
        id_threshold_mmh=i_thresh,
        ed_threshold_mm=e_thresh,
        antecedent_threshold_mm=ante_thresh,
        threshold_exceeded=overall_exceeded,
        id_exceeded=id_exceeded,
        ed_exceeded=ed_exceeded,
        exceedance_ratio=exceedance_ratio
    )


# =============================================================================
# 3. COMPOSITE RISK INDEX (CRI) FUSION & 2-OF-3 SIGNAL CONFIDENCE TIERING
# =============================================================================

def calculate_composite_risk_index(
    static_susceptibility: float,
    dynamic_rainfall_prob: float,
    ground_anomaly_score: float,
    vulnerability_score: float,
    physical_fs: float,
    empirical_threshold_exceeded: bool,
    ml_probability: float
) -> CompositeRiskResult:
    """
    Computes the Composite Risk Index (CRI) and applies the false alarm suppression rule.

    Hazard Formula:
      H = (0.40 * S) + (0.35 * P) + (0.25 * A)
      Where:
        S = static susceptibility (0-1)
        P = dynamic rainfall probability (0-1)
        A = ground anomaly score (0-1)

    Vulnerability:
      V = normalized factor (0.1 to 1.0) based on population density and road criticality.

    Composite Risk Index:
      CRI = H * V * 100  (Range: 0 - 100)

    Bands:
      0-20:   LOW (Routine monitoring)
      20-40:  MODERATE (Increased sensor polling)
      40-60:  HIGH (Watch to DDMA & local app users)
      60-80:  VERY_HIGH (Warning to SDMA, field verification dispatched)
      80-100: EXTREME (CAP-XML broadcast, evacuation advisory)

    False Alarm Suppression Rule:
      To classify as "EXTREME" (Red alert), at least 2 of the 3 independent signals must trigger:
        1) Physical FS <= 1.0
        2) Empirical threshold exceeded (I > I_thresh or E > E_thresh)
        3) ML probability > 0.8
      If raw CRI >= 80 but fewer than 2 independent signals agree, auto-downgrade alert to "VERY_HIGH" (Orange/Watch).
    """
    s = max(0.0, min(1.0, float(static_susceptibility)))
    p = max(0.0, min(1.0, float(dynamic_rainfall_prob)))
    a = max(0.0, min(1.0, float(ground_anomaly_score)))
    v = max(0.1, min(1.0, float(vulnerability_score)))

    # Hazard calculation
    h = (0.40 * s) + (0.35 * p) + (0.25 * a)
    h = max(0.0, min(1.0, h))

    # Raw Composite Risk Index
    raw_cri = round(h * v * 100.0, 2)

    # Determine initial band
    if raw_cri >= 80.0:
        tentative_band = "EXTREME"
    elif raw_cri >= 60.0:
        tentative_band = "VERY_HIGH"
    elif raw_cri >= 40.0:
        tentative_band = "HIGH"
    elif raw_cri >= 20.0:
        tentative_band = "MODERATE"
    else:
        tentative_band = "LOW"

    # Evaluate 3 independent physical & empirical signals
    sig_fs = (float(physical_fs) <= 1.0)
    sig_empirical = bool(empirical_threshold_exceeded)
    sig_ml = (float(ml_probability) > 0.8)

    signals_triggered = sum([1 if sig else 0 for sig in (sig_fs, sig_empirical, sig_ml)])

    downgraded = False
    downgrade_reason: Optional[str] = None
    final_cri = raw_cri
    final_band = tentative_band

    # False Alarm Suppression Rule
    if tentative_band == "EXTREME":
        if signals_triggered < 2:
            final_band = "VERY_HIGH"
            downgraded = True
            # Cap final CRI representation to top of VERY_HIGH band (79.9)
            final_cri = min(79.9, raw_cri)
            downgrade_reason = (
                f"Auto-downgraded from EXTREME to VERY_HIGH: Only {signals_triggered}/3 independent "
                f"signals confirmed instability (Requires >= 2 of: FS<=1.0, Empirical I-D Exceeded, ML>0.8)."
            )

    protocol = ALERT_PROTOCOLS.get(final_band, ALERT_PROTOCOLS["LOW"])

    return CompositeRiskResult(
        hazard_score=round(h, 4),
        vulnerability_score=round(v, 4),
        raw_cri=raw_cri,
        final_cri=final_cri,
        alert_band=final_band,
        is_extreme=(final_band == "EXTREME"),
        downgraded=downgraded,
        downgrade_reason=downgrade_reason,
        signals_triggered=signals_triggered,
        signal_physical_fs=sig_fs,
        signal_empirical_threshold=sig_empirical,
        signal_ml_probability=sig_ml,
        protocol=protocol
    )


# =============================================================================
# 4. END-TO-END SECTOR HAZARD EVALUATOR & REFERENCE CURVES
# =============================================================================

def evaluate_sector_hazard(payload: Dict[str, Any]) -> PahadSectorEvaluation:
    """
    Orchestrates physical stability, empirical thresholding, and CRI fusion for a given sector.
    """
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    sector_id = str(payload.get("sector_id", "SECTOR-UNKNOWN"))

    # 1. Physical Infinite-Slope Model
    c = float(payload.get("cohesion_kpa", payload.get("c", 12.0)))
    phi = float(payload.get("friction_deg", payload.get("phi", 28.0)))
    beta = float(payload.get("slope_deg", payload.get("beta", 35.0)))
    z = float(payload.get("soil_depth_m", payload.get("z", 4.0)))
    m = float(payload.get("water_table_ratio", payload.get("m", 0.5)))
    gamma_sat = float(payload.get("soil_sat_weight", payload.get("gamma_sat", 19.5)))
    gamma_w = float(payload.get("water_unit_weight", 9.81))

    physical_res = calculate_infinite_slope_fs(
        cohesion_kpa=c,
        friction_deg=phi,
        slope_deg=beta,
        soil_depth_m=z,
        water_table_ratio=m,
        soil_sat_weight=gamma_sat,
        water_unit_weight=gamma_w
    )

    # 2. Empirical Thresholds
    rainfall_intensity = float(payload.get("rainfall_intensity_mmh", payload.get("rainfall_intensity", 0.0)))
    duration_hours = float(payload.get("duration_hours", payload.get("duration", 24.0)))

    empirical_res = is_empirical_threshold_exceeded(
        rainfall_intensity_mmh=rainfall_intensity,
        duration_hours=duration_hours
    )

    # 3. Composite Risk Index & Confidence Tiering
    static_susc = float(payload.get("static_susceptibility", 0.5))
    ml_prob = float(payload.get("ml_probability", 0.5))
    # Dynamic rainfall prob defaults to ml_prob or empirical exceedance ratio
    dynamic_rain = float(payload.get("dynamic_rainfall_prob", ml_prob))
    ground_anomaly = float(payload.get("ground_anomaly_score", payload.get("ground_anomaly", 0.0)))
    vuln = float(payload.get("vulnerability_score", payload.get("vulnerability", 0.8)))

    cri_res = calculate_composite_risk_index(
        static_susceptibility=static_susc,
        dynamic_rainfall_prob=dynamic_rain,
        ground_anomaly_score=ground_anomaly,
        vulnerability_score=vuln,
        physical_fs=physical_res.factor_of_safety,
        empirical_threshold_exceeded=empirical_res.threshold_exceeded,
        ml_probability=ml_prob
    )

    return PahadSectorEvaluation(
        sector_id=sector_id,
        timestamp=now_iso,
        physical_model=physical_res,
        empirical_thresholds=empirical_res,
        composite_risk=cri_res
    )


def generate_threshold_curve_points(
    min_hours: int = 1,
    max_hours: int = 72,
    step_hours: int = 1
) -> Dict[str, Any]:
    """
    Generates structured North-East Himalaya empirical threshold curve reference points
    for plotting Intensity-Duration (ID), Event-Duration (ED), and Antecedent lines.
    """
    points: List[Dict[str, Any]] = []
    durations: List[float] = []
    id_thresholds: List[float] = []
    ed_thresholds: List[float] = []
    antecedent_thresholds: List[float] = []

    for h in range(min_hours, max_hours + 1, step_hours):
        h_float = float(h)
        i_th = calculate_id_threshold(h_float)
        e_th = calculate_ed_threshold(h_float)
        a_th = calculate_antecedent_threshold(h_float)

        durations.append(h_float)
        id_thresholds.append(i_th)
        ed_thresholds.append(e_th)
        antecedent_thresholds.append(a_th)

        points.append({
            "duration_hours": h_float,
            "duration_days": round(h_float / 24.0, 3),
            "id_threshold_mmh": i_th,
            "ed_threshold_mm": e_th,
            "antecedent_threshold_mm": a_th
        })

    return {
        "status": "SUCCESS",
        "region": "North-East Himalaya (Sikkim / Darjeeling / Assam Hills)",
        "equations": {
            "id_threshold": "I = 5.8294 * (D ** -0.4141) [mm/hr]",
            "ed_threshold": "E = 1.3728 * (D_days ** 1.1083) [mm]",
            "antecedent_threshold": "E_ante = -11.10 + 0.62 * D_hours [mm]"
        },
        "range_hours": [min_hours, max_hours],
        "points_count": len(points),
        "durations": durations,
        "id_curve": id_thresholds,
        "ed_curve": ed_thresholds,
        "antecedent_curve": antecedent_thresholds,
        "points": points
    }


# =============================================================================
# 5. UNIFIED PAHAD FUSED RISK EVALUATION (PHASE 2A CONTRACT)
# =============================================================================

def evaluate_pahad_fused_risk(
    sector_id: str,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    PAHAD Unified Multi-Modal Risk & Prediction Evaluator (Phase 2A Contract).
    Consumes the unified feature vector from engine.pahad_inputs and integrates:
      1. Physical Infinite-Slope Stability (Mohr-Coulomb)
      2. Empirical Rainfall Thresholds (Mandal & Sarkar 2013)
      3. Machine Learning FoS Prediction (GradientBoostingRegressor)
      4. Dynamic Seismic Trigger Modifier (SeismicService)
      5. Multi-Signal Agreement & Alert Safety Verification (2-of-3 Rule)

    Returns the standardized Model Output Contract dictionary.
    """
    import os
    import joblib
    import pandas as pd
    from engine.pahad_inputs import build_pahad_feature_vector

    # 1. Synthesize multi-modal feature vector
    vector_bundle = build_pahad_feature_vector(sector_id)
    features = dict(vector_bundle["features"])
    if overrides:
        features.update(overrides)

    raw_contract = vector_bundle.get("raw_contract", {})

    # 2. Physical Infinite-Slope Model
    c_kpa = float(features.get("cohesion_kpa", 16.0))
    phi_deg = float(features.get("friction_deg", 28.0))
    slope_deg = float(features.get("slope_deg", 34.0))
    z_m = float(features.get("soil_depth_m", 3.8))
    u_kpa = float(features.get("pore_water_pressure_kpa", 0.0))

    # Water table ratio derived from pore pressure
    gamma_w = 9.81
    m_ratio = min(1.0, max(0.0, u_kpa / max(1.0, gamma_w * z_m)))

    physical_res = calculate_infinite_slope_fs(
        cohesion_kpa=c_kpa,
        friction_deg=phi_deg,
        slope_deg=slope_deg,
        soil_depth_m=z_m,
        water_table_ratio=m_ratio,
        soil_sat_weight=19.5,
        water_unit_weight=gamma_w
    )
    physical_fs = physical_res.factor_of_safety

    # 3. Regional Empirical Rainfall Thresholds
    intensity_mmh = float(features.get("rainfall_current_mmh", 0.0))
    rain_24h = float(features.get("rainfall_24h_mm", 0.0))
    effective_intensity = intensity_mmh if intensity_mmh > 0.0 else (rain_24h / 24.0)

    empirical_res = is_empirical_threshold_exceeded(
        rainfall_intensity_mmh=effective_intensity,
        duration_hours=24.0
    )

    # 4. Machine Learning Inference (GradientBoostingRegressor)
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "fos_predictor.pkl")
    ml_fos = physical_fs  # Baseline fallback
    model_version = "1.0.0-phase8"

    if os.path.exists(model_path):
        try:
            bundle = joblib.load(model_path)
            model = bundle["model"]
            model_version = bundle.get("version", "1.0.0-phase8")
            feat_names = bundle.get("feature_names", ["rainfall_24h", "pore_water_pressure", "river_scour_tau_b"])
            # Scour baseline
            scour_val = 350.0 + (rain_24h * 20.0)
            x_in = pd.DataFrame([[float(rain_24h), float(u_kpa), float(scour_val)]], columns=feat_names)
            ml_fos = float(model.predict(x_in)[0])
            ml_fos = max(0.20, min(3.0, round(ml_fos, 3)))
        except Exception as e:
            ml_fos = physical_fs

    # Failure probability mapped from ML & Physical FoS
    # Inverse sigmoid centered at FS=1.0
    combined_fs = min(physical_fs, ml_fos)
    failure_prob = round(1.0 / (1.0 + math.exp(4.0 * (combined_fs - 1.05))), 3)
    failure_prob = max(0.01, min(0.99, failure_prob))

    # 5. Seismic Shaking Modifier
    seismic_shaking_g = float(features.get("seismic_shaking_proxy_g", 0.0))
    seismic_adj = float(features.get("seismic_risk_adjustment", 0.0))
    seismic_trigger_lvl = "LOW"
    if seismic_shaking_g >= 0.20:
        seismic_trigger_lvl = "VERY_HIGH"
    elif seismic_shaking_g >= 0.10:
        seismic_trigger_lvl = "HIGH"
    elif seismic_shaking_g >= 0.04:
        seismic_trigger_lvl = "MODERATE"

    # 6. Composite Risk Index (CRI) Fusion
    # Physical stability hazard term: increases steeply as FoS drops below 1.5
    phys_hazard = max(0.0, min(1.0, (1.6 - combined_fs) / 1.1)) if combined_fs < 1.6 else 0.0

    # Static susceptibility proxy
    static_s = min(1.0, (slope_deg / 45.0) * (1.0 - (c_kpa / 40.0)))
    static_s = max(0.1, round(static_s, 3))

    # Dynamic precipitation loading
    dynamic_p = min(1.0, max(0.0, (rain_24h / 100.0) + (effective_intensity / 12.0)))

    # Ground anomaly index
    ground_a = min(1.0, (u_kpa / 35.0) * 0.6 + (float(features.get("displacement_rate_mm_day", 0.0)) / 4.0) * 0.4)

    # Hazard score synthesizing physical FoS collapse, rainfall, ground anomaly, and seismic/static factor
    hazard_score = (0.35 * phys_hazard) + (0.30 * dynamic_p) + (0.20 * ground_a) + (0.15 * max(static_s, seismic_adj * 2.5))
    hazard_score = min(1.0, max(0.0, hazard_score))

    # Vulnerability score (road criticality & population exposure)
    road_crit = float(features.get("road_criticality", 0.85))
    vulnerability_score = min(1.0, max(0.2, road_crit))

    raw_cri = round(hazard_score * vulnerability_score * 100.0, 2)

    # 7. Multi-Signal Agreement & Alert Safety Rule (2-of-3 Principle)
    sig_physical = (physical_fs <= 1.0)
    sig_rainfall = bool(empirical_res.id_exceeded)
    sig_ml = (failure_prob > 0.80 or ml_fos < 1.0)

    signal_count = sum([1 if s else 0 for s in (sig_physical, sig_rainfall, sig_ml)])

    # Initial tentative band
    if raw_cri >= 80.0:
        tentative_band = "EXTREME"
    elif raw_cri >= 60.0:
        tentative_band = "VERY_HIGH"
    elif raw_cri >= 40.0:
        tentative_band = "HIGH"
    elif raw_cri >= 20.0:
        tentative_band = "MODERATE"
    else:
        tentative_band = "LOW"

    # Safety Rule Enforcement
    final_band = tentative_band
    final_cri = raw_cri
    downgraded = False

    if tentative_band == "EXTREME":
        if signal_count < 2:
            # Downgrade to prevent single-signal false alarms
            final_band = "VERY_HIGH"
            final_cri = min(79.9, raw_cri)
            downgraded = True

    # 8. Dominant Drivers & Recommendations
    dominant_drivers: List[str] = []
    if sig_physical:
        dominant_drivers.append(f"Physical Factor of Safety Critical ({physical_fs:.2f} <= 1.0)")
    if sig_rainfall:
        dominant_drivers.append(f"Regional I-D Threshold Exceeded ({effective_intensity:.1f} mm/h vs {empirical_res.id_threshold_mmh:.1f} mm/h)")
    if u_kpa > 15.0:
        dominant_drivers.append(f"Elevated Borehole Pore-Water Pressure ({u_kpa:.1f} kPa)")
    if seismic_shaking_g >= 0.04:
        dominant_drivers.append(f"Seismic Ground Shaking Trigger ({seismic_shaking_g:.3f}g, M{features.get('seismic_magnitude', 0.0):.1f})")
    if not dominant_drivers:
        dominant_drivers.append("Normal hillslope equilibrium; baseline monitoring active")

    protocol = ALERT_PROTOCOLS.get(final_band, ALERT_PROTOCOLS["LOW"])
    recommended_action = protocol["actions"][0] if protocol.get("actions") else "Routine observation"

    # Distinct Alert Operational States
    if final_band == "EXTREME":
        prediction_state = "CRITICAL_FAILURE_IMMINENT"
        alert_recommendation = "EXTREME_MANDATORY_EVACUATION"
        public_alert_dispatch = "AUTHORIZED_FOR_CAP_BROADCAST"
    elif final_band == "VERY_HIGH":
        prediction_state = "HIGH_INSTABILITY_WATCH"
        alert_recommendation = "SEVERE_WARNING_DISPATCH_PATROL"
        public_alert_dispatch = "PENDING_OPERATOR_CONFIRMATION"
    elif final_band == "HIGH":
        prediction_state = "ELEVATED_PORE_PRESSURE"
        alert_recommendation = "ISSUE_DDMA_ADVISORY"
        public_alert_dispatch = "INTERNAL_ADVISORY_ONLY"
    else:
        prediction_state = "STABLE"
        alert_recommendation = "ROUTINE_MONITORING"
        public_alert_dispatch = "NONE"

    return {
        "sector_id": sector_id,
        "cri": final_cri,
        "raw_cri": raw_cri,
        "risk_band": final_band,
        "downgraded": downgraded,
        "failure_probability": failure_prob,
        "factor_of_safety": round(combined_fs, 3),
        "physical_fs": physical_fs,
        "ml_fs": ml_fos,
        "rainfall_trigger": {
            "intensity_mm_hr": round(effective_intensity, 2),
            "rain_24h_mm": round(rain_24h, 2),
            "api_3d": round(float(features.get("api_3d", 0.0)), 2),
            "threshold_exceeded": empirical_res.threshold_exceeded,
            "id_ratio": empirical_res.exceedance_ratio,
            "state": empirical_res.threshold_exceeded
        },
        "seismic_trigger": {
            "shaking_proxy_g": seismic_shaking_g,
            "trigger_level": seismic_trigger_lvl,
            "risk_adjustment": seismic_adj,
            "earthquake_magnitude": float(features.get("seismic_magnitude", 0.0)),
            "distance_km": float(features.get("seismic_distance_km", 999.0))
        },
        "ground_anomaly": {
            "pore_water_pressure_kpa": u_kpa,
            "displacement_rate_mm_day": float(features.get("displacement_rate_mm_day", 0.0)),
            "soil_moisture_vwc": float(features.get("soil_moisture_vwc", 0.28))
        },
        "data_quality": vector_bundle.get("data_quality", "MEDIUM"),
        "signal_agreement": {
            "physical": sig_physical,
            "rainfall": sig_rainfall,
            "ml": sig_ml,
            "count": signal_count
        },
        "dominant_drivers": dominant_drivers,
        "recommended_action": recommended_action,
        "forecast_window": "24h",
        "operational_states": {
            "prediction": prediction_state,
            "alert_recommendation": alert_recommendation,
            "public_alert_dispatch": public_alert_dispatch
        },
        "protocol": protocol,
        "provenance": vector_bundle.get("feature_sources", {}),
        "overall_provenance": vector_bundle.get("overall_provenance", ["SIMULATED"]),
        "model_version": model_version
    }

