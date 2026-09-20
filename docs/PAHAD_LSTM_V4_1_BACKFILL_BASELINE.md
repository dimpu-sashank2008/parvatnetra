# PARVAT NETRA / PAHAD AI — V4.1 Historical Backfill Baseline Ledger

**Document ID**: `PAHAD-DOC-V4-1-BASELINE-001`  
**Timestamp**: `2026-09-20T16:45:00+05:30`  
**Phase**: `V4.1 — Historical Temporal Data Acquisition & Backfill`  
**Status**: `VERIFIED & LOCKED`

---

## 1. System Invariant Statement

Prior to initiating any historical temporal data acquisition or backfill procedures, the repository state was forensically verified and locked:
- **No neural network retraining** is being performed.
- **`models/pahad_lstm_v3_weights.pt`** is strictly locked and untouched.
- **`models/pahad_lstm_v4_weights.pt`** is strictly locked and untouched.
- **CRI, FoS, and EOC safety rules** remain completely unchanged.
- **Zero synthetic measurements** or linspace trajectory interpolations are permitted in the backfill pipeline.

---

## 2. Git State & Working Tree Audit

- **Branch**: `main` (Ahead of `origin/main` by 6 commits).
- **Latest Commit**: `626771c feat: Phase 15 Chrome DevTools capture, autonomous scheduler, OpenAPI docs, and Docker containerization`.
- **White-Space & Diff Check**: `git diff --check` returned clean exit code 0.

---

## 3. Cryptographic Artifact Integrity Ledger

| Artifact | Purpose | Size (Bytes) | SHA-256 Cryptographic Checksum | Status |
|---|---|---|---|---|
| `models/pahad_lstm_v3_weights.pt` | Active Production BiLSTM v3 Weights | 5,189,381 | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` | **LOCKED / UNTOUCHED** |
| `models/pahad_lstm_v3_config.json` | BiLSTM v3 Hyperparameters & Thresholds | 2,953 | `7e9d76e26fc66a383ec60d2449da25ff4cce451d9346d665d6210912aacf9f88` | **LOCKED / UNTOUCHED** |
| `models/pahad_lstm_v3_metrics.json` | BiLSTM v3 Evaluated Metrics | 4,084 | `e212d6d5c64fe42a69cda887f67580d5380ce47c226ab9c73673824908d472be` | **LOCKED / UNTOUCHED** |
| `models/pahad_lstm_v4_weights.pt` | Research BiLSTM v4 Weights (Shadow Mode) | 5,189,189 | `3dcf66fc804a241067349f907a84d4d6efb0b2b5847903e0edb3d04a65b61462` | **LOCKED / UNTOUCHED** |
| `models/pahad_lstm_v4_metadata.json`| BiLSTM v4 Architecture & Provenance | 13,882 | `59b8a1aa69eb4f77639df693999600a95635c35de5c2bfac6342bea1cb4be797` | **LOCKED / UNTOUCHED** |
| `models/pahad_lstm_v4_metrics.json` | BiLSTM v4 Forensic Checkpoint | 6,671 | `d5c72e473f2537f4bbbf695d80be61c933274efde0e2a9190d6885450b6837d6` | **LOCKED / UNTOUCHED** |

---

## 4. Phase 4.1 Scope & Boundaries

The objective of Phase 4.1 is **DATA ACQUISITION & BACKFILL ONLY**. Under no circumstances will this phase:
1. Retrain or alter model weights.
2. Deploy or switch the active production model.
3. Synthesize hourly data using polynomial equations.
4. Fabricate institutional credentials or API responses.

*Execution proceeds to CP02 (Lock the Event Register).*
