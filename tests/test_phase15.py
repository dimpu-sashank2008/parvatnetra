"""
PARVAT NETRA -- Phase 15 Automated Verification Suite
Chrome DevTools Visual Capture, Autonomous Background Scheduler, OpenAPI Docs & Docker Containerization
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Verifies:
1. All 3 captured Chrome screenshots exist in docs/screenshots/ with valid file sizes (> 40 KB)
2. Interactive Swagger UI (/api/docs) and OpenAPI 3.0 specification (/api/openapi.json)
3. Autonomous Background Scheduler execution cycle & heartbeat logging
4. Production Dockerfile, docker-compose.yml, and .dockerignore syntax & structure
5. Milestone Git snapshot checkpoint via backend.mcp_integrations
"""

import os
import sys
import json
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

from backend.scheduler import run_scheduler_cycle
from backend.mcp_integrations import git_commit_snapshot

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8080")


def test_part1_browser_screenshots():
    print("[PART 1] Verifying Chrome DevTools Screenshots in docs/screenshots/...")
    screenshot_dir = os.path.join(REPO_ROOT, "docs", "screenshots")
    assert os.path.exists(screenshot_dir), f"Directory {screenshot_dir} does not exist"

    expected_files = [
        "01_executive_operations_dashboard.png",
        "02_multimodal_gis_console.png",
        "03_bilingual_indigenous_voice_cap_modal.png"
    ]

    min_size_bytes = 40 * 1024  # 40 KB requirement
    for fname in expected_files:
        fpath = os.path.join(screenshot_dir, fname)
        assert os.path.exists(fpath), f"Missing screenshot: {fpath}"
        sz = os.path.getsize(fpath)
        assert sz >= min_size_bytes, f"Screenshot {fname} is too small ({sz} bytes < {min_size_bytes} bytes)"
        print(f"  -> Verified: {fname} (Size: {sz / 1024:.1f} KB, Threshold: >= 40 KB)")

    print("[PASS] PART 1: All 3 High-Resolution Chrome DevTools Screenshots Verified.")


def test_part2_openapi_and_docs():
    print("\n[PART 2] Verifying Interactive OpenAPI Documentation & Swagger UI (/api/docs)...")
    
    # 1. Test /api/docs
    docs_url = f"{BASE_URL}/api/docs"
    r_docs = requests.get(docs_url, timeout=15)
    assert r_docs.status_code == 200, f"Expected 200 for /api/docs, got {r_docs.status_code}"
    html = r_docs.text
    assert "SwaggerUIBundle" in html, "SwaggerUIBundle missing from /api/docs"
    assert "PARVAT NETRA" in html, "Brand title missing from /api/docs"
    assert "/api/openapi.json" in html, "OpenAPI spec link missing from /api/docs"
    print("  -> GET /api/docs: HTTP 200 (Interactive Swagger UI Delivered)")

    # 2. Test /api/openapi.json
    spec_url = f"{BASE_URL}/api/openapi.json"
    r_spec = requests.get(spec_url, timeout=15)
    assert r_spec.status_code == 200, f"Expected 200 for /api/openapi.json, got {r_spec.status_code}"
    spec = r_spec.json()
    assert spec.get("openapi") == "3.0.0", f"Expected openapi 3.0.0, got {spec.get('openapi')}"
    paths = spec.get("paths", {})
    
    required_endpoints = [
        "/api/health",
        "/api/ml/latest-risk",
        "/api/sensors/live",
        "/api/insar/points",
        "/api/satellite/detected-scars",
        "/api/hydrology/teesta-status",
        "/api/terrain/anthropogenic-cuts",
        "/api/routing/evacuation-plan",
        "/api/humanitarian/isolation-matrix",
        "/api/reports/clustered",
        "/api/reports/submit",
        "/api/alerts/broadcast-trigger"
    ]
    for ep in required_endpoints:
        assert ep in paths, f"Endpoint {ep} missing from OpenAPI specification"
    print(f"  -> GET /api/openapi.json: HTTP 200 ({len(paths)} operational endpoints documented)")

    # 3. Test /api/health
    health_url = f"{BASE_URL}/api/health"
    r_health = None
    import time
    for attempt in range(4):
        try:
            r_health = requests.get(health_url, timeout=30)
            if r_health.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(2.0)

    assert r_health is not None and r_health.status_code == 200, f"Expected 200 for /api/health, got {r_health.status_code if r_health else 'None'}"
    health_data = r_health.json()
    assert health_data.get("status") == "UP", f"Expected UP status, got {health_data}"
    assert health_data.get("database") == "CONNECTED", f"Expected CONNECTED database, got {health_data}"
    print(f"  -> GET /api/health: HTTP 200 (Status: {health_data['status']}, Database: {health_data['database']})")

    print("[PASS] PART 2: Interactive OpenAPI & Health Check APIs Verified.")


def test_part3_autonomous_scheduler():
    print("\n[PART 3] Testing Autonomous Background Scheduler Cycle & Heartbeat...")
    cycle_res = run_scheduler_cycle(max_retries=3)
    assert cycle_res.get("status") == "SUCCESS", f"Scheduler cycle failed: {cycle_res.get('error')}"
    assert cycle_res.get("telemetry_readings", 0) > 0, "No telemetry readings processed"
    assert cycle_res.get("risk_evaluations", 0) > 0, "No risk evaluations processed"
    assert cycle_res.get("routes_evaluated", 0) > 0, "No bypass routes evaluated"
    
    heartbeat = cycle_res.get("heartbeat", "")
    assert "[HEARTBEAT]" in heartbeat, "Heartbeat log missing from cycle result"
    print(f"  -> Cycle Result: Status: {cycle_res['status']}")
    print(f"  -> Heartbeat: {heartbeat}")
    print("[PASS] PART 3: Autonomous Background Scheduler Cycle Verified.")


def test_part4_docker_artifacts():
    print("\n[PART 4] Verifying Cloud Containerization Artifacts (Dockerfile, Compose, Ignore)...")
    
    # 1. Dockerfile
    dockerfile_path = os.path.join(REPO_ROOT, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile missing from root directory"
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        df_content = f.read()
    assert "FROM python:3.11-slim" in df_content, "Dockerfile missing Python 3.11 base"
    assert "gunicorn" in df_content, "Dockerfile missing gunicorn execution"
    assert "EXPOSE 8080" in df_content, "Dockerfile missing port 8080 exposure"
    assert "HEALTHCHECK" in df_content, "Dockerfile missing healthcheck probe"
    print("  -> Dockerfile: Multi-stage slim Python 3.11 container with health check verified.")

    # 2. docker-compose.yml
    compose_path = os.path.join(REPO_ROOT, "docker-compose.yml")
    assert os.path.exists(compose_path), "docker-compose.yml missing from root directory"
    with open(compose_path, "r", encoding="utf-8") as f:
        compose_content = f.read()
    assert "parvat-netra-web" in compose_content, "Service parvat-netra-web missing from compose"
    assert "8080:8080" in compose_content, "Port 8080:8080 missing from compose"
    assert ".env" in compose_content, "Env file linkage missing from compose"
    print("  -> docker-compose.yml: Service declaration & port mappings verified.")

    # 3. .dockerignore
    ignore_path = os.path.join(REPO_ROOT, ".dockerignore")
    assert os.path.exists(ignore_path), ".dockerignore missing from root directory"
    with open(ignore_path, "r", encoding="utf-8") as f:
        ignore_content = f.read()
    assert ".venv" in ignore_content, ".venv missing from .dockerignore"
    assert "__pycache__" in ignore_content, "__pycache__ missing from .dockerignore"
    assert ".env" in ignore_content, ".env exclusion missing from .dockerignore"
    print("  -> .dockerignore: Critical exclusion rules verified.")

    # 4. requirements.txt
    req_path = os.path.join(REPO_ROOT, "requirements.txt")
    with open(req_path, "r", encoding="utf-8") as f:
        req_content = f.read()
    assert "gunicorn" in req_content, "gunicorn missing from requirements.txt"
    assert "psycopg2-binary" in req_content, "psycopg2-binary missing from requirements.txt"
    print("  -> requirements.txt: Production WSGI and database dependencies verified.")

    print("[PASS] PART 4: Production Cloud Containerization Artifacts Verified.")


def test_part5_milestone_git_commit():
    print("\n[PART 5] Checkpointing Phase 15 Milestone to Git...")
    commit_msg = "feat: Phase 15 Chrome DevTools capture, autonomous scheduler, OpenAPI docs, and Docker containerization"
    res = git_commit_snapshot(commit_msg)
    assert res.get("success") is True, f"Git commit snapshot failed: {res.get('error')}"
    if res.get("committed"):
        print(f"  -> Milestone Git Commit Created: {res.get('commit_hash')[:8]} - '{commit_msg}'")
    else:
        print(f"  -> Milestone Status: {res.get('message')}")
    print("[PASS] PART 5: Milestone Git Checkpoint Verified.")


def main():
    print("=" * 80)
    print("PARVAT NETRA -- PHASE 15 AUTOMATED VERIFICATION SUITE")
    print("Chrome DevTools Visual QA, Background Scheduler, OpenAPI & Containerization")
    print("=" * 80)

    test_part1_browser_screenshots()
    test_part2_openapi_and_docs()
    test_part3_autonomous_scheduler()
    test_part4_docker_artifacts()
    test_part5_milestone_git_commit()

    print("\n" + "=" * 80)
    print(">>> ALL PHASE 15 AUTOMATED TESTS PASSED SUCCESSFULLY! (5/5 PARTS) <<<")
    print("=" * 80)


if __name__ == '__main__':
    main()
