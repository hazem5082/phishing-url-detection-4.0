# Model Testing Guide

This directory contains comprehensive testing suites for the phishing URL classification model.

## Quick Start

### 1️⃣ **Quick Model Evaluation** (Recommended First)
```bash
python tests/test_model_evaluation.py
```
**What it does:**
- Loads the trained model and dataset
- Computes performance metrics (Accuracy, Precision, Recall, F1, ROC-AUC)
- Tests sample URLs (both legitimate and suspicious)
- Generates detailed CSV report and summary
- **Output:** Reports saved in `tests/reports/`

**Time:** ~30 seconds

---

### 2️⃣ **Interactive URL Testing** (Real-time)
```bash
python tests/test_urls_interactive.py
```
**What it does:**
- Opens an interactive prompt to test URLs one at a time
- Shows prediction confidence and extracted features
- Color-coded output (🟢 Legitimate, 🔴 Phishing)
- Helpful feature explanations

**How to use:**
```
Enter URL: https://www.google.com
→ Shows: Prediction, probability, all features

Enter URL: http://phishing-site.xyz
→ Shows: Red flags, suspicious indicators

Type 'quit' to exit
Type 'examples' to see sample URLs
```

**Time:** Interactive, test as many URLs as you want

---

### 3️⃣ **Comprehensive Unit Tests** (For Development)
```bash
# Install pytest if needed
pip install pytest

# Run all tests with verbose output
pytest tests/test_model_comprehensive.py -v -s

# Run specific test class
pytest tests/test_model_comprehensive.py::TestFeatureExtraction -v

# Run with coverage
pytest tests/test_model_comprehensive.py --cov=src
```

**What it tests:**
- ✓ Feature extraction functions
- ✓ URL normalization
- ✓ Brand detection
- ✓ Suspicious TLD identification
- ✓ Model loading and initialization
- ✓ Model performance metrics
- ✓ Predictions on custom URLs
- ✓ Edge cases (very long URLs, special characters, etc.)

**Test Classes:**
1. `TestFeatureExtraction` - Tests individual feature functions
2. `TestModelLoading` - Verifies model file and structure
3. `TestModelPerformance` - Full performance metrics on dataset
4. `TestPredictionOnCustomURLs` - Tests specific URL predictions
5. `TestEdgeCases` - Edge case handling

**Time:** ~1-2 minutes

---

## Expected Output Examples

### Model Evaluation Output
```
============================================================
  🚀 Phishing URL Classifier - Model Evaluation
============================================================

✓ Model loaded successfully
✓ Data loaded: 15000 samples, 9 features
✓ Dataset class distribution:
    Legitimate: 7500 (50.00%)
    Phishing:   7500 (50.00%)

============================================================
  Model Evaluation
============================================================

🔍 Generating predictions...

📊 Model Performance Metrics:
  Accuracy:    0.9234 (92.34%)
  Precision:   0.9156
  Recall:      0.9301
  F1 Score:    0.9228
  ROC-AUC:     0.9687

📈 Confusion Matrix:
  True Negatives (TN):  6952
  False Positives (FP): 548
  False Negatives (FN): 525
  True Positives (TP):  6975
```

### Sample URL Test Output
```
✓ URL: https://www.google.com
  Expected:  Legitimate
  Predicted: Legitimate
  Confidence: 0.0234 (Phishing)

✗ URL: http://phishing-site.xyz
  Expected:  Phishing
  Predicted: Legitimate
  Confidence: 0.3421 (Phishing)
```

---

## Feature Explanations

The model extracts 9 features from each URL:

1. **url_length** - Log-normalized length (detects unusually long URLs)
2. **dot_count** - Number of dots in URL (high count is suspicious)
3. **has_at_symbol** - Presence of @ symbol (URL spoofing technique)
4. **has_https** - Whether URL uses HTTPS (legitimate sites often use it)
5. **has_sensitive_word** - Contains words like "login", "verify", "confirm"
6. **is_suspicious_tld** - Uses suspicious TLDs (.xyz, .tk, .ml, etc.)
7. **has_hyphens** - Contains hyphens (phishing domains often use them)
8. **is_known_legit** - From known legitimate domains (e.g., Wikipedia, BBC)
9. **is_known_brand** - Contains major brand names (Google, Amazon, etc.)

---

## Interpreting Results

### Confidence Levels
- **< 0.3**: Very likely legitimate
- **0.3 - 0.7**: Uncertain (investigate further)
- **> 0.7**: Very likely phishing

### Key Metrics
- **Accuracy**: Overall correctness (higher is better)
- **Precision**: When model says "phishing", how often is it correct?
- **Recall**: What % of actual phishing URLs does it catch?
- **F1 Score**: Balance between precision and recall
- **ROC-AUC**: Overall classifier performance (0.5=random, 1.0=perfect)

### Confusion Matrix
```
              Predicted
              Legit  Phishing
Actual Legit   TN      FP      (Type I Error - False Alarms)
       Phishing FN      TP      (Type II Error - Missed Phishing)
```

---

## Troubleshooting

### Model not found
```
❌ Model not found at models/phishing_rf_model.joblib
```
**Solution:** Train the model first using `src/models/train_classifier.py`

### Data not found
```
❌ Processed data not found at data/processed/phishing_processed.csv
```
**Solution:** Process raw data first:
```bash
python src/feature_engineering/url_features.py
```

### Import errors
```
ModuleNotFoundError: No module named 'sklearn'
```
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Colorama not installed (interactive tester)
```bash
pip install colorama
```

---

## Running Tests in CI/CD

```bash
# Run all tests and generate report
pytest tests/ -v --cov=src --cov-report=html

# Exit with failure if coverage below threshold
pytest tests/ --cov=src --cov-fail-under=80

# Run specific test file
pytest tests/test_model_comprehensive.py -v
```

---

## Report Location

After running `test_model_evaluation.py`, reports are saved in:
```
tests/reports/
├── model_evaluation_YYYYMMDD_HHMMSS.csv      # Detailed predictions
└── model_evaluation_YYYYMMDD_HHMMSS_summary.txt  # Metrics summary
```

Open the CSV file to see:
- Predictions for each URL
- Phishing probability scores
- All 9 extracted features
- Whether prediction was correct
- Class distribution analysis

---

## Next Steps

1. **Start with:** `python tests/test_model_evaluation.py`
2. **Then try:** `python tests/test_urls_interactive.py` (test custom URLs)
3. **For development:** `pytest tests/test_model_comprehensive.py -v`

---

## Contact & Issues

If tests fail or you have questions:
1. Check troubleshooting section above
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure model and data files exist
4. Check file paths in error messages
