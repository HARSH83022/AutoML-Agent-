"""
Setup Kaggle credentials from .env file
This creates the ~/.kaggle/kaggle.json file that Kaggle API expects
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def setup_kaggle_credentials():
    """Setup Kaggle credentials from environment variables"""
    
    kaggle_username = os.getenv("KAGGLE_USERNAME")
    kaggle_key = os.getenv("KAGGLE_KEY")
    
    if not kaggle_username or not kaggle_key:
        print("❌ ERROR: KAGGLE_USERNAME and KAGGLE_KEY not found in .env file")
        print("\nPlease add them to your .env file:")
        print("KAGGLE_USERNAME=your_username")
        print("KAGGLE_KEY=your_api_key")
        print("\nGet your API key from: https://www.kaggle.com/settings/account")
        return False
    
    # Create .kaggle directory in user's home
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    
    # Create kaggle.json file
    kaggle_json_path = kaggle_dir / "kaggle.json"
    
    credentials = {
        "username": kaggle_username,
        "key": kaggle_key
    }
    
    with open(kaggle_json_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    # Set proper permissions (Unix-like systems)
    try:
        os.chmod(kaggle_json_path, 0o600)
    except:
        pass  # Windows doesn't support chmod
    
    print("✅ Kaggle credentials configured successfully!")
    print(f"   Created: {kaggle_json_path}")
    print(f"   Username: {kaggle_username}")
    print("\nYou can now use Kaggle datasets in your AutoML runs.")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("KAGGLE CREDENTIALS SETUP")
    print("=" * 60)
    print()
    
    success = setup_kaggle_credentials()
    
    if success:
        print("\n" + "=" * 60)
        print("TESTING KAGGLE CONNECTION")
        print("=" * 60)
        print()
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            
            print("✅ Kaggle authentication successful!")
            print("\nTesting dataset search...")
            
            datasets = api.dataset_list(search="iris", page=1, max_size=3)
            print(f"✅ Found {len(datasets)} datasets:")
            for ds in datasets:
                print(f"   - {ds.ref}: {ds.title}")
            
            print("\n✅ All tests passed! Kaggle is ready to use.")
            
        except Exception as e:
            print(f"❌ Kaggle test failed: {e}")
            print("\nTroubleshooting:")
            print("1. Check your credentials at: https://www.kaggle.com/settings/account")
            print("2. Make sure you've accepted Kaggle's terms of service")
            print("3. Try running: pip install kaggle --upgrade")
    
    print("\n" + "=" * 60)
