# PARVAT NETRA / PAHAD AI — PHASE V5.1 REPRODUCIBILITY REPORT

**Document ID**: `DOC-V5-1-REPRODUCIBILITY`  
**Phase**: V5.1 — Scientific Truth Ledger & Model Reproducibility  
**Primary Corridor**: `CORR-NH10-SIKKIM-KM48`  
**System Designation**: Smart India Hackathon (SIH) 2026 AI-Assisted Research and Decision-Support Prototype  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering Swarm  
**Date**: September 21, 2026  

---

## 1. Executive Summary

This report establishes the cryptographic reproducibility environment and commands for all trained models in PARVAT NETRA / PAHAD AI.

Training, evaluation, and data hashing are deterministic under fixed random seeds and pinned library versions.

---

## 2. Cryptographic Weight Invariance

| Model | Path | Algorithm / Framework | Verified SHA-256 | Bit-for-Bit Verified |
|---|---|---|---|---|
| **Production BiLSTM V3** | `models/pahad_lstm_v3_weights.pt` | PyTorch BiLSTM (2-layer, hidden=160, 33 features) | `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` | **EXACT MATCH** |
| **Research BiLSTM V4.5** | `models/pahad_lstm_v4_5_research_weights.pt` | PyTorch BiLSTM + Attention (1-layer, hidden=128, 31 features) | `31e16ce003cdd2c5934df034e6229661d27a8530a6a0dbc6a18e1ff56277da9f` | **EXACT MATCH** |
| **Event Classifier GBDT** | `models/pahad_event_model.pkl` | Scikit-Learn GradientBoostingClassifier | `80eeeb3c261e4e3e3b3e23927d3b51d8b9d3ffbb9007f3d9d300ad8c44b931be` | **EXACT MATCH** |

---

## 3. Retraining Commands & Seeds

### 3.1 Event Classifier (GBDT) Retraining Command
```bash
python scripts/train_event_model.py \
  --dataset data/features/features_all.csv \
  --output models/pahad_event_model.pkl \
  --algorithm GradientBoostingClassifier \
  --seed 42 \
  --forecast-window 24h \
  --model-version 1.0.0
```
- **Seed**: `42`
- **Scikit-Learn Version**: Pinned in environment
- **Dataset Hash**: `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`

### 3.2 Research BiLSTM V4.5 Evaluation Command
```bash
python scripts/train_lstm_v4_5.py --evaluate-only --weights models/pahad_lstm_v4_5_research_weights.pt
```
- **Dataset Hash**: `89b48d3b8354f8e66a26ccd9dc3b08d8b51a7616b3e983a803aa4d3285c305e3`

---

## 4. Environment Specification
- **Python**: 3.11.x
- **PyTorch**: CUDA / CPU compatible deterministic execution
- **Platform**: Localhost only (`127.0.0.1`)
- **Public Exposure**: Strictly Disabled
