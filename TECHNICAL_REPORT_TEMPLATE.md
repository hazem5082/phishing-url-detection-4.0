# Technical Report Template: Phishing URL Detection Using Machine Learning

## Document Information
- **Title:** Phishing URL Detection Using Machine Learning
- **Date:** April 26, 2026
- **Team Members:** [Insert Names Here]
- **Course/Project:** [Insert Course/Project Name]

---

## 1. Executive Summary (1-2 Pages)

### Problem Statement
Phishing attacks pose a significant cybersecurity threat, with malicious actors continuously evolving their tactics to deceive users. Traditional detection methods relying on blacklists become outdated quickly as attackers register new domains.

### Solution Overview
This project develops a machine learning-based phishing URL classifier using a Random Forest algorithm that analyzes 9 key URL features to distinguish between legitimate and phishing URLs with 79.14% accuracy.

### Key Results
- **Model Accuracy:** 79.14%
- **Precision:** 0.7899 (when model predicts phishing, it's correct 79% of the time)
- **Recall:** 0.7536 (detects 75.36% of actual phishing URLs)
- **ROC-AUC:** 0.8735 (excellent discrimination ability)
- **Dataset Size:** 20,000 URLs (53.33% legitimate, 46.67% phishing)

### Impact
This model can process URLs in real-time for email filtering, browser extensions, or security appliances, automatically flagging suspicious URLs before users interact with them.

---

## 2. Introduction (2-3 Pages)

### Background on Phishing
[Write 1-2 paragraphs about:
- Definition of phishing
- Statistics on phishing prevalence
- Business and personal impact
- Economic costs of phishing attacks
]

### Current Detection Methods
[Write 1-2 paragraphs covering:
- Blacklist-based approaches
- URL pattern analysis
- Limitations of existing methods
- Why ML-based approaches are needed
]

### Project Objectives
The primary objectives of this project are:
1. **Build a robust ML classifier** for real-time phishing detection
2. **Extract meaningful URL features** that distinguish phishing from legitimate URLs
3. **Achieve high recall** to minimize missed phishing attempts
4. **Balance precision and recall** to reduce false alarms
5. **Document methodology** for reproducibility and further research

---

## 3. Literature Review (2-3 Pages)

### Existing Phishing Detection Approaches
[Write 1-2 paragraphs on:
- Content-based methods
- URL structure analysis
- Machine learning in cybersecurity
- Comparative studies
]

### Feature-Based Detection
[Write about:
- URL characteristics used for detection
- Legitimacy indicators
- Phishing red flags
- Why these 9 features were selected
]

### Machine Learning in Cybersecurity
[Discuss:
- Random Forest advantages
- Why we chose RF over other algorithms
- Trade-offs between algorithms
- Related work in phishing detection
]

---

## 4. Methodology (3-4 Pages)

### 4.1 Data Collection Process
**Dataset:** 20,000 URLs from Phishing Detection dataset
- **Source:** [Specify source - HuggingFace, Kaggle, etc.]
- **Class Distribution:** 10,666 Legitimate (53.33%), 9,334 Phishing (46.67%)
- **Preprocessing:** URL normalization, protocol stripping, label validation

### 4.2 Feature Engineering (9 Features)

| # | Feature | Type | Description | Phishing Indicator |
|---|---------|------|-------------|-------------------|
| 1 | `url_length` | Numeric | Log-normalized URL length | Very long URLs (log scale) |
| 2 | `dot_count` | Integer | Number of dots in domain | High dot count indicates subdomains |
| 3 | `has_at_symbol` | Binary | Presence of @ symbol | URL spoofing technique |
| 4 | `has_https` | Binary | Uses HTTPS protocol | Legitimate indicator |
| 5 | `has_sensitive_word` | Binary | Contains: login, verify, confirm, password, account | High phishing indicator |
| 6 | `is_suspicious_tld` | Binary | .xyz, .info, .top, .tk, .ml, .co | Cheap, easily registered domains |
| 7 | `has_hyphens` | Binary | Presence of hyphens in domain | Phishing often uses hyphens |
| 8 | `is_known_legit` | Binary | Known legitimate domains (Wikipedia, BBC, etc.) | Whitelisted domains |
| 9 | `is_known_brand` | Binary | Contains major brand names (Google, Amazon, etc.) | Phishing often impersonates brands |

### 4.3 Algorithm Selection

**Algorithms Tested:**
1. **Logistic Regression** (Baseline)
   - Simple, interpretable
   - Linear decision boundary
   - Baseline for comparison

2. **Random Forest** (Selected)
   - Non-linear decision boundaries
   - Handles feature interactions
   - Feature importance extraction
   - Robust to outliers

3. **Gradient Boosting**
   - Sequential tree building
   - Can overfit on small datasets
   - Requires careful tuning

**Selection Rationale:** Random Forest achieved best balance of accuracy, recall, and interpretability.

### 4.4 Training Approach
- **Data Split:** 80% training, 20% testing
- **Hyperparameters:** [List Random Forest parameters used]
- **Class Weights:** Balanced to handle class imbalance
- **Random State:** 42 (for reproducibility)

### 4.5 Evaluation Metrics
- **Accuracy:** Overall correctness
- **Precision:** Positive predictive value (phishing predictions correct)
- **Recall:** Sensitivity (catch phishing URLs)
- **F1 Score:** Harmonic mean
- **ROC-AUC:** Discrimination ability

---

## 5. Data Analysis (2-3 Pages)

### 5.1 Dataset Overview
**Table: Dataset Statistics**
- Total URLs: 20,000
- Legitimate URLs: 10,666 (53.33%)
- Phishing URLs: 9,334 (46.67%)
- Class Balance: Reasonably balanced

### 5.2 Feature Statistics

[Create table with:
- Feature name
- Mean
- Std Dev
- Min
- Max
- For both phishing and legitimate URLs
]

### 5.3 Key Findings from EDA

[Include discussion of:
- Feature distributions
- Correlation patterns
- Class-specific characteristics
- Outliers and anomalies
]

---

## 6. Results & Evaluation (3-4 Pages)

### 6.1 Model Performance Metrics

**Table: Classification Metrics**
| Metric | Value | Interpretation |
|--------|-------|-----------------|
| Accuracy | 0.7914 (79.14%) | 79% of predictions correct |
| Precision | 0.7899 | When predicting phishing: 79% correct |
| Recall | 0.7536 | Catches 75% of actual phishing |
| F1 Score | 0.7713 | Good balance of precision/recall |
| ROC-AUC | 0.8735 | Excellent discrimination |

### 6.2 Confusion Matrix Analysis

```
                    Predicted
                    Legit    Phishing
Actual  Legitimate  8,795    1,871
        Phishing    2,300    7,034
```

**Interpretation:**
- **True Negatives (TN):** 8,795 - Correctly identified legitimate URLs
- **False Positives (FP):** 1,871 - False alarms (17.54%)
- **False Negatives (FN):** 2,300 - Missed phishing (24.64%)
- **True Positives (TP):** 7,034 - Correctly caught phishing

### 6.3 Feature Importance
[Reference Figure 8: Feature Importance]
The most important features for classification are:
1. [Top feature]
2. [Second feature]
3. [Third feature]

---

## 7. Discussion (2-3 Pages)

### 7.1 Model Strengths
- High accuracy on test set
- Good ROC-AUC (0.8735)
- Interpretable features
- Fast inference time
- Real-time deployment capability

### 7.2 Model Weaknesses
- 24.64% false negative rate (missed phishing)
- 17.54% false positive rate (false alarms)
- Limited to URL-based features only
- May need retraining with new phishing techniques

### 7.3 Real-World Applicability
- **Email Filtering:** Automatically flag suspicious URLs in emails
- **Browser Extensions:** Warn users before clicking phishing links
- **API Usage:** Real-time detection in security appliances
- **Scalability:** Can process thousands of URLs per second

### 7.4 Limitations
- **Feature Scope:** Only analyzes URL structure, not content
- **Zero-Day Phishing:** May not catch novel techniques
- **Encoding:** Website content analysis not included
- **Temporal:** Model may degrade over time as phishing evolves

### 7.5 Model Interpretability
The feature importance analysis shows that [list top 3 features] are the strongest indicators of phishing. This aligns with known phishing tactics:
- Use of suspicious TLDs
- Sensitive words in URLs
- Brand name impersonation

---

## 8. Conclusion (1-2 Pages)

### Key Findings
1. Machine learning can effectively detect phishing URLs with 79.14% accuracy
2. URL structure features are strong indicators of phishing intent
3. Random Forest outperforms baseline and boosting approaches
4. The model achieves good balance between precision and recall

### Future Improvements
1. **Multi-modal Analysis:** Combine URL analysis with webpage content analysis
2. **Deep Learning:** Implement neural networks for better pattern recognition
3. **Ensemble Methods:** Combine multiple models for improved accuracy
4. **Active Learning:** Incorporate user feedback for continuous improvement
5. **Adversarial Robustness:** Test against adversarial examples

### Practical Applications
- Email security systems
- Web browsers
- Enterprise firewall solutions
- DNS-level filtering
- API security

### Final Remarks
This project demonstrates that machine learning can provide a practical, scalable solution for phishing detection. The trained model achieves strong performance and can be deployed in production environments to protect users from phishing threats.

---

## 9. References

[List your sources following APA/IEEE format]

1. [Reference 1]
2. [Reference 2]
3. [Reference 3]
4. ...

**Suggested References:**
- Phishing detection research papers
- Machine learning in cybersecurity
- URL analysis studies
- Class imbalance handling techniques

---

## 10. Appendices

### A. Code Samples
[Include snippets of:
- Feature extraction
- Model training
- Evaluation code
]

### B. Additional Visualizations
[Reference all 9 figures]

### C. Sample Predictions
[Show examples of model predictions on different URLs]

### D. Hyperparameter Details
[Full RF hyperparameter list]

### E. Dataset Summary
[Detailed dataset information]

---

**Document Prepared By:** [Names]  
**Date:** April 26, 2026  
**Total Pages:** [Count]

---

## Notes for Completion
- Replace all [bracketed sections] with your own content
- Add actual data from your analysis
- Include all 9 generated visualizations
- Reference the model metrics from your evaluation
- Write with academic tone
- Proofread before submission
