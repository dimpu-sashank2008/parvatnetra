# PAHAD AI — Operations Runbook

**Document**: `PAHAD_OPERATIONS_RUNBOOK.md`  
**Classification**: Operational Reference  
**Audience**: SDMA/DDMA duty officers, platform operators, development engineers  

---

## 1. Daily Operator Checklist

```
☐  1. Start PAHAD AI server (if not running)
☐  2. Verify /api/health returns 200
☐  3. Check /api/pahad/data-status — all streams GREEN
☐  4. Confirm model loaded: /api/pahad/event-model/status → model_loaded: true
☐  5. Run a test inference on NH-10 Km 48 sector
☐  6. Review active alerts: /api/pahad/alerts
☐  7. Check system provenance: /api/system/provenance → system_trust_score > 0.6
☐  8. Verify DRY_RUN status before authorizing any real alerts
```

---

## 2. Starting the Server

### Windows PowerShell

```powershell
# Navigate to project
cd c:\Users\dimpu\Downloads\PARVAT_NETRA_PAHAD_AI_FIRST\silly-fermi

# Demo / development mode (safe — no real SMS/sirens)
$env:PAHAD_DEMO_MODE = "1"
$env:DRY_RUN = "true"
$env:FLASK_ENV = "development"
python app.py

# Production mode (requires valid credentials)
$env:PAHAD_DEMO_MODE = "0"
$env:DRY_RUN = "false"
$env:FLASK_ENV = "production"
$env:IMD_API_KEY = "<imd_api_key>"
$env:NCS_API_KEY = "<ncs_api_key>"
python app.py
```

### Verifying startup
After starting, wait for:
```
[INFO] Edge Network REST routes registered on Flask app.
[INFO] [Notifications] Registered Notification Center blueprint & APIs.
[INFO] [AI TRIAGE] Autonomous evaluation worker started (Interval: 30s).
```
Then access `http://localhost:5000` in a browser.

---

## 3. Health Checks

### System Health
```
GET http://localhost:5000/api/health
GET http://localhost:5000/api/status
```
Expected: HTTP 200, `{"status": "OK"}`

### Data Stream Status (Phase 5)
```
GET http://localhost:5000/api/pahad/data-status
```
Expected response:
```json
{
  "status": "SUCCESS",
  "demo_mode": true,
  "data_streams": {
    "weather": {"available": true, "provenance": "SIMULATED"},
    "seismic": {"available": true, "provenance": "SIMULATED"},
    "iot":     {"available": true, "device_count": 12, "provenance": "SIMULATED"}
  },
  "event_model": {
    "model_loaded": true,
    "model_status": "DATA-GROUNDED RESEARCH PROTOTYPE",
    "training_rows": 16
  }
}
```
⚠️ If `model_loaded: false` — check that `models/pahad_event_model.pkl` exists. Run `python scripts/train_event_model.py` to rebuild.

### System Provenance Audit
```
GET http://localhost:5000/api/system/provenance
```
Key field: `system_trust_score` — should be > 0.6 in demo mode, > 0.8 in production.

---

## 4. Model Status Check

```
GET http://localhost:5000/api/pahad/event-model/status
```
Expected fields:
- `model_status`: `DATA-GROUNDED RESEARCH PROTOTYPE` (N=16 training samples)
- `model_version`: `1.x.x`
- `training_rows`: `16`
- `real_event_rows`: `17`
- `forecast_horizons`: `["6h", "12h", "24h", "48h"]`

```
GET http://localhost:5000/api/pahad/event-model/data-quality
```

---

## 5. Running a Test Inference

### Via HTTP (PowerShell)
```powershell
$body = @{
    sector_id     = "SK-NH10-KM48"
    latitude      = 27.33
    longitude     = 88.61
    horizon_hours = 24
    features = @{
        rainfall_24h          = 185.0
        soil_moisture         = 0.54
        pore_pressure_kpa     = 28.2
        tilt_deg              = 4.1
        ground_displacement_mm = 48.0
        slope_deg             = 42.0
        elevation_m           = 890.0
    }
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:5000/api/pahad/live-inference" -Method POST -Body $body -ContentType "application/json"
```

### Expected Result Fields
| Field | Meaning |
|-------|---------|
| `event_probability` | Calibrated P(event) ∈ [0, 1] |
| `fos_physical` | Infinite Slope FoS |
| `fos_status` | STABLE / MARGINAL / CRITICAL / FAILED |
| `cri` | Composite Risk Index 0–100 |
| `risk_band` | LOW / MODERATE / HIGH / VERY_HIGH / EXTREME |
| `alert_eligible` | True when 2-of-3 corroboration met |
| `data_quality_score` | 0–1 data trustworthiness |
| `demo_mode` | True in PAHAD_DEMO_MODE=1 |

---

## 6. Multi-Horizon Forecast

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/pahad/forecast?sector_id=SK-NH10-KM48&latitude=27.33&longitude=88.61&horizons=6,12,24,48" -Method GET
```

> ⚠️ **Important**: All horizons currently use the same trained model (N=16 training samples). Independent horizon-specific models require a larger dataset. Results are marked with `model_limitation` in the response.

---

## 7. Viewing Active Alerts

```
GET http://localhost:5000/api/pahad/alerts
GET http://localhost:5000/api/pahad/alerts?state=ISSUED
```

Alert lifecycle states:
```
DETECTED → EVALUATING → VERIFIED → ISSUED → ACKNOWLEDGED → ESCALATED → RESOLVED / EXPIRED
```

To authorize an alert (HIGH+):
```
POST http://localhost:5000/api/pahad/alerts/{alert_id}/authorize
Body: {"authority_id": "SDMA-DUTY-OFFICER-01", "signature": "..."}
```

---

## 8. Entering / Exiting Demo Mode

### Enter demo mode
```powershell
$env:PAHAD_DEMO_MODE = "1"
# Restart server
```
In demo mode:
- All provenance badges show `[SIMULATED]`
- Alerts are flagged `is_demo: true`
- No real SMS or siren triggers occur
- Demo alerts can be cleared: `POST /api/pahad/reset-demo-alerts`

### Exit demo mode (production)
```powershell
$env:PAHAD_DEMO_MODE = "0"
$env:DRY_RUN = "false"
# Restart server
```

---

## 9. Log File Locations

| Log | Location |
|-----|---------|
| Flask application logs | Console stdout (configure with Python logging) |
| Alert audit log | `engine/pahad_notification_orchestrator.py` → in-memory + API |
| Weather cache | `data/cache/weather/` |
| Seismic cache | `data/cache/seismic/` |
| Model artifacts | `models/pahad_event_model.pkl`, `models/pahad_event_metrics.json` |

### Setting log level (PowerShell)
```powershell
$env:PAHAD_LOG_LEVEL = "DEBUG"  # or INFO, WARNING, ERROR
python app.py
```

---

## 10. Escalation Procedure

If an alert is generated but not acted upon within 15 minutes:
1. System auto-escalates: `ISSUED → ESCALATED`
2. Escalation triggers secondary notification to backup authority
3. If not resolved within 60 minutes: `ESCALATED → EXPIRED`

Manual escalation:
```
POST http://localhost:5000/api/pahad/alerts/{alert_id}/escalate
Body: {"reason": "Primary duty officer unreachable"}
```

---

## 11. Rebuilding the Event Model

```powershell
# Rebuild with default settings
python scripts/train_event_model.py

# Rebuild with specific parameters
python scripts/train_event_model.py --seed 42 --algorithm gradient_boosting --forecast-window 24

# Rebuild temporal dataset first
python scripts/build_temporal_dataset.py
python scripts/train_event_model.py --dataset data/features/real_train.csv
```

---

## 12. Running Tests

```powershell
# Full regression suite
python -m pytest tests/ -v --tb=short

# Specific test suites
python -m pytest tests/test_failure_behavior.py -v    # Fallback behavior
python -m pytest tests/test_live_inference.py -v      # Phase 5 live inference
python -m pytest tests/test_pahad_end_to_end.py -v    # End-to-end pipeline
python -m pytest tests/test_alert_lifecycle.py -v     # Alert state machine
python -m pytest tests/test_notification_orchestrator.py -v  # Notification pipeline

# Individual failing test
python -m pytest tests/test_live_inference.py::TestLiveInferenceEngine::test_cri_in_bounds -v -s
```
