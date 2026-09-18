"""Synthetic live endpoint verification script."""
import urllib.request
import json

def run_checks():
    urls = [
        'http://127.0.0.1:8080/demo',
        'http://127.0.0.1:8080/terrain-3d',
        'http://127.0.0.1:8080/edge-network',
        'http://127.0.0.1:8080/api/cv/cameras',
        'http://127.0.0.1:8080/api/cv/analyze-aperture?camera_id=CAM-NH10-KM48',
        'http://127.0.0.1:8080/api/voice/briefing?sector_id=SK-NH10-KM48'
    ]
    for u in urls:
        with urllib.request.urlopen(u) as r:
            print(f"[PASS] GET {u} -> HTTP {r.status}")

    body = json.dumps({
        'commander_pin': 'NDMA-2026',
        'sector_id': 'SK-NH10-KM48',
        'corroborated_signals': 3,
        'target_subscribers': 5000
    }).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8080/api/alerts/dispatch-sachet',
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode('utf-8'))
        d_id = res.get('dispatch_id')
        deliv = res.get('cdac_cell_broadcast', {}).get('delivered_acknowledgments')
        print(f"[PASS] POST /api/alerts/dispatch-sachet -> HTTP {r.status} (ID: {d_id}, Delivered: {deliv})")

if __name__ == '__main__':
    run_checks()
