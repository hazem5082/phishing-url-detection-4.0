# 🧪 Model Testing - Quick Reference

## Three Testing Options

### 1. QUICK EVALUATION (Start Here! ⭐)
```bash
python tests/test_model_evaluation.py
```
✓ Full metrics (Accuracy, Precision, Recall, F1, ROC-AUC)
✓ Tests 7 sample URLs
✓ Generates CSV report
⏱️ ~30 seconds

### 2. INTERACTIVE TESTING (Manual Testing)
```bash
python tests/test_urls_interactive.py
```
✓ Test any URL in real-time
✓ See extracted features
✓ Color-coded results
✓ Type 'examples' for sample URLs
⏱️ As long as you want

### 3. UNIT TESTS (Development)
```bash
pytest tests/test_model_comprehensive.py -v -s
```
✓ Tests all functions
✓ Feature extraction validation
✓ Edge case handling
✓ 50+ individual tests
⏱️ 1-2 minutes

---

## Files Created

| File | Purpose |
|------|---------|
| `tests/test_model_evaluation.py` | Quick model evaluation script |
| `tests/test_urls_interactive.py` | Interactive URL tester |
| `tests/test_model_comprehensive.py` | Full pytest test suite |
| `TESTING_GUIDE.md` | Detailed testing documentation |

---

## Expected Results

**Good Model Performance:**
- Accuracy: > 85%
- Precision: > 0.80
- Recall: > 0.80
- ROC-AUC: > 0.85

---

## What Gets Tested

✅ Feature extraction (9 features from each URL)
✅ URL normalization (protocol stripping)
✅ Brand detection (Google, Amazon, Facebook, etc.)
✅ Suspicious TLD detection (.xyz, .tk, .ml, etc.)
✅ Sensitive word detection (login, verify, confirm, etc.)
✅ Model predictions on dataset
✅ Performance metrics
✅ Confusion matrix analysis
✅ Edge cases (long URLs, special chars, international domains)

---

## Example Output

### URL: `https://www.google.com`
```
✓ LEGITIMATE
Phishing Probability: 2.34%
Features:
  Known Brand: ✓
  Has HTTPS: ✓
  Suspicious TLD: ✗
```

### URL: `http://verify-account.xyz/login`
```
🚨 PHISHING
Phishing Probability: 94.12%
Features:
  Suspicious TLD: ✓ (.xyz)
  Has Sensitive Word: ✓ (login)
  Has HTTPS: ✗
```

---

## Recommendations

1. **Start:** Run `test_model_evaluation.py` first
2. **Then:** Try interactive testing with your own URLs
3. **If Developing:** Run full pytest suite before pushing code

---

## Report Outputs

After running evaluation, find reports in:
```
tests/reports/model_evaluation_YYYYMMDD_HHMMSS.csv
tests/reports/model_evaluation_YYYYMMDD_HHMMSS_summary.txt
```

The CSV file contains predictions for every URL in the dataset!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: sklearn` | `pip install -r requirements.txt` |
| Model not found | Train model with `src/models/train_classifier.py` |
| Data not found | Process data with `src/feature_engineering/url_features.py` |
| Colorama not installed | `pip install colorama` |

---

## Need Help?

Check `TESTING_GUIDE.md` for detailed documentation.
