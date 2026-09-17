"""
tests/test_runtime_data_truth.py
Comprehensive test suite verifying the Authoritative Runtime Data-Lineage
and Live-Data Truth Audit for PARVAT NETRA / PAHAD AI.
"""

import os
import csv
import json
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_CSV = os.path.join(BASE_DIR, 'reports', 'pahad_runtime_data_ledger.csv')
LEDGER_JSON = os.path.join(BASE_DIR, 'reports', 'pahad_runtime_data_ledger.json')
TRUTH_MATRIX_MD = os.path.join(BASE_DIR, 'reports', 'pahad_runtime_truth_matrix.md')
FORMULA_AUDIT_MD = os.path.join(BASE_DIR, 'reports', 'pahad_cri_runtime_formula_audit.md')
FLOW_MD = os.path.join(BASE_DIR, 'reports', 'pahad_runtime_data_flow.md')
CONTRADICTIONS_MD = os.path.join(BASE_DIR, 'reports', 'pahad_data_truth_contradictions.md')

VALID_DATA_CLASSES = {
    'LIVE_EXTERNAL',
    'CACHED_LIVE',
    'HISTORICAL',
    'STATIC_PREDEFINED',
    'MODEL_PRETRAINED',
    'SIMULATED',
    'DERIVED',
    'AUTH_REQUIRED',
    'UNAVAILABLE'
}

REQUIRED_LEDGER_COLUMNS = [
    "TIMESTAMP",
    "UI_FIELD",
    "API_ENDPOINT",
    "BACKEND_FUNCTION",
    "SOURCE",
    "PROVIDER",
    "SOURCE_URL",
    "VALUE",
    "UNIT",
    "SOURCE_TIMESTAMP",
    "INGESTED_AT",
    "STORED_AT",
    "SERVED_AT",
    "FRESHNESS_SECONDS",
    "CACHE_STATUS",
    "DATA_CLASS",
    "LIVE_CONTRIBUTION",
    "FALLBACK_PROVIDER",
    "USED_IN_CRI",
    "USED_IN_PAHAD",
    "USED_IN_MAP",
    "RUNTIME_EVIDENCE",
    "CONFIDENCE",
    "NOTES"
]


def test_audit_report_artifacts_exist():
    """All required reports must exist on disk."""
    assert os.path.exists(LEDGER_CSV), f"Missing {LEDGER_CSV}"
    assert os.path.exists(LEDGER_JSON), f"Missing {LEDGER_JSON}"
    assert os.path.exists(TRUTH_MATRIX_MD), f"Missing {TRUTH_MATRIX_MD}"
    assert os.path.exists(FORMULA_AUDIT_MD), f"Missing {FORMULA_AUDIT_MD}"
    assert os.path.exists(FLOW_MD), f"Missing {FLOW_MD}"
    assert os.path.exists(CONTRADICTIONS_MD), f"Missing {CONTRADICTIONS_MD}"


def test_runtime_ledger_csv_structure_and_counts():
    """Ledger CSV must contain exactly 47 rows and all 24 mandatory schema columns."""
    with open(LEDGER_CSV, mode='r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    
    assert len(reader) == 47, f"Expected 47 operational elements, found {len(reader)}"
    
    with open(LEDGER_CSV, mode='r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        header = next(csv_reader)
        assert header == REQUIRED_LEDGER_COLUMNS, f"Header mismatch: {header}"


def test_runtime_ledger_json_parity():
    """Ledger JSON must have exact record parity with CSV."""
    with open(LEDGER_JSON, mode='r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data.get("total_records") == 47
    records = data.get("records", [])
    assert len(records) == 47


def test_authoritative_data_classes_validity():
    """Every single row must have exactly ONE valid authoritative data class."""
    with open(LEDGER_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            dc = row['DATA_CLASS']
            assert dc in VALID_DATA_CLASSES, f"Row {i} ({row['UI_FIELD']}): Invalid DATA_CLASS '{dc}'"
            assert row['LIVE_CONTRIBUTION'] in ('HIGH', 'PARTIAL', 'ZERO')
            assert row['USED_IN_CRI'] in ('YES', 'NO')
            assert row['USED_IN_PAHAD'] in ('YES', 'NO')
            assert row['USED_IN_MAP'] in ('YES', 'NO')
            assert row['CONFIDENCE'] in ('HIGH', 'MEDIUM', 'LOW', 'LIMITED')
            assert len(row['RUNTIME_EVIDENCE']) > 15, f"Row {i} runtime evidence too brief"


def test_critical_telemetry_classifications():
    """Verify specific forensic truth invariants for key operational telemetry."""
    lookup = {}
    with open(LEDGER_CSV, mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            lookup[row['UI_FIELD']] = row

    # 1. CRI is DERIVED with PARTIAL live contribution
    cri = lookup.get('card-kpi-cri')
    assert cri['DATA_CLASS'] == 'DERIVED'
    assert cri['LIVE_CONTRIBUTION'] == 'PARTIAL'
    assert cri['USED_IN_CRI'] == 'YES'

    # 2. Factor of Safety is DERIVED
    fos = lookup.get('card-kpi-fos')
    assert fos['DATA_CLASS'] == 'DERIVED'
    assert fos['LIVE_CONTRIBUTION'] == 'PARTIAL'
    assert fos['USED_IN_CRI'] == 'YES'

    # 3. Event Probability is MODEL_PRETRAINED
    prob = lookup.get('card-kpi-prob')
    assert prob['DATA_CLASS'] == 'MODEL_PRETRAINED'
    assert prob['LIVE_CONTRIBUTION'] == 'PARTIAL'

    # 4. Rainfall is LIVE_EXTERNAL via Open-Meteo
    rain = lookup.get('ev-rain')
    assert rain['DATA_CLASS'] == 'LIVE_EXTERNAL'
    assert rain['LIVE_CONTRIBUTION'] == 'HIGH'
    assert 'Open-Meteo' in rain['PROVIDER']

    # 5. VWC Soil Moisture is SIMULATED with ZERO live contribution
    vwc = lookup.get('ev-vwc')
    assert vwc['DATA_CLASS'] == 'SIMULATED'
    assert vwc['LIVE_CONTRIBUTION'] == 'ZERO'

    # 6. Weather radar is AUTH_REQUIRED
    radar = lookup.get('weather-radar-overlay')
    assert radar['DATA_CLASS'] == 'AUTH_REQUIRED'
    assert radar['LIVE_CONTRIBUTION'] == 'ZERO'

    # 7. Regional CRI dataset is CACHED_LIVE
    spark = lookup.get('regional-hazard-sparkline')
    assert spark['DATA_CLASS'] == 'CACHED_LIVE'
    assert spark['LIVE_CONTRIBUTION'] == 'PARTIAL'

    # 8. Siren activation is SIMULATED (Dry run)
    siren = lookup.get('btn-arm-siren')
    assert siren['DATA_CLASS'] == 'SIMULATED'
    assert siren['LIVE_CONTRIBUTION'] == 'ZERO'


def test_factor_of_safety_physics_mechanics():
    """Verify Mohr-Coulomb limit equilibrium calculation logic."""
    from backend.risk_engine import calculate_factor_of_safety
    
    # Stable slope: high cohesion, moderate angle
    fs_stable = calculate_factor_of_safety(
        cohesion_kpa=25.0,
        phi_deg=32.0,
        gamma_kn_m3=19.5,
        depth_m=3.0,
        slope_beta_deg=25.0,
        suction_kpa=15.0,
        is_saturated=False,
        toe_resistance_loss_pct=0.0
    )
    assert fs_stable > 1.3, f"Expected stable FS, got {fs_stable}"

    # Critical slope: low cohesion, steep angle, toe erosion
    fs_critical = calculate_factor_of_safety(
        cohesion_kpa=5.0,
        phi_deg=22.0,
        gamma_kn_m3=20.0,
        depth_m=4.0,
        slope_beta_deg=45.0,
        suction_kpa=0.0,
        is_saturated=True,
        toe_resistance_loss_pct=50.0
    )
    assert fs_critical < 1.0, f"Expected critical FS < 1.0, got {fs_critical}"


def test_corroboration_gate_false_alarm_suppression():
    """Verify 2-of-3 corroboration gate caps false alarms at 79.9."""
    from engine.pahad_fusion import PahadFusionEngine

    engine = PahadFusionEngine()
    
    # Simulate single high signal with raw_cri >= 80.0 (tentative EXTREME, but only 1 signal confirmed)
    res = engine.fuse(
        sector_id="SEVOKE_GANGTOK_NH10",
        raw_cri=85.0,
        rainfall_threshold_exceeded=True,  # Signal 1: Rain = True
        fos_physical=1.65,                 # Signal 2: FoS stable = False
        event_probability_24h=0.45,        # Signal 3: ML prob low = False
        vulnerability_score=0.95
    )
    
    # Tentative score would be EXTREME, but only 1 signal confirmed -> capped at 79.9
    assert res['cri'] <= 79.9
    assert res['risk_band'] == 'VERY_HIGH'
    assert 'downgraded' in res
    assert res['downgraded'] is True
