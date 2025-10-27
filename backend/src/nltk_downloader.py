import nltk
def ensure_nltk_data():
    """
    Checks for and downloads NLTK 'punkt' and 'stopwords' if they are missing.
    """
    try:
        # Check if 'punkt' is available
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("NLTK 'punkt' tokenizer not found. Downloading...")
        nltk.download('punkt', quiet=True) # quiet=True suppresses verbose output

    try:
        # Check if 'stopwords' is available
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("NLTK 'stopwords' corpus not found. Downloading...")
        nltk.download('stopwords', quiet=True)