"""
Interactive URL Testing Tool
Test individual URLs against the trained model in real-time.
Run: python test_urls_interactive.py
"""

import os
import sys
import joblib
import numpy as np
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from feature_engineering.url_features import extract_url_features


def load_model():
    """Load the trained model."""
    model_path = os.path.join(BASE_DIR, 'models', 'phishing_rf_model.joblib')
    
    if not os.path.exists(model_path):
        print(f"{Fore.RED}❌ Model not found at {model_path}")
        return None
    
    try:
        model = joblib.load(model_path)
        print(f"{Fore.GREEN}✓ Model loaded successfully")
        return model
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to load model: {e}")
        return None


def predict_url(model, url):
    """Predict if a URL is phishing or legitimate."""
    try:
        # Extract features
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
        
        # Make prediction
        prediction = model.predict(feature_array)[0]
        probabilities = model.predict_proba(feature_array)[0]
        
        phishing_prob = probabilities[1]
        legitimate_prob = probabilities[0]
        
        return {
            'prediction': prediction,
            'phishing_prob': phishing_prob,
            'legitimate_prob': legitimate_prob,
            'features': features,
        }
    except Exception as e:
        print(f"{Fore.RED}❌ Error processing URL: {e}")
        return None


def print_result(url, result):
    """Print formatted prediction result."""
    if result is None:
        return
    
    prediction = result['prediction']
    phishing_prob = result['phishing_prob']
    legitimate_prob = result['legitimate_prob']
    features = result['features']
    
    # Determine color and label
    if prediction == 1:
        color = Fore.RED
        label = "🚨 PHISHING"
    else:
        color = Fore.GREEN
        label = "✓ LEGITIMATE"
    
    print(f"\n{color}{'='*70}")
    print(f"{label}")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    print(f"\nURL: {url}")
    print(f"\n{Fore.YELLOW}Prediction Confidence:{Style.RESET_ALL}")
    print(f"  Phishing Probability:    {Fore.RED}{phishing_prob:.2%}{Style.RESET_ALL}")
    print(f"  Legitimate Probability:  {Fore.GREEN}{legitimate_prob:.2%}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Extracted Features:{Style.RESET_ALL}")
    print(f"  URL Length (log):       {features['url_length']:.4f}")
    print(f"  Dot Count:              {features['dot_count']}")
    print(f"  Has @ Symbol:           {bool(features['has_at_symbol'])} ⚠️" if features['has_at_symbol'] else f"  Has @ Symbol:           {bool(features['has_at_symbol'])}")
    print(f"  Has HTTPS:              {bool(features['has_https'])}")
    print(f"  Has Sensitive Word:     {bool(features['has_sensitive_word'])} ⚠️" if features['has_sensitive_word'] else f"  Has Sensitive Word:     {bool(features['has_sensitive_word'])}")
    print(f"  Suspicious TLD:         {bool(features['is_suspicious_tld'])} ⚠️" if features['is_suspicious_tld'] else f"  Suspicious TLD:         {bool(features['is_suspicious_tld'])}")
    print(f"  Has Hyphens:            {bool(features['has_hyphens'])}")
    print(f"  Known Legitimate:       {bool(features['is_known_legit'])} ✓" if features['is_known_legit'] else f"  Known Legitimate:       {bool(features['is_known_legit'])}")
    print(f"  Known Brand:            {bool(features['is_known_brand'])} ✓" if features['is_known_brand'] else f"  Known Brand:            {bool(features['is_known_brand'])}")
    
    print()


def print_banner():
    """Print welcome banner."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🔐 Phishing URL Classifier - Interactive Tester        ║
║                                                                  ║
║  Test URLs in real-time to detect if they are phishing or       ║
║  legitimate. Enter URLs one at a time for analysis.              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)


def print_example_urls():
    """Print example URLs to test."""
    examples = """
{Fore.YELLOW}Example URLs to test:{Style.RESET_ALL}

Legitimate URLs:
  https://www.google.com
  https://github.com/username/repo
  https://www.amazon.com/products
  https://en.wikipedia.org/wiki/Machine_Learning

Suspicious/Phishing URLs:
  http://g00gle-login-verify.xyz/account/confirm
  http://amazon-payment.top/login
  http://paypal@phishing.com/account
  http://verify-account-now.tk

Type 'quit' or 'exit' to stop testing.
Type 'examples' to see more URLs.
"""
    print(examples)


def main():
    """Main interactive testing loop."""
    print_banner()
    
    # Load model
    print(f"\n{Fore.BLUE}Loading model...{Style.RESET_ALL}")
    model = load_model()
    
    if model is None:
        print(f"{Fore.RED}Cannot proceed without model.{Style.RESET_ALL}")
        return
    
    print_example_urls()
    
    test_count = 0
    
    while True:
        try:
            print(f"\n{Fore.BLUE}Enter URL to test (or 'quit'/'examples'/'help'):{Style.RESET_ALL}")
            user_input = input("> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Fore.GREEN}✓ Thank you for testing! {test_count} URLs analyzed.{Style.RESET_ALL}")
                break
            
            if user_input.lower() == 'examples':
                print_example_urls()
                continue
            
            if user_input.lower() == 'help':
                print(f"""
{Fore.CYAN}Commands:{Style.RESET_ALL}
  - Enter any URL to test
  - Type 'examples' to see sample URLs
  - Type 'quit' or 'exit' to stop
  - Type 'help' to see this message
                """)
                continue
            
            # Predict
            result = predict_url(model, user_input)
            print_result(user_input, result)
            test_count += 1
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️ Testing interrupted by user.{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
