import os
import pandas as pd
from datasets import load_dataset


def get_data_path(subfolder="raw"):
    """Returns the absolute path to a data subfolder."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, "data", subfolder)


def download_huggingface_dataset(dataset_name="ealvaradob/phishing-dataset"):
    """Downloads the dataset from Hugging Face and saves it to data/raw.
    
    Dataset contains URLs with 'text' and 'label' columns.
    """
    try:
        print(f"Fetching {dataset_name}...")
        # Load raw JSON directly — the repo's dataset script is blocked by newer HF versions
        dataset = load_dataset("json", data_files="hf://datasets/ealvaradob/phishing-dataset/urls.json")

        df = pd.DataFrame(dataset['train'])
        output_file = os.path.join(get_data_path("raw"), "phishing_raw_huggingface.csv")
        df.to_csv(output_file, index=False)
        print(f"HuggingFace dataset successfully saved to: {output_file}")
        return True

    except Exception as e:
        print(f"Error downloading HuggingFace dataset: {e}")
        return False


def download_kaggle_dataset():
    """Downloads the Kaggle phishing dataset.
    
    Requires Kaggle API setup:
    1. Install: pip install kaggle
    2. Download credentials from https://www.kaggle.com/settings/account
    3. Place kaggle.json in ~/.kaggle/
    
    Dataset has 48 pre-extracted features from phishing/legitimate webpages.
    """
    try:
        import subprocess
        print("Downloading Kaggle dataset...")
        print("Note: This requires Kaggle API credentials. Setup instructions above.")
        
        # Download to data/raw
        output_dir = get_data_path("raw")
        os.makedirs(output_dir, exist_ok=True)
        
        # Download dataset
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", "shashwatwork/phishing-dataset-for-machine-learning", "-p", output_dir],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Unzip if needed
            import zipfile
            zip_files = [f for f in os.listdir(output_dir) if f.endswith('.zip')]
            for zip_file in zip_files:
                zip_path = os.path.join(output_dir, zip_file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                os.remove(zip_path)
            print(f"✓ Kaggle dataset downloaded to: {output_dir}")
            return True
        else:
            print(f"Kaggle download failed: {result.stderr}")
            return False
    except ImportError:
        print("Error: Kaggle CLI not installed. Install with: pip install kaggle")
        return False
    except Exception as e:
        print(f"Error downloading Kaggle dataset: {e}")
        return False


def load_kaggle_phishing_data():
    """Load the pre-downloaded Kaggle dataset (48 features)."""
    kaggle_csv = os.path.join(get_data_path("raw"), "Phishing_Legitimate_full.csv")
    
    if not os.path.exists(kaggle_csv):
        print(f"Kaggle dataset not found at {kaggle_csv}")
        print("Download it first using: download_kaggle_dataset()")
        return None
    
    df = pd.read_csv(kaggle_csv)
    # Rename class column to 'label' if needed
    if 'class' in df.columns:
        df.rename(columns={'class': 'label'}, inplace=True)
    # Convert -1 (phishing) to 1, 1 (legitimate) to 0
    if df['label'].min() == -1:
        df['label'] = (df['label'] == -1).astype(int)
    
    print(f"✓ Loaded Kaggle data: {df.shape[0]} samples, {df.shape[1]} features")
    return df


if __name__ == "__main__":
    print("Available datasets:")
    print("1. HuggingFace dataset (URLs): download_huggingface_dataset()")
    print("2. Kaggle dataset (48 features): download_kaggle_dataset()")
    download_huggingface_dataset()