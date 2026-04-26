"""
Standalone Model Evaluation Script
Quickly test model performance, generate reports, and save results.
Run directly: python test_model_evaluation.py
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report, roc_curve, auc
)

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from feature_engineering.url_features import extract_url_features


def load_model_and_data():
    """Load the trained model and processed dataset."""
    model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
    processed_data_path = os.path.join(BASE_DIR, 'data', 'processed', 'phishing_processed.csv')
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        return None, None, None, None
    
    if not os.path.exists(processed_data_path):
        print(f"❌ Processed data not found at {processed_data_path}")
        return None, None, None, None
    
    print(f"📂 Loading model from: {model_path}")
    model = joblib.load(model_path)
    
    print(f"📂 Loading data from: {processed_data_path}")
    df = pd.read_csv(processed_data_path)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    return model, X, y, df


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def evaluate_model(model, X, y):
    """Compute comprehensive model metrics."""
    print("🔍 Generating predictions...")
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]
    
    # Compute metrics
    accuracy = accuracy_score(y, predictions)
    precision = precision_score(y, predictions, zero_division=0)
    recall = recall_score(y, predictions, zero_division=0)
    f1 = f1_score(y, predictions, zero_division=0)
    roc_auc = roc_auc_score(y, probabilities)
    cm = confusion_matrix(y, predictions)
    
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'predictions': predictions,
        'probabilities': probabilities,
    }
    
    return metrics


def print_metrics(metrics):
    """Print formatted metrics."""
    print("📊 Model Performance Metrics:")
    print(f"  Accuracy:    {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"  Precision:   {metrics['precision']:.4f}")
    print(f"  Recall:      {metrics['recall']:.4f}")
    print(f"  F1 Score:    {metrics['f1']:.4f}")
    print(f"  ROC-AUC:     {metrics['roc_auc']:.4f}")
    
    print("\n📈 Confusion Matrix:")
    cm = metrics['confusion_matrix']
    print(f"  True Negatives (TN):  {cm[0, 0]}")
    print(f"  False Positives (FP): {cm[0, 1]}")
    print(f"  False Negatives (FN): {cm[1, 0]}")
    print(f"  True Positives (TP):  {cm[1, 1]}")
    
    # Calculate rates
    tpr = cm[1, 1] / (cm[1, 1] + cm[1, 0]) if (cm[1, 1] + cm[1, 0]) > 0 else 0
    fpr = cm[0, 1] / (cm[0, 1] + cm[0, 0]) if (cm[0, 1] + cm[0, 0]) > 0 else 0
    
    print(f"\n  True Positive Rate (TPR/Sensitivity): {tpr:.4f}")
    print(f"  False Positive Rate (FPR):            {fpr:.4f}")


def test_sample_urls(model):
    """Test predictions on sample URLs."""
    print("\n🧪 Testing Sample URLs:")
    
    test_cases = [
        ("https://www.google.com", "Legitimate"),
        ("https://www.github.com/user/repo", "Legitimate"),
        ("https://www.amazon.com/products", "Legitimate"),
        ("http://g00gle-login-verify.xyz/account/confirm", "Phishing"),
        ("http://amazon-payment-verify.top/login", "Phishing"),
        ("http://paypal@phishing.com/account", "Phishing"),
        ("http://verify-account-now.tk", "Phishing"),
    ]
    
    for url, expected in test_cases:
        features = extract_url_features(url)
        
        # Create feature array in correct order
        feature_array = np.array([[
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
        
        prediction = model.predict(feature_array)[0]
        probability = model.predict_proba(feature_array)[0][1]
        
        predicted_label = "Phishing" if prediction == 1 else "Legitimate"
        match = "✓" if predicted_label == expected else "✗"
        
        print(f"\n  {match} URL: {url}")
        print(f"    Expected:  {expected}")
        print(f"    Predicted: {predicted_label}")
        print(f"    Confidence: {probability:.4f} (Phishing)")


def analyze_predictions(y, predictions, probabilities):
    """Analyze prediction distribution."""
    print("\n\n📋 Prediction Analysis:")
    
    phishing_count = np.sum(predictions == 1)
    legit_count = np.sum(predictions == 0)
    
    print(f"  URLs classified as Phishing: {phishing_count} ({phishing_count/len(predictions)*100:.2f}%)")
    print(f"  URLs classified as Legitimate: {legit_count} ({legit_count/len(predictions)*100:.2f}%)")
    
    print(f"\n  Average Phishing Probability: {np.mean(probabilities):.4f}")
    print(f"  Min Probability: {np.min(probabilities):.4f}")
    print(f"  Max Probability: {np.max(probabilities):.4f}")
    print(f"  Std Dev: {np.std(probabilities):.4f}")


def save_detailed_report(model, X, y, predictions, probabilities, df_original):
    """Save detailed report to file."""
    report_dir = os.path.join(BASE_DIR, 'tests', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"model_evaluation_{timestamp}.csv")
    
    # Create report dataframe
    report_df = pd.DataFrame({
        'prediction': predictions,
        'phishing_probability': probabilities,
    })
    
    # Add features
    for col in X.columns:
        report_df[col] = X[col].values
    
    # Add true labels
    report_df['true_label'] = y.values
    
    # Add match column
    report_df['correct'] = (report_df['prediction'] == report_df['true_label']).astype(int)
    
    report_df.to_csv(report_path, index=False)
    print(f"\n📄 Detailed report saved: {report_path}")
    
    return report_path


def generate_metrics_summary(metrics):
    """Generate a text summary of metrics."""
    summary = f"""
PHISHING URL CLASSIFIER - MODEL EVALUATION REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

=== PERFORMANCE METRICS ===
Accuracy:  {metrics['accuracy']:.4f}
Precision: {metrics['precision']:.4f}
Recall:    {metrics['recall']:.4f}
F1 Score:  {metrics['f1']:.4f}
ROC-AUC:   {metrics['roc_auc']:.4f}

=== INTERPRETATION ===
- Accuracy: Percentage of correct predictions
- Precision: When predicting Phishing, how often is it correct?
- Recall: What percentage of actual phishing URLs are caught?
- F1 Score: Harmonic mean of Precision and Recall
- ROC-AUC: Overall classifier discrimination ability (0.5=random, 1.0=perfect)

=== CONFUSION MATRIX ===
              Predicted
              Legitimate  Phishing
Actual Legitimate   {metrics['confusion_matrix'][0, 0]}        {metrics['confusion_matrix'][0, 1]}
       Phishing      {metrics['confusion_matrix'][1, 0]}        {metrics['confusion_matrix'][1, 1]}

=== STATUS ===
✓ Model evaluation completed successfully
"""
    return summary


def main():
    """Main evaluation routine."""
    print_header("🚀 Phishing URL Classifier - Model Evaluation")
    
    # Load model and data
    model, X, y, df_original = load_model_and_data()
    
    if model is None:
        print("❌ Failed to load model or data")
        return
    
    print(f"✓ Model loaded successfully")
    print(f"✓ Data loaded: {len(X)} samples, {X.shape[1]} features")
    print(f"✓ Dataset class distribution:")
    print(f"    Legitimate: {np.sum(y == 0)} ({np.sum(y == 0)/len(y)*100:.2f}%)")
    print(f"    Phishing:   {np.sum(y == 1)} ({np.sum(y == 1)/len(y)*100:.2f}%)")
    
    # Evaluate model
    print_header("Model Evaluation")
    metrics = evaluate_model(model, X, y)
    print_metrics(metrics)
    
    # Analyze predictions
    analyze_predictions(y, metrics['predictions'], metrics['probabilities'])
    
    # Test sample URLs
    print_header("Sample URL Testing")
    test_sample_urls(model)
    
    # Save detailed report
    print_header("Report Generation")
    report_path = save_detailed_report(
        model, X, y,
        metrics['predictions'],
        metrics['probabilities'],
        df_original
    )
    
    # Generate and save summary
    summary = generate_metrics_summary(metrics)
    summary_path = report_path.replace('.csv', '_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"📄 Summary saved: {summary_path}")
    
    print_header("Evaluation Complete ✓")
    print(summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
