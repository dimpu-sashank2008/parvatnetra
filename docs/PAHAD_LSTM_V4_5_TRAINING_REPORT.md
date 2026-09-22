# PARVAT NETRA / PAHAD AI — Phase V4.5 Model Training Report

**Document ID**: `PAHAD-DOC-V4-5-TRAIN-001`  
**Timestamp**: `2026-09-20T14:37:22.346486+00:00`  
**Phase**: `Phase V4.5 — Long-Range Multi-Horizon Temporal Modeling`  

---

## 1. Experimental Training Configuration
- **Hardware & Environment**: Python 3.11.0 on Windows
- **PyTorch Version**: 2.14.0+cpu (CUDA Available: False)
- **Architecture**: 1-Layer BiLSTM with Temporal Attention (`PAHADBiLSTMv4_5`)
- **Active Features**: 31 defensible historical channels (Reanalysis, Seismicity, FoS, Static DEM)
- **Sequence Length**: 168 hours (7 continuous days)
- **Trainable Parameters**: **127,239** (strictly bounded <150k params)
- **Optimizer**: AdamW (Initial lr: $3 \times 10^{-4}$, weight decay: $1 \times 10^{-3}$)
- **Learning Rate Scheduler**: Cosine Annealing over 80 epochs
- **Loss Function**: Balanced Binary Cross-Entropy across all 6 prediction horizons

## 2. Convergence Dynamics
- **Best Validation Epoch**: Epoch 9
- **Validation Loss**: 0.5582
- **Training Population**: 48 base sequences $\to$ 168 augmented sequences (Train partition only)
- **Validation Population**: 33 unaugmented sequences
- **Test Population**: 24 unaugmented sequences (Single-pass frozen test)

## 3. Production Isolation
- `models/pahad_lstm_v3_weights.pt` hash verified: `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183` (LOCKED).
