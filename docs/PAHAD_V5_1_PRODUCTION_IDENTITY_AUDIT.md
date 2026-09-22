# PARVAT NETRA / PAHAD AI — PHASE V5.1 PRODUCTION IDENTITY AUDIT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: Cryptographic Architecture & Channel Separation between Production V3 & Research V4.5  

---

## 1. Executive Summary

This report provides the architectural and mathematical proof that Production V3 and Research V4.5 are two distinct, non-overlapping models designed for different operational and research purposes.

---

## 2. Model Distinction Matrix

```
+-----------------------------------+------------------------------------+------------------------------------+
| Dimension                         | Production V3                      | Research V4.5                      |
+-----------------------------------+------------------------------------+------------------------------------+
| Model Identifier                  | PAHAD-BiLSTM-v3-MultiModal-33Feat  | Model_D_1Layer_BiLSTM_Att_V4_5     |
| Weights File                      | models/pahad_lstm_v3_weights.pt    | models/pahad_lstm_v4_5_research_...|
| Verified SHA-256                  | 7cb823888646ca2b074389de3719c9d... | 31e16ce003cdd2c5934df034e622966... |
| Architecture                      | 2-layer BiLSTM + Attention         | 1-layer BiLSTM + Multi-Head Attn   |
| Hidden Dimension                  | 160                                | 128                                |
| Parameter Count                   | 1,293,125 parameters               | 127,239 parameters                 |
| Input Sequence Length             | 72 hours                           | 168 hours (7 full days)            |
| Feature Channels                  | 33 channels (includes CRI legacy)  | 31 channels (CRI strictly excluded)|
| Target Task                       | Multi-horizon CRI alert vector     | Deep infiltration failure detection|
| Temperature Scaling               | T = 1.0552                         | T = 1.0000 (calibrated via BCE)    |
| Operational Status                | ACTIVE_PRODUCTION_FROZEN           | OFFLINE_RESEARCH_BASELINE          |
+-----------------------------------+------------------------------------+------------------------------------+
```

---

## 3. CRI Channel Separation & Leakage Prevention

In Phase V3, the Composite Risk Index (CRI) was provided as an input feature channel (#33) to allow the model to condition on composite risk history. However, in Phase V4.4 and V4.5 research, it was determined that including CRI in sequence inputs introduces a potential circular dependency (target leakage) if CRI is derived from contemporaneous risk scores.

Therefore:
- **Production V3** retains its 33-feature contract strictly frozen under SHA-256 `7cb82388...` to prevent runtime crashes in deployed endpoints.
- **Research V4.5** explicitly removes CRI from its 31 input channels, forcing the neural network to rely solely on pure physics, meteorology, soil moisture, and geodetic signals.
- The two models remain completely isolated.
