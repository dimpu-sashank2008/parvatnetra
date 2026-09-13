# PHASE 7D: CHECKPOINT 09 — CALIBRATION AUDIT
Date: 2026-09-10T23:47:00Z

## 1. Calibration Method
Method: Platt Scaling (sigmoid fitting over GradientBoostingClassifier raw scores)
Implementation: sklearn.calibration.CalibratedClassifierCV(base_estimator, method='sigmoid', cv='prefit')
Training data for calibration: validation split (pos=4, neg=8, N=12)

## 2. Calibration Results on Test Partition

Test partition: 8 samples (pos=5, neg=3)

  Positive events (true label=1):
    All 5 samples predicted P = 0.8331 (Platt sigmoid output)
    Raw GBM score (before calibration): ~0.92
    Post-calibration compression: sigmoid squeezes 0.92 -> 0.8331

  Negative controls (true label=0):
    All 3 samples predicted P in [0.4021, 0.4233]
    Probability gap from positives: ~0.41 (large, reliable separation)

Brier Score (calibration quality): 0.0824
  Interpretation: Brier=0 is perfect, Brier=0.25 is random. 0.0824 indicates good calibration.
  CAVEAT: Brier score on N=8 test partition is unreliable as a population-level estimate.

Expected Calibration Error (ECE): NOT CALCULABLE
  Reason: ECE requires binning probability outputs. With only 8 test samples,
  bins cannot be populated. ECE calculation would be misleading.

Reliability Diagram: NOT GENERATED
  Reason: Requires N >= 100 samples for meaningful reliability binning.

## 3. Monotonicity Check

Calibrated model response to increasing rainfall_24h (with all other features held at median):
  Verified by test_event_calibration.py::test_monotonic_response_to_increasing_rainfall
  Result: MONOTONIC INCREASE — P(event) increases as rainfall increases.
  Status: PASS

## 4. Calibration Limitations

  a) Calibration was performed on validation set (N=12). With N=12 calibration samples,
     Platt sigmoid parameters have high uncertainty.
  b) Isotonic regression (the alternative calibration method) requires even more samples
     and was NOT applied to avoid overfitting.
  c) The reported Brier score reflects the test partition only (N=8).
     Population-level calibration quality is unknown.

## 5. Checkpoint 09 Determination
STATUS: CONDITIONAL_PASS
  - Calibration method correctly applied (Platt scaling)
  - Brier score = 0.0824 (good on limited data)
  - Monotonicity verified
  - ECE and reliability diagram deferred pending sufficient data volume
