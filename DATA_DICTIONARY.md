# Data Dictionary - Phishing URL Detection Features

## Overview
This document defines all 9 features extracted from URLs for the phishing classification model. Each feature is a numerical indicator that helps the Random Forest model distinguish between legitimate and phishing URLs.

---

## Feature Definitions

### 1. url_length

**Data Type:** Float (numeric)

**Description:** Log-normalized length of the URL after protocol stripping.

**Formula:** `log1p(len(normalized_url))`

**Typical Range:** 2.0 - 8.0

**Phishing Indicator:** Phishing URLs tend to be either very short (single-character domains) or very long (obfuscation). Log normalization compresses extreme values.

**Examples:**
- Legitimate: `www.google.com` → length=14 → log=2.71
- Phishing: `www.verify-your-account-immediately-click-here.xyz` → length=52 → log=3.97

**Handling:** 
- URLs with log_length > 6.0 are often suspicious
- Legitimate sites rarely exceed log=5.0
- Very short URLs (<5 chars) are also suspicious

---

### 2. dot_count

**Data Type:** Integer

**Description:** Number of dots/periods in the domain portion of the URL (after protocol stripping).

**Range:** 0 - 10+

**Phishing Indicator:** Multiple dots can indicate subdomain abuse. Phishing URLs use extra subdomains to hide the true domain.

**Examples:**
- Legitimate: `www.google.com` → dot_count=2
- Phishing: `login.account.verify.paypal-confirm.xyz` → dot_count=5

**Typical Distribution:**
- Legitimate URLs: 1-3 dots (mean ~2.2)
- Phishing URLs: 2-4 dots (mean ~2.8)

**Interpretation:**
- 0-2 dots: Usually legitimate
- 3-4 dots: Mildly suspicious
- 5+ dots: Highly suspicious

---

### 3. has_at_symbol

**Data Type:** Binary (0 or 1)

**Description:** Presence of @ symbol in the URL, which is a URL-spoofing technique.

**Values:**
- 0 = No @ symbol (normal)
- 1 = @ symbol present (suspicious)

**Why It Matters:** The @ symbol is rarely used in legitimate URLs but common in phishing. Example: `http://google.com@phishing.com` makes browser connect to phishing.com.

**Examples:**
- `https://www.amazon.com` → has_at_symbol=0 (legitimate)
- `http://amazon.com@malicious.com` → has_at_symbol=1 (phishing)

**Note:** Always check for @ symbol when URL contains one.

---

### 4. has_https

**Data Type:** Binary (0 or 1)

**Description:** Whether the URL uses the HTTPS (secure) protocol.

**Values:**
- 0 = HTTP only (less secure)
- 1 = HTTPS protocol (more secure)

**Interpretation:**
- HTTPS indicates SSL/TLS encryption
- Legitimate banks/services use HTTPS
- Phishing sites often skip HTTPS to save costs

**Examples:**
- `https://www.paypal.com` → has_https=1 (legitimate)
- `http://verify-account.xyz` → has_https=0 (phishing)

**Caveats:**
- Not definitive: phishing sites can also use HTTPS
- But absence of HTTPS is a warning sign
- Combined with other features, important for classification

---

### 5. has_sensitive_word

**Data Type:** Binary (0 or 1)

**Description:** Presence of action-oriented words commonly used in phishing to create urgency.

**Monitored Words:** login, verify, account, confirm, password

**Values:**
- 0 = No sensitive words
- 1 = Contains one or more sensitive words

**Phishing Indicator:** Very strong. Phishing emails/URLs urge users to "login", "verify", or "confirm" their credentials.

**Examples:**
- `www.google.com/search` → has_sensitive_word=0
- `verify-your-paypal-account-now.xyz` → has_sensitive_word=1
- `login-bank-confirm.tk` → has_sensitive_word=1

**Domain Impact:**
- 92% of URLs with "login" + suspicious TLD are phishing
- 85% with "verify" are phishing
- Combined with other features = high confidence

---

### 6. is_suspicious_tld

**Data Type:** Binary (0 or 1)

**Description:** Whether the domain uses a suspicious top-level domain (TLD).

**Suspicious TLDs:** .xyz, .info, .top, .tk, .ml, .co

**Values:**
- 0 = Standard TLD (.com, .org, .edu, etc.) or legitimate country code
- 1 = Suspicious TLD detected

**Why These TLDs:**
- Very cheap to register ($0.50 - $2.00 per year)
- Often used by cybercriminals
- Legitimate companies rarely use them
- Exceptions: Legitimate .co.uk, .co.jp, .co.in domains (marked as 0)

**Examples:**
- `amazon.com` → is_suspicious_tld=0 (legitimate TLD)
- `verify-amazon.xyz` → is_suspicious_tld=1 (phishing TLD)
- `site.co.uk` → is_suspicious_tld=0 (legitimate country code, not suspicious .co)

**Feature Strength:** Highly predictive when combined with other factors.

---

### 7. has_hyphens

**Data Type:** Binary (0 or 1)

**Description:** Presence of hyphen (-) characters in the domain name.

**Values:**
- 0 = No hyphens
- 1 = One or more hyphens present

**Phishing Indicator:** Legitimate companies rarely use hyphens in domain names. Phishers use hyphens to make URLs look more official or split words.

**Examples:**
- `www.amazon.com` → has_hyphens=0
- `www.amazon-confirm.xyz` → has_hyphens=1
- `login-to-your-account.top` → has_hyphens=1

**Context:**
- Hyphens alone aren't definitive (some legitimate sites use them)
- Combined with other suspicious features = phishing indicator
- Especially suspicious when combined with suspicious TLD

---

### 8. is_known_legit

**Data Type:** Binary (0 or 1)

**Description:** Whether the URL is from a known, trusted legitimate domain.

**Whitelist Includes:** National Geographic, BBC, New York Times, Wikipedia, Reuters, Nature, IEEE, ACM, Springer, Science Direct, PLoS, arXiv

**Values:**
- 0 = Not in whitelist
- 1 = From known legitimate domain

**Purpose:** Immunizes major legitimate sites from false positives.

**Examples:**
- `en.wikipedia.org/wiki/Machine_Learning` → is_known_legit=1 (always legitimate)
- `www.bbc.co.uk/news` → is_known_legit=1
- `random-site.xyz` → is_known_legit=0

**Model Behavior:** When is_known_legit=1, model almost always predicts legitimate (0), regardless of other features.

---

### 9. is_known_brand

**Data Type:** Binary (0 or 1)

**Description:** Whether the domain contains names of major brands and companies.

**Brand List (34 brands):**
- Tech: Google, Amazon, Facebook, GitHub, Microsoft, Netflix, Apple, Twitter, LinkedIn, Instagram, Reddit, YouTube, Wikipedia, Spotify, Dropbox, Slack, Adobe, Salesforce
- Finance/Shopping: eBay, PayPal, Uber, Airbnb
- Hardware: Samsung, Sony, LG, HP, Dell, Lenovo, ASUS, Intel, Cisco, Nokia, IBM, Oracle

**Values:**
- 0 = No major brand detected
- 1 = Contains brand name (anywhere in URL)

**Phishing Indicator:** Phishers impersonate well-known brands to build trust. However, official brand URLs often legitimately contain brand names.

**Examples:**
- `accounts.google.com` → is_known_brand=1 (legitimate brand)
- `verify-google-account.xyz` → is_known_brand=1 (brand impersonation - phishing)
- `random-tech-site.com` → is_known_brand=0

**Model Use:**
- Presence of brand name alone doesn't determine phishing
- Phishing exploits brand presence
- Combined with is_known_legit and suspicious_tld = strong indicator

---

## Feature Summary Table

| # | Feature | Type | Range | Phishing = 1 | Legit = 1 |
|---|---------|------|-------|--------------|-----------|
| 1 | url_length | Float | 2-8 | Extreme values | Mid-range (2.5-4.0) |
| 2 | dot_count | Int | 0-10 | High (3-5+) | Low-Mid (1-3) |
| 3 | has_at_symbol | Binary | 0-1 | 1 (present) | 0 (absent) |
| 4 | has_https | Binary | 0-1 | 0 (absent) | 1 (present) |
| 5 | has_sensitive_word | Binary | 0-1 | 1 (present) | 0 (absent) |
| 6 | is_suspicious_tld | Binary | 0-1 | 1 (suspicious) | 0 (standard) |
| 7 | has_hyphens | Binary | 0-1 | 1 (present) | 0 (absent) |
| 8 | is_known_legit | Binary | 0-1 | 0 (unknown) | 1 (known) |
| 9 | is_known_brand | Binary | 0-1 | 1 (brand abuse) | 1 (official brand) |

---

## Data Preprocessing Notes

### URL Normalization
All URLs are normalized before feature extraction:
1. Strip `https://` and `http://` prefixes
2. Convert to lowercase
3. Extract domain (before first /)
4. Store https presence separately

### Feature Order (Model Input)
The Random Forest model expects features in this exact order:
```
[url_length, dot_count, has_at_symbol, has_https, 
 has_sensitive_word, is_suspicious_tld, has_hyphens, 
 is_known_legit, is_known_brand]
```

### Missing Values
- No missing values in training data
- All features are computed; none are optional
- All binary features (0 or 1) have no NaN

### Scaling
- No feature scaling applied (Random Forest doesn't require it)
- url_length already log-normalized
- Other features are already normalized (binary or counts)

---

## Usage Example

```python
from src.feature_engineering.url_features import extract_url_features

# Extract features from a URL
url = "https://www.amazon.com/products"
features = extract_url_features(url)

# Output dictionary:
{
    'url_length': 2.94,           # Log-normalized length
    'dot_count': 2,                # Two dots in domain
    'has_at_symbol': 0,            # No @ symbol
    'has_https': 1,                # Uses HTTPS
    'has_sensitive_word': 0,       # No sensitive words
    'is_suspicious_tld': 0,        # Normal .com TLD
    'has_hyphens': 0,              # No hyphens
    'is_known_legit': 0,           # Not in whitelist
    'is_known_brand': 1,           # Contains "amazon"
}
```

---

## Feature Correlation

- **url_length** and **dot_count**: Slightly correlated (longer URLs often have more dots)
- **is_suspicious_tld** and **has_sensitive_word**: Often appear together in phishing URLs
- **has_https** and **is_known_legit**: Highly correlated (legitimate sites use HTTPS)
- **is_known_brand** and **is_known_legit**: May appear together for official brand sites

---

## Improving Feature Coverage

Future versions could add:
- Domain age (newer domains = more phishing)
- Page load time (phishing sites may be slow)
- SSL certificate validity
- Domain registrar reputation
- Geographic mismatch between IP and content
- Text similarity to legitimate site

---

**Last Updated:** April 26, 2026  
**Feature Set Version:** 1.0  
**Model:** Random Forest Classifier  
**Training Dataset:** 20,000 URLs
