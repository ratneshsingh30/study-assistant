import nltk
import os

# This will be called by app.py on startup
def download_nltk_data():
    """Download required NLTK data if not already present"""
    try:
        # Check if punkt is already downloaded
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            print("Downloaded NLTK punkt")
        
        # Check if stopwords is already downloaded
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            print("Downloaded NLTK stopwords")
        
        # Check if wordnet is already downloaded
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
            print("Downloaded NLTK wordnet")
        
        return True
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")
        return False