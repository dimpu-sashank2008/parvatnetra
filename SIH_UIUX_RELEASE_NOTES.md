# PARVAT NETRA — SIH UI/UX Release Notes

## What changed

- Added an SIH 2026 decision-first command snapshot at the top of the dashboard.
- Added a six-stage operational journey: Monitor → Predict → Explain → Warn → Route → Respond.
- Wired the command snapshot to live risk, IoT, Teesta hydrology, field-report and AI SitRep endpoints.
- Updated `/api/ml/latest-risk` to expose persisted physical Factor of Safety, rainfall threshold status and toe-resistance loss fields when available.
- Changed the snapshot to select the highest current risk sector instead of relying on the first database row.
- Added dynamic severity coloring and live-evidence freshness handling.
- Preserved existing GIS, CAP alerting, multilingual, BRO routing, citizen reporting, 3D terrain and telemetry features.

## Validation

- Python syntax compilation passed for `app.py`, `backend/*.py`, `engine/*.py`, and `services/*.py`.
- `tests/test_ui_redesign.py` passed: 6/6.
- `tests/test_map_viewport.py` passed: 6/6.
- Full runtime integration tests were not executed in this environment because the local Python runtime did not have `psycopg2` installed; the project's `requirements.txt` declares `psycopg2-binary==2.9.9`.

## Run

1. Create/activate the Python environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and configure the database/API credentials.
4. Start: `python app.py`.
5. Open `http://127.0.0.1:8080`.
