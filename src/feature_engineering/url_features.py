import os
import pandas as pd
import numpy as np


def normalize_url(url):
    """Strips http/https prefix, recording the https flag before removal."""
    has_https = 1 if url.startswith('https://') else 0
    # Strip protocol so length/dot features match the training data distribution
    for prefix in ('https://', 'http://'):
        if url.startswith(prefix):
            url = url[len(prefix):]
            break
    return url, has_https


def is_known_brand(url):
    """Checks if URL contains a known major brand/company name."""
    brands = [
        'google', 'amazon', 'facebook', 'github', 'microsoft', 'netflix', 'apple',
        'twitter', 'linkedin', 'instagram', 'reddit', 'youtube', 'wikipedia',
        'ebay', 'paypal', 'uber', 'airbnb', 'spotify', 'dropbox', 'slack',
        'adobe', 'salesforce', 'oracle', 'ibm', 'intel', 'cisco', 'nokia',
        'samsung', 'sony', 'lg', 'hp', 'dell', 'lenovo', 'asus'
    ]
    return 1 if any(brand in url.lower() for brand in brands) else 0


def extract_url_features(url):
    """Extracts 9 numerical features from a URL string."""
    normalized_url, has_https = normalize_url(url)
    url_lower = normalized_url.lower()
    
    # Check if URL contains known brand
    known_brand = is_known_brand(normalized_url)
    
    # Refined list: Only words that indicate phishing intent/urgency
    sensitive_words = ['login', 'verify', 'account', 'confirm', 'password']
    has_sensitive_word = 1 if any(word in url_lower for word in sensitive_words) else 0
    
    # Known legitimate domains that are NEVER phishing
    known_legit_domains = [
        'nationalgeographic.com', 'bbc.co.uk', 'nytimes.com', 
        'sciencedirect.com', 'nature.com', 'pnas.org', 'arxiv.org',
        'ieee.org', 'acm.org', 'springer.com',
        'washingtonpost.com', 'theguardian.com', 'bbc.com',
        'reuters.com', 'apnews.com', 'cnn.com', 'bbc.co'
    ]
    is_known_legit = 1 if any(domain in url_lower for domain in known_legit_domains) else 0
    
    # Check for suspicious TLDs by matching at the END of domain (before path)
    suspicious_tlds = ['.xyz', '.info', '.top', '.tk', '.ml', '.co']
    
    # Extract just the domain part (before the first /)
    domain_part = normalized_url.split('/')[0]
    domain_lower = domain_part.lower()
    
    # For .co, explicitly check that it's NOT part of .com or .co.uk, .co.id, etc.
    is_suspicious_tld = 0
    for tld in suspicious_tlds:
        if domain_lower.endswith(tld):
            # Exception: .co at the end is suspicious UNLESS it's .co.uk, .co.id, etc.
            if tld == '.co' and len(domain_lower) > 4:
                # Check if it's actually .co[something] like .co.uk
                if not domain_lower.endswith(('.co.uk', '.co.id', '.co.nz', '.co.za', '.co.jp', '.co.in')):
                    is_suspicious_tld = 1
                    break
            else:
                is_suspicious_tld = 1
                break
    
    return {
        'url_length': np.log1p(len(normalized_url)),  # Log-normalized to reduce impact of very long URLs
        'dot_count': normalized_url.count('.'),
        'has_at_symbol': 1 if '@' in normalized_url else 0,  # '@' hides the true host
        'has_https': has_https,
        'has_sensitive_word': has_sensitive_word,
        'is_suspicious_tld': is_suspicious_tld,
        'has_hyphens': 1 if '-' in normalized_url else 0,  # Phishing domains often use hyphens
        'is_known_legit': is_known_legit,  # Legitimate domains get immunity
        'is_known_brand': known_brand,  # Major brands are rarely phishing targets
    }


def process_dataset(input_file, output_file):
    """Loads raw CSV, extracts features via vectorized ops, and saves processed CSV."""
    print(f"Loading raw data from: {input_file}")
    df = pd.read_csv(input_file)

    # Sample large datasets to keep training times reasonable
    if len(df) > 20000:
        print("Large dataset detected — sampling 20,000 rows.")
        df = df.sample(n=20000, random_state=42).reset_index(drop=True)

    print("Extracting features from URLs...")
    texts = df['text'].astype(str)
    
    # Normalize URLs: strip protocol like extract_url_features does
    def strip_protocol(url_str):
        for prefix in ('https://', 'http://'):
            if url_str.startswith(prefix):
                return url_str[len(prefix):]
        return url_str
    
    normalized_texts = texts.apply(strip_protocol)

    # Refined list: Only words that indicate phishing intent/urgency
    sensitive_words = ['login', 'verify', 'account', 'confirm', 'password']
    has_sensitive_word = normalized_texts.str.lower().str.contains('|'.join(sensitive_words), regex=True).astype(int)
    
    # Known legitimate domains that are NEVER phishing
    def is_known_legit(url):
        known_legit_domains = [
            'nationalgeographic.com', 'bbc.co.uk', 'nytimes.com',
            'sciencedirect.com', 'nature.com', 'pnas.org', 'arxiv.org',
            'ieee.org', 'acm.org', 'springer.com',
            'washingtonpost.com', 'theguardian.com', 'bbc.com',
            'reuters.com', 'apnews.com', 'cnn.com', 'bbc.co'
        ]
        return 1 if any(domain in url.lower() for domain in known_legit_domains) else 0
    
    is_known_legit_series = normalized_texts.apply(is_known_legit).astype(int)
    
    # Check for suspicious TLDs by matching at the END of domain
    def has_suspicious_tld(url):
        url_lower = url.lower()
        # Extract just the domain part (before the first /)
        domain_part = url_lower.split('/')[0]
        
        suspicious_tlds = ['.xyz', '.info', '.top', '.tk', '.ml', '.co']
        for tld in suspicious_tlds:
            if domain_part.endswith(tld):
                if tld == '.co':
                    # Exclude country-specific .co domains
                    if not domain_part.endswith(('.co.uk', '.co.id', '.co.nz', '.co.za', '.co.jp', '.co.in')):
                        return 1
                else:
                    return 1
        return 0
    
    is_suspicious_tld = normalized_texts.apply(has_suspicious_tld).astype(int)
    
    # Check for known brands
    is_known_brand_series = normalized_texts.apply(is_known_brand).astype(int)

    # Vectorized extraction is significantly faster than row-by-row apply()
    features_df = pd.DataFrame({
        'url_length': np.log1p(texts.astype(str).str.len()),  # Log-normalized URL length
        'dot_count': texts.astype(str).str.count(r'\.'),
        'has_at_symbol': texts.astype(str).str.contains('@').astype(int),
        'has_https': texts.astype(str).str.startswith('https://').astype(int),
        'has_sensitive_word': has_sensitive_word,
        'is_suspicious_tld': is_suspicious_tld,
        'has_hyphens': texts.astype(str).str.contains('-').astype(int),
        'is_known_legit': is_known_legit_series,
        'is_known_brand': is_known_brand_series,
    })

    processed_df = pd.concat([features_df, df['label']], axis=1)
    processed_df.to_csv(output_file, index=False)
    print(f"Saved processed data to: {output_file}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    raw_data_path = os.path.join(base_dir, "data", "raw", "phishing_raw.csv")
    processed_data_path = os.path.join(base_dir, "data", "processed", "phishing_processed.csv")

    if not os.path.exists(raw_data_path):
        print(f"Error: Raw data not found at {raw_data_path}")
        print("Please run data_loader.py first.")
    else:
        process_dataset(raw_data_path, processed_data_path)
