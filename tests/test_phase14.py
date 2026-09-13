"""
PARVAT NETRA -- Phase 14 Automated Verification Suite
Computer Vision Surface Distress Triage & Crowdsourced Spatial Clustering (SIH Problem Statement ID: 26001)

Verifies:
1. PostGIS Database Schemas & GIST/B-Tree Indexes on field_reports
2. Computer Vision Geotechnical Distress Classifier & DBSCAN Clustering Engine
3. REST Endpoint GET /api/reports/clustered
4. REST Endpoint POST /api/reports/submit with automated triage
5. Frontend Dashboard Controls & Handlers in templates/index.html
6. Milestone Git snapshot checkpoint via backend.mcp_integrations
"""

import os
import sys
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.migrate_phase14 import load_env
from backend.cv_crack_classifier import (
    classify_surface_distress,
    run_dbscan_clustering,
    get_db_connection
)
from backend.mcp_integrations import git_commit_snapshot

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8080")


def test_part1_database_schema():
    print("[PART 1] Verifying PostGIS Database Schemas & Indexes...")
    load_env()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check required columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'field_reports';
        """)
        cols = {row['column_name']: row['data_type'] for row in cur.fetchall()}
        required_cols = [
            'report_id', 'reporter_name', 'phone', 'severity', 'description',
            'image_url', 'latitude', 'longitude', 'cv_crack_type',
            'cv_confidence_pct', 'cv_aperture_mm', 'triage_priority',
            'cluster_id', 'geom'
        ]
        for rc in required_cols:
            assert rc in cols, f"Missing column '{rc}' in field_reports"

        # Check indexes
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'field_reports';
        """)
        indexes = {row['indexname']: row['indexdef'] for row in cur.fetchall()}
        assert any('gist' in idx.lower() and 'geom' in idx.lower() for idx in indexes.values()), \
            "GIST spatial index on geom missing"
        assert any('cluster_id' in idx.lower() for idx in indexes.values()), \
            "B-Tree index on cluster_id missing"

        # Check seeded benchmark count
        cur.execute("SELECT COUNT(*) as cnt FROM field_reports WHERE reporter_name IN ('Constable Tashi Lepcha', 'Pemba Bhutia (Panchayat)', 'Driver Rajesh Gurung');")
        seed_cnt = cur.fetchone()['cnt']
        assert seed_cnt >= 3, f"Expected at least 3 benchmark seeds, found {seed_cnt}"

        print(f"  -> Columns Verified: {len(cols)} columns")
        print(f"  -> Indexes Verified: GIST(geom) and B-Tree(cluster_id) active")
        print(f"  -> Benchmark Ground Truth: {seed_cnt} seeded reports verified")
        print("[PASS] PART 1: PostGIS Database Schemas & Indexes Verified.")
    finally:
        cur.close()
        conn.close()


def test_part2_cv_classification_and_dbscan():
    print("\n[PART 2] Testing CV Distress Classification & DBSCAN Clustering Engine...")
    
    # 1. Test classifier rule sets
    res1 = classify_surface_distress("Transverse asphalt fissure opening across road section", None)
    assert res1['cv_crack_type'] == "TENSION_CRACK", f"Unexpected crack type: {res1}"
    assert res1['triage_priority'] == "IMMEDIATE_CLOSURE", f"Expected IMMEDIATE_CLOSURE: {res1}"
    assert res1['cv_aperture_mm'] >= 35.0, f"Expected aperture >= 35mm: {res1}"

    res2 = classify_surface_distress("Minor gravel slide and debris cone blocking inner mountain lane", None)
    assert res2['cv_crack_type'] == "DEBRIS_CONE", f"Unexpected crack type: {res2}"
    assert res2['triage_priority'] == "INSPECT_24H", f"Expected INSPECT_24H: {res2}"

    # 2. Run DBSCAN clustering
    cluster_res = run_dbscan_clustering(eps_degrees=0.0025, minpoints=1)
    assert cluster_res['success'] is True, f"Clustering failed: {cluster_res.get('error')}"
    assert cluster_res['total_clusters'] > 0, "No clusters generated"

    # 3. Assert Singtam reports are clustered together
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT report_id, reporter_name, cluster_id 
            FROM field_reports 
            WHERE reporter_name IN ('Constable Tashi Lepcha', 'Pemba Bhutia (Panchayat)');
        """)
        rows = cur.fetchall()
        assert len(rows) == 2, f"Expected 2 benchmark Singtam reports, found {len(rows)}"
        c1 = rows[0]['cluster_id']
        c2 = rows[1]['cluster_id']
        assert c1 == c2, f"Singtam reports must be in the same cluster! Got c1={c1}, c2={c2}"
        print(f"  -> Singtam Corroboration: #{rows[0]['report_id']} ({rows[0]['reporter_name']}) and #{rows[1]['report_id']} ({rows[1]['reporter_name']}) clustered into Cluster #{c1}")
        print(f"  -> Total DBSCAN Clusters Identified: {cluster_res['total_clusters']}")
        print("[PASS] PART 2: Computer Vision Classification & DBSCAN Clustering Engine Verified.")
    finally:
        cur.close()
        conn.close()


def test_part3_api_clustered_reports():
    print("\n[PART 3] Testing GET /api/reports/clustered...")
    url = f"{BASE_URL}/api/reports/clustered"
    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data.get("type") == "FeatureCollection", "Expected FeatureCollection GeoJSON"
    features = data.get("features", [])
    assert len(features) > 0, "No cluster features returned"

    # Verify structure of first feature
    f0 = features[0]
    props = f0.get("properties", {})
    assert "cluster_id" in props, "cluster_id missing from feature properties"
    assert "corroborating_reports_count" in props, "corroborating_reports_count missing"
    assert "highest_triage_priority" in props, "highest_triage_priority missing"
    assert "reports" in props, "reports list missing from feature properties"

    rep0 = props["reports"][0]
    assert "cv_crack_type" in rep0, "cv_crack_type missing from report item"
    assert "cv_aperture_mm" in rep0, "cv_aperture_mm missing from report item"
    assert "cv_confidence_pct" in rep0, "cv_confidence_pct missing from report item"

    print(f"  -> HTTP Status Code: {resp.status_code}")
    print(f"  -> Returned Clusters: {len(features)}")
    print(f"  -> Cluster #{props['cluster_id']}: {props['corroborating_reports_count']} report(s), Priority: {props['highest_triage_priority']}, Avg Aperture: {props.get('avg_aperture_mm')}mm")
    print("[PASS] PART 3: GET /api/reports/clustered verified with Point GeoJSON and CV dossiers.")


def test_part4_api_submit_report():
    print("\n[PART 4] Testing POST /api/reports/submit...")
    url = f"{BASE_URL}/api/reports/submit"
    payload = {
        "reporter_name": "Border Roads Engineer Sonam",
        "phone": "9876543210",
        "latitude": 27.1514,
        "longitude": 88.4984,
        "severity": "CRITICAL",
        "description": "Severe transverse tension crack splitting highway pavement open near Singtam junction",
        "image_url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600"
    }
    resp = requests.post(url, json=payload, timeout=60)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data.get("status") == "SUCCESS", f"Unexpected submission status: {data}"
    assert "report_id" in data, "report_id missing from submit response"
    assert "cluster_id" in data, "cluster_id missing from submit response"
    
    cv_info = data.get("cv_classification", {})
    assert cv_info.get("cv_crack_type") == "TENSION_CRACK", f"Unexpected CV crack type: {cv_info}"
    assert cv_info.get("triage_priority") == "IMMEDIATE_CLOSURE", f"Unexpected triage priority: {cv_info}"
    assert cv_info.get("cv_aperture_mm", 0) >= 35.0, f"Expected aperture >= 35mm: {cv_info}"

    print(f"  -> HTTP Status Code: {resp.status_code}")
    print(f"  -> Ingested Report ID: #{data['report_id']} | Assigned Cluster: #{data['cluster_id']}")
    print(f"  -> Automated CV Classification: {cv_info['cv_crack_type']} ({cv_info['cv_confidence_pct']}%) | Aperture: {cv_info['cv_aperture_mm']}mm | Triage: {cv_info['triage_priority']}")
    print("[PASS] PART 4: POST /api/reports/submit verified with automated CV inference & spatial clustering.")


def test_part5_frontend_elements():
    print("\n[PART 5] Verifying Frontend Dashboard Controls & Handlers...")
    url = f"{BASE_URL}/"
    resp = requests.get(url, timeout=30)
    assert resp.status_code == 200, f"Expected 200 for index page, got {resp.status_code}"
    html = resp.text

    assert 'id="toggle-reports-btn"' in html, "Missing #toggle-reports-btn in DOM"
    assert 'toggleReportsLayer()' in html, "Missing toggleReportsLayer() call in DOM"
    assert 'loadClusteredReports()' in html, "Missing loadClusteredReports() handler in DOM"
    assert 'report-pulse-closure' in html, "Missing report-pulse-closure CSS class in DOM"
    assert 'reportsLayerGroup' in html, "Missing reportsLayerGroup in Leaflet setup"

    print("  -> Found #toggle-reports-btn filter control in map toolbar")
    print("  -> Found reportsLayerGroup, loadClusteredReports, and pulse styling in DOM")
    print("[PASS] PART 5: Frontend Dashboard Controls & Handlers Verified.")


def test_part6_browser_screenshots():
    print("\n[PART 6] Verifying Chrome DevTools Screenshots in docs/screenshots/...")
    screenshot_dir = os.path.join(REPO_ROOT, "docs", "screenshots")
    assert os.path.exists(screenshot_dir), f"Directory {screenshot_dir} does not exist"

    expected_files = [
        "01_full_dashboard_console.png",
        "02_gis_map_layers.png",
        "03_bilingual_indigenous_cap_alert.png"
    ]

    min_size_bytes = 50 * 1024  # 50 KB
    for fname in expected_files:
        fpath = os.path.join(screenshot_dir, fname)
        assert os.path.exists(fpath), f"Missing screenshot: {fpath}"
        sz = os.path.getsize(fpath)
        assert sz >= min_size_bytes, f"Screenshot {fname} is too small ({sz} bytes < {min_size_bytes} bytes)"
        print(f"  -> Verified: {fname} (Size: {sz / 1024:.1f} KB, Threshold: >= 50 KB)")

    print("[PASS] PART 6: All 3 High-Resolution Chrome DevTools Screenshots Verified.")


def test_part7_milestone_git_commit():
    print("\n[PART 7] Checkpointing Phase 14 Milestone to Git...")
    commit_msg = "feat: Phase 14 CV crack triage, DBSCAN clustering, and live Chrome DevTools screenshots"
    res = git_commit_snapshot(commit_msg)
    assert res.get("success") is True, f"Git commit snapshot failed: {res.get('error')}"
    if res.get("committed"):
        print(f"  -> Milestone Git Commit Created: {res.get('commit_hash')[:8]} - '{commit_msg}'")
    else:
        print(f"  -> Milestone Status: {res.get('message')}")
    print("[PASS] PART 7: Milestone Git Checkpoint Verified.")


def main():
    print("=" * 80)
    print("PARVAT NETRA -- PHASE 14 AUTOMATED VERIFICATION SUITE")
    print("Computer Vision Surface Distress Triage, DBSCAN & Chrome DevTools Visual QA")
    print("=" * 80)

    test_part1_database_schema()
    test_part2_cv_classification_and_dbscan()
    test_part3_api_clustered_reports()
    test_part4_api_submit_report()
    test_part5_frontend_elements()
    test_part6_browser_screenshots()
    test_part7_milestone_git_commit()

    print("\n" + "=" * 80)
    print(">>> ALL PHASE 14 AUTOMATED TESTS PASSED SUCCESSFULLY! (7/7 PARTS) <<<")
    print("=" * 80)


if __name__ == '__main__':
    main()

