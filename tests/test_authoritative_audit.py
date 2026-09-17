"""
tests/test_authoritative_audit.py
Verifies the 47-row authoritative data audit classification and CRI runtime trace.
"""
import os
import csv
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'reports', 'pahad_authoritative_data_audit.csv')
MD_PATH = os.path.join(BASE_DIR, 'reports', 'pahad_authoritative_data_audit.md')

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

def test_audit_files_exist():
    assert os.path.exists(CSV_PATH), f"Missing {CSV_PATH}"
    assert os.path.exists(MD_PATH), f"Missing {MD_PATH}"

def test_exactly_47_rows():
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 47, f"Expected 47 rows, found {len(reader)}"

def test_single_authoritative_data_class_per_row():
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            dc = row.get('DATA_CLASS')
            assert dc in VALID_DATA_CLASSES, f"Row {i} ({row.get('UI_FIELD')}): Invalid DATA_CLASS '{dc}'"

def test_mandatory_columns_present_and_valid():
    required_cols = [
        'ROW_INDEX',
        'UI_FIELD',
        'API_ENDPOINT',
        'SOURCE_NAME',
        'DATA_CLASS',
        'LIVE_CONTRIBUTION',
        'USED_IN_CRI',
        'USED_IN_PAHAD',
        'USED_IN_MAP',
        'USER_VISIBLE',
        'RUNTIME_ORIGIN_VERDICT'
    ]
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == required_cols
        for i, row in enumerate(reader, 1):
            assert row['LIVE_CONTRIBUTION'] in ('HIGH', 'PARTIAL', 'ZERO')
            assert row['USED_IN_CRI'] in ('YES', 'NO')
            assert row['USED_IN_PAHAD'] in ('YES', 'NO')
            assert row['USED_IN_MAP'] in ('YES', 'NO')
            assert row['USER_VISIBLE'] in ('YES', 'NO')
            assert len(row['RUNTIME_ORIGIN_VERDICT']) > 10

def test_cri_component_trace_in_markdown():
    with open(MD_PATH, mode='r', encoding='utf-8') as f:
        content = f.read()
    assert "## 3. Forensic Trace: Actual Runtime Value of Every CRI Component" in content
    assert "Open-Meteo" in content
    assert "Mohr-Coulomb" in content
    assert "CartoDEM" in content
    assert "van Genuchten" in content
    assert "THE HOMEPAGE NUMBER IS A HYBRID DERIVED CALCULATION" in content
