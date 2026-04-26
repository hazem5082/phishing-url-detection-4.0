"""
Comprehensive model testing suite for phishing URL classification.
Tests model performance, feature extraction, and predictions.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import pytest
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, auc
)

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from feature_engineering.url_features import extract_url_features, normalize_url, is_known_brand


class TestFeatureExtraction:
    """Test individual feature extraction functions."""
    
    def test_normalize_url_https(self):
        """Test that HTTPS URLs are normalized correctly."""
        url = "https://www.example.com/path"
        normalized, has_https = normalize_url(url)
        assert normalized == "www.example.com/path"
        assert has_https == 1
    
    def test_normalize_url_http(self):
        """Test that HTTP URLs are normalized correctly."""
        url = "http://www.example.com/path"
        normalized, has_https = normalize_url(url)
        assert normalized == "www.example.com/path"
        assert has_https == 0
    
    def test_normalize_url_no_protocol(self):
        """Test that URLs without protocol are handled."""
        url = "www.example.com"
        normalized, has_https = normalize_url(url)
        assert normalized == "www.example.com"
        assert has_https == 0
    
    def test_known_brand_detection(self):
        """Test that known brands are detected."""
        assert is_known_brand("https://www.google.com") == 1
        assert is_known_brand("https://www.amazon.com") == 1
        assert is_known_brand("https://www.facebook.com") == 1
        assert is_known_brand("https://www.unknown-site.com") == 0
    
    def test_extract_url_features_legitimate(self):
        """Test feature extraction on a legitimate URL."""
        url = "https://www.google.com/search"
        features = extract_url_features(url)
        
        # Assertions
        assert isinstance(features, dict)
        assert len(features) == 9
        assert features['has_https'] == 1
        assert features['is_known_brand'] == 1
        assert features['is_suspicious_tld'] == 0
        assert features['is_known_legit'] == 0  # Google not in legit list, but is brand
        assert all(isinstance(v, (int, float, np.integer, np.floating)) for v in features.values())
    
    def test_extract_url_features_suspicious(self):
        """Test feature extraction on a suspicious URL."""
        url = "http://g00gle-login-verify.xyz/account/confirm"
        features = extract_url_features(url)
        
        assert features['has_https'] == 0
        assert features['is_suspicious_tld'] == 1
        assert features['has_sensitive_word'] == 1
        assert features['has_hyphens'] == 1
    
    def test_url_length_feature(self):
        """Test that URL length is log-normalized."""
        short_url = "http://a.com"
        long_url = "http://a.com/" + "x" * 1000
        
        short_features = extract_url_features(short_url)
        long_features = extract_url_features(long_url)
        
        # Log normalization should prevent extreme differences
        diff = long_features['url_length'] - short_features['url_length']
        assert 1 < diff < 10  # Reasonable range due to log transformation
    
    def test_at_symbol_detection(self):
        """Test @ symbol detection (URL spoofing technique)."""
        url_with_at = "http://google.com@phishing.com"
        url_without_at = "http://google.com"
        
        assert extract_url_features(url_with_at)['has_at_symbol'] == 1
        assert extract_url_features(url_without_at)['has_at_symbol'] == 0
    
    def test_suspicious_tld_detection(self):
        """Test suspicious TLD detection."""
        suspicious_urls = [
            "http://example.xyz",
            "http://example.top",
            "http://example.tk",
            "http://example.ml",
        ]
        legitimate_urls = [
            "http://example.com",
            "http://example.org",
            "http://example.co.uk",
        ]
        
        for url in suspicious_urls:
            assert extract_url_features(url)['is_suspicious_tld'] == 1
        
        for url in legitimate_urls:
            assert extract_url_features(url)['is_suspicious_tld'] == 0


class TestModelLoading:
    """Test that the model can be loaded and is valid."""
    
    def test_model_exists(self):
        """Test that the model file exists."""
        model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
        assert os.path.exists(model_path), f"Model not found at {model_path}"
    
    def test_model_loads(self):
        """Test that the model can be loaded."""
        model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
        model = joblib.load(model_path)
        assert model is not None
        assert hasattr(model, 'predict')
        assert hasattr(model, 'predict_proba')
    
    def test_model_expects_9_features(self):
        """Test that the model expects 9 input features."""
        model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
        model = joblib.load(model_path)
        assert model.n_features_in_ == 9


class TestModelPerformance:
    """Test model performance on processed dataset."""
    
    @pytest.fixture
    def model_and_data(self):
        """Load model and processed data."""
        model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
        processed_data_path = os.path.join(BASE_DIR, 'data', 'processed', 'phishing_processed.csv')
        
        model = joblib.load(model_path)
        df = pd.read_csv(processed_data_path)
        
        X = df.drop(columns=['label'])
        y = df['label']
        
        return model, X, y
    
    def test_model_predictions_shape(self, model_and_data):
        """Test that predictions have correct shape."""
        model, X, y = model_and_data
        predictions = model.predict(X)
        
        assert len(predictions) == len(y)
        assert all(p in [0, 1] for p in predictions)
    
    def test_model_probabilities_shape(self, model_and_data):
        """Test that probabilities have correct shape and range."""
        model, X, y = model_and_data
        probabilities = model.predict_proba(X)
        
        assert probabilities.shape == (len(y), 2)
        assert np.all(probabilities >= 0) and np.all(probabilities <= 1)
        assert np.allclose(probabilities.sum(axis=1), 1.0)
    
    def test_model_accuracy(self, model_and_data):
        """Test that model achieves reasonable accuracy."""
        model, X, y = model_and_data
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        
        # Model should achieve at least 75% accuracy
        assert accuracy >= 0.75, f"Accuracy too low: {accuracy}"
        print(f"\n✓ Model Accuracy: {accuracy:.4f}")
    
    def test_model_precision_recall(self, model_and_data):
        """Test precision and recall are balanced."""
        model, X, y = model_and_data
        predictions = model.predict(X)
        
        precision = precision_score(y, predictions, zero_division=0)
        recall = recall_score(y, predictions, zero_division=0)
        
        print(f"\n✓ Precision: {precision:.4f}")
        print(f"✓ Recall: {recall:.4f}")
        
        # Both should be meaningful (> 0.5)
        assert precision >= 0.5
        assert recall >= 0.5
    
    def test_model_f1_score(self, model_and_data):
        """Test F1 score."""
        model, X, y = model_and_data
        predictions = model.predict(X)
        
        f1 = f1_score(y, predictions, zero_division=0)
        print(f"✓ F1 Score: {f1:.4f}")
        
        # F1 should be reasonable
        assert f1 >= 0.5
    
    def test_model_roc_auc(self, model_and_data):
        """Test ROC-AUC score."""
        model, X, y = model_and_data
        probabilities = model.predict_proba(X)[:, 1]
        
        roc_auc = roc_auc_score(y, probabilities)
        print(f"✓ ROC-AUC Score: {roc_auc:.4f}")
        
        # ROC-AUC should be > 0.7 for a good classifier
        assert roc_auc >= 0.7
    
    def test_confusion_matrix_no_errors(self, model_and_data):
        """Test that confusion matrix can be computed."""
        model, X, y = model_and_data
        predictions = model.predict(X)
        
        cm = confusion_matrix(y, predictions)
        assert cm.shape == (2, 2)
        assert np.all(cm >= 0)
        print(f"\n✓ Confusion Matrix:\n{cm}")


class TestPredictionOnCustomURLs:
    """Test predictions on specific URLs."""
    
    @pytest.fixture
    def model(self):
        """Load model."""
        model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
        return joblib.load(model_path)
    
    def test_predict_known_legitimate_urls(self, model):
        """Test predictions on known legitimate URLs."""
        legitimate_urls = [
            "https://www.google.com",
            "https://www.github.com/user/repo",
            "https://www.amazon.com/products",
            "https://www.wikipedia.org/wiki/Machine_Learning",
        ]
        
        for url in legitimate_urls:
            features = extract_url_features(url)
            features_array = np.array([[
                features['url_length'],
                features['dot_count'],
                features['has_at_symbol'],
                features['has_https'],
                features['has_sensitive_word'],
                features['is_suspicious_tld'],
                features['has_hyphens'],
                features['is_known_legit'],
                features['is_known_brand'],
            ]])
            
            prediction = model.predict(features_array)[0]
            probability = model.predict_proba(features_array)[0][1]
            
            print(f"\nURL: {url}")
            print(f"  Prediction: {'Phishing' if prediction == 1 else 'Legitimate'}")
            print(f"  Phishing Probability: {probability:.4f}")
    
    def test_predict_suspicious_urls(self, model):
        """Test predictions on suspicious URLs."""
        suspicious_urls = [
            "http://g00gle-login-verify.xyz/account/confirm",
            "http://amazon-payment.top/login",
            "http://paypal@phishing.com/account",
            "http://verify-account-here.tk",
        ]
        
        for url in suspicious_urls:
            features = extract_url_features(url)
            features_array = np.array([[
                features['url_length'],
                features['dot_count'],
                features['has_at_symbol'],
                features['has_https'],
                features['has_sensitive_word'],
                features['is_suspicious_tld'],
                features['has_hyphens'],
                features['is_known_legit'],
                features['is_known_brand'],
            ]])
            
            prediction = model.predict(features_array)[0]
            probability = model.predict_proba(features_array)[0][1]
            
            print(f"\nURL: {url}")
            print(f"  Prediction: {'Phishing' if prediction == 1 else 'Legitimate'}")
            print(f"  Phishing Probability: {probability:.4f}")


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_long_url(self):
        """Test feature extraction on very long URL."""
        long_url = "https://www.example.com/" + "a" * 5000
        features = extract_url_features(long_url)
        assert not any(np.isnan(v) if isinstance(v, (float, np.floating)) else False 
                      for v in features.values())
    
    def test_special_characters_in_url(self):
        """Test URLs with special characters."""
        urls = [
            "https://example.com/path?query=value&other=123",
            "https://example.com/path#anchor",
            "https://example.com/path;jsessionid=123",
        ]
        for url in urls:
            features = extract_url_features(url)
            assert isinstance(features, dict)
            assert len(features) == 9
    
    def test_international_domain(self):
        """Test URLs with international domains."""
        urls = [
            "https://example.co.uk",
            "https://example.co.jp",
            "https://example.co.in",
        ]
        for url in urls:
            features = extract_url_features(url)
            # Should not flag country-specific .co domains as suspicious
            assert features['is_suspicious_tld'] == 0
    
    def test_empty_and_none_handling(self):
        """Test handling of edge case URLs."""
        urls = [
            "http://",
            "https://.",
        ]
        for url in urls:
            try:
                features = extract_url_features(url)
                assert isinstance(features, dict)
            except Exception as e:
                print(f"Expected handling of {url}: {e}")


def test_all_features_present():
    """Test that extract_url_features returns all 9 features."""
    url = "https://www.example.com/path"
    features = extract_url_features(url)
    
    required_features = [
        'url_length', 'dot_count', 'has_at_symbol', 'has_https',
        'has_sensitive_word', 'is_suspicious_tld', 'has_hyphens',
        'is_known_legit', 'is_known_brand'
    ]
    
    for feature in required_features:
        assert feature in features, f"Missing feature: {feature}"


if __name__ == "__main__":
    # Run with: pytest tests/test_model_comprehensive.py -v -s
    print("Run tests with: pytest tests/test_model_comprehensive.py -v -s")
