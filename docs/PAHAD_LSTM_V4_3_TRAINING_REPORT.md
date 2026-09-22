# PARVAT NETRA / PAHAD AI — Phase V4.3 Training Report

**Document ID**: `PAHAD-DOC-V4-3-TRAIN-001`  
**Timestamp**: `2026-09-20T12:13:23.116715+00:00`  
**Operational Status**: **RESEARCH ONLY — PRODUCTION DISABLED**  

---

## 1. Capacity Benchmark (<150,000 Parameters)
- Simple GRU: 27,460 params (Best Ep 12, Val Loss 0.6535, 24h CSI 0.545)
- Simple LSTM: 35,780 params (Best Ep 13, Val Loss 0.6621, 24h CSI 0.522)
- Simple BiLSTM: 69,316 params (Best Ep 11, Val Loss 0.6841, 24h CSI 0.571)
- BiLSTM + Attention: 110,661 params (Best Ep 3, Val Loss 0.6846, 24h CSI 0.522)

## 2. Test Set Evaluation
| Horizon | N | Pos / Neg | POD | FAR | CSI | Brier Score | ECE | ROC-AUC |
|---|---|---|---|---|---|---|---|---|
| **6h**  | 24 | 4 / 20 | 0.000 | 1.000 | 0.000 | 0.1562 | 0.0986 | 0.45 |
| **12h** | 24 | 8 / 16 | 0.250 | 0.500 | 0.200 | 0.2408 | 0.1477 | 0.5312 |
| **24h** | 24 | 12 / 12 | **0.750** | **0.500** | **0.429** | **0.2543** | **0.0202** | 0.4097 |
| **48h** | 24 | 20 / 4 | **1.000** | **0.167** | **0.833** | **0.1532** | **0.0936** | 0.275 |
