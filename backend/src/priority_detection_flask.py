import spacy # type: ignore
from spacy.cli import download # type: ignore

# ---------- Cached spaCy loader ----------
_nlp = None

def get_nlp():
    """Load and cache spaCy model once."""
    global _nlp
    if _nlp is None:
        model_name = "en_core_web_sm"
        try:
            _nlp = spacy.load(model_name, disable=["parser"])
        except OSError:
            print(f"[INFO] spaCy model '{model_name}' not found. Downloading...")
            download(model_name)
            _nlp = spacy.load(model_name, disable=["parser"])
        print("[INFO] spaCy model loaded and cached successfully.")
    return _nlp


# ---------- Manual NLP-based priority detection ----------
def detect_priority(email_text: str) -> str:
    """
    Detects priority based on certain keywords, entities, and tone of the email.
    Returns: "High", "Medium", or "Low"
    """
    nlp = get_nlp()
    doc = nlp(email_text.lower())

    # --- Keyword-based heuristic rules ---
    high_keywords = [
        "urgent", "asap", "immediately", "critical", "important", "deadline",
        "issue", "problem", "payment", "fail", "error", "approve", "cancel", "delay"
    ]
    medium_keywords = ["update", "review", "schedule", "meeting", "reminder", "follow up"]
    low_keywords = ["thanks", "thank you", "newsletter", "greetings", "invitation"]

    high_count = sum(1 for token in doc if token.lemma_ in high_keywords)
    medium_count = sum(1 for token in doc if token.lemma_ in medium_keywords)
    low_count = sum(1 for token in doc if token.lemma_ in low_keywords)

    # --- Named Entity Recognition (NER) cues ---
    has_date_or_money = any(ent.label_ in ["DATE", "MONEY"] for ent in doc.ents)

    # --- Scoring system ---
    score = high_count * 3 + medium_count * 2 + low_count
    if has_date_or_money:
        score += 2  # deadlines or invoices often imply higher priority

    # --- Decision ---
    if score >= 5 or high_count > 0:
        priority = "High"
    elif 3 <= score < 5:
        priority = "Medium"
    else:
        priority = "Low"
    
    entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "DATE", "MONEY", "GPE"]]
    
    return {
        "priority": priority,
        "entities": entities
    }
