# -*- coding: utf-8 -*-
"""
scripts/phase11j_perf_smoke.py
Measures endpoint response latency under test_client.
"""
import time
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = app.test_client()

endpoints = [
    ("GET", "/health", None),
    ("GET", "/api/pahad/data-status", None),
    ("GET", "/api/pahad/highest-risk-corridor", None),
    ("POST", "/api/pahad/live-inference", {"sector_id": "SK-NH10-KM48", "latitude": 27.33, "longitude": 88.61, "horizon_hours": 24}),
    ("GET", "/api/eoc/incidents", None),
    ("GET", "/api/eoc/command-brief", None),
]

results = []

for method, path, payload in endpoints:
    times = []
    # 3 iterations
    for _ in range(3):
        t0 = time.perf_counter()
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json=payload)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0) # in ms
    
    avg_ms = sum(times) / len(times)
    min_ms = min(times)
    max_ms = max(times)
    status_code = res.status_code
    
    results.append({
        "endpoint": path,
        "method": method,
        "status_code": status_code,
        "avg_ms": round(avg_ms, 2),
        "min_ms": round(min_ms, 2),
        "max_ms": round(max_ms, 2)
    })
    print(f"[{method}] {path} -> {status_code} | Avg: {avg_ms:.2f}ms (Min: {min_ms:.2f}ms, Max: {max_ms:.2f}ms)")

os.makedirs("reports", exist_ok=True)
with open("reports/PHASE11J_PERFORMANCE_SMOKE.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Performance smoke report saved to reports/PHASE11J_PERFORMANCE_SMOKE.json")
