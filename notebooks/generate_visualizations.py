"""
Visualization Generation Script
Creates all 8+ figures needed for the technical report.
Run: python notebooks/generate_visualizations.py
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from feature_engineering.url_features import extract_url_features


def create_output_dir():
    """Create output directory for visualizations."""
    output_dir = os.path.join(BASE_DIR, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def load_data():
    """Load model and processed data."""
    model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
    processed_data_path = os.path.join(BASE_DIR, 'data', 'processed', 'phishing_processed.csv')
    
    model = joblib.load(model_path)
    df = pd.read_csv(processed_data_path)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    return model, X, y


def figure1_correlation_heatmap(X, output_dir):
    """Figure 1: Feature Correlation Heatmap"""
    print("Generating Figure 1: Feature Correlation Heatmap...")
    
    plt.figure(figsize=(10, 8))
    correlation_matrix = X.corr()
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                square=True, cbar_kws={'label': 'Correlation'})
    plt.title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure1_Correlation_Heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure2_feature_distributions(X, output_dir):
    """Figure 2: Feature Distribution Histograms"""
    print("Generating Figure 2: Feature Distribution Histograms...")
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    fig.suptitle('Feature Distributions', fontsize=16, fontweight='bold')
    
    for idx, col in enumerate(X.columns):
        row = idx // 3
        col_idx = idx % 3
        ax = axes[row, col_idx]
        
        ax.hist(X[col], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_title(col, fontweight='bold')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure2_Feature_Distributions.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure3_class_distribution(y, output_dir):
    """Figure 3: Class Distribution Bar Chart"""
    print("Generating Figure 3: Class Distribution Bar Chart...")
    
    plt.figure(figsize=(10, 6))
    class_counts = y.value_counts()
    colors = ['#2ecc71', '#e74c3c']
    labels = ['Legitimate (0)', 'Phishing (1)']
    
    bars = plt.bar(labels, [class_counts[0], class_counts[1]], color=colors, edgecolor='black', linewidth=2)
    plt.title('Dataset Class Distribution', fontsize=14, fontweight='bold')
    plt.ylabel('Number of URLs', fontsize=12)
    plt.xlabel('Class', fontsize=12)
    
    # Add count labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}\n({int(height)/len(y)*100:.1f}%)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure3_Class_Distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure4_url_length_distribution(X, y, output_dir):
    """Figure 4: URL Length Distribution by Class"""
    print("Generating Figure 4: URL Length Distribution by Class...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    legit_lengths = X[y == 0]['url_length']
    phishing_lengths = X[y == 1]['url_length']
    
    ax.hist(legit_lengths, bins=30, alpha=0.6, label='Legitimate', color='#2ecc71', edgecolor='black')
    ax.hist(phishing_lengths, bins=30, alpha=0.6, label='Phishing', color='#e74c3c', edgecolor='black')
    
    plt.title('URL Length Distribution by Class', fontsize=14, fontweight='bold')
    plt.xlabel('Log-Normalized URL Length', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure4_URL_Length_Distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure5_confusion_matrix(model, X, y, output_dir):
    """Figure 5: Confusion Matrix Heatmap"""
    print("Generating Figure 5: Confusion Matrix Heatmap...")
    
    predictions = model.predict(X)
    cm = confusion_matrix(y, predictions)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': 'Count'},
                xticklabels=['Legitimate', 'Phishing'],
                yticklabels=['Legitimate', 'Phishing'])
    plt.title('Confusion Matrix - Random Forest Model', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure5_Confusion_Matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure6_roc_curve(model, X, y, output_dir):
    """Figure 6: ROC Curve"""
    print("Generating Figure 6: ROC Curve...")
    
    probabilities = model.predict_proba(X)[:, 1]
    fpr, tpr, thresholds = roc_curve(y, probabilities)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='#3498db', lw=2.5, label=f'ROC Curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='red', lw=2, linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve - Model Performance', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure6_ROC_Curve.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure7_precision_recall_curve(model, X, y, output_dir):
    """Figure 7: Precision-Recall Curve"""
    print("Generating Figure 7: Precision-Recall Curve...")
    
    probabilities = model.predict_proba(X)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y, probabilities)
    
    plt.figure(figsize=(10, 8))
    plt.plot(recall, precision, color='#2ecc71', lw=2.5, label='Precision-Recall Curve')
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curve - Model Trade-offs', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure7_Precision_Recall_Curve.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure8_feature_importance(model, X, output_dir):
    """Figure 8: Feature Importance Chart"""
    print("Generating Figure 8: Feature Importance Chart...")
    
    feature_importance = model.feature_importances_
    features = X.columns
    
    # Sort by importance
    indices = np.argsort(feature_importance)[::-1]
    
    plt.figure(figsize=(12, 7))
    plt.bar(range(len(indices)), feature_importance[indices], color='#9b59b6', edgecolor='black', alpha=0.7)
    plt.xticks(range(len(indices)), [features[i] for i in indices], rotation=45, ha='right')
    plt.title('Feature Importance - Random Forest Model', fontsize=14, fontweight='bold')
    plt.xlabel('Feature', fontsize=12)
    plt.ylabel('Importance Score', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure8_Feature_Importance.png'), dpi=300, bbox_inches='tight')
    plt.close()


def figure9_model_metrics_comparison(model, X, y, output_dir):
    """Figure 9: Model Metrics Comparison"""
    print("Generating Figure 9: Model Metrics Comparison...")
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]
    
    metrics = {
        'Accuracy': accuracy_score(y, predictions),
        'Precision': precision_score(y, predictions),
        'Recall': recall_score(y, predictions),
        'F1 Score': f1_score(y, predictions),
        'ROC-AUC': roc_auc_score(y, probabilities),
    }
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors_metric = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
    bars = ax.bar(metrics.keys(), metrics.values(), color=colors_metric, edgecolor='black', linewidth=2)
    
    plt.title('Model Performance Metrics', fontsize=14, fontweight='bold')
    plt.ylabel('Score', fontsize=12)
    plt.ylim([0, 1])
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Figure9_Metrics_Comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Generate all visualizations."""
    print("\n" + "="*60)
    print("  📊 Generating Visualizations for Technical Report")
    print("="*60 + "\n")
    
    output_dir = create_output_dir()
    print(f"✓ Output directory: {output_dir}\n")
    
    # Load data
    print("📂 Loading model and data...")
    model, X, y = load_data()
    print("✓ Model and data loaded\n")
    
    # Generate all figures
    figure1_correlation_heatmap(X, output_dir)
    figure2_feature_distributions(X, output_dir)
    figure3_class_distribution(y, output_dir)
    figure4_url_length_distribution(X, y, output_dir)
    figure5_confusion_matrix(model, X, y, output_dir)
    figure6_roc_curve(model, X, y, output_dir)
    figure7_precision_recall_curve(model, X, y, output_dir)
    figure8_feature_importance(model, X, output_dir)
    figure9_model_metrics_comparison(model, X, y, output_dir)
    
    print("\n" + "="*60)
    print("✓ All visualizations generated successfully!")
    print("="*60)
    print(f"\nOutputs saved to: {output_dir}")
    print("\nGenerated files:")
    for i in range(1, 10):
        print(f"  ✓ Figure{i}_*.png")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
