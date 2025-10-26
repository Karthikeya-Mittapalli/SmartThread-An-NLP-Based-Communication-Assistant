import spacy  # type: ignore
import threading
import re
import dateparser  # type: ignore
from spacy.cli import download  # type: ignore
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
from datetime import datetime

# ---------- Cached spaCy loader ----------
_nlp = None
_vader = SentimentIntensityAnalyzer()  # Initialize VADER sentiment analyzer
_load_lock = threading.Lock()


def get_nlp():
    """Load and cache spaCy model once."""
    global _nlp
    with _load_lock:
        if _nlp is None:
            model_name = "en_core_web_sm"
            try:
                _nlp = spacy.load(model_name, disable=["parser"])
            except OSError:
                print(
                    f"[INFO] spaCy model '{model_name}' not found. Downloading...")
                download(model_name)
                _nlp = spacy.load(model_name, disable=["parser"])
        if "parser" not in _nlp.pipe_names and "senter" not in _nlp.pipe_names:
            _nlp.add_pipe("sentencizer")
    return _nlp


# ---------- Manual NLP-based priority detection ----------
def detect_priority(email_text: str) -> dict:
    """
    Improved intermediate priority detector:
    - keyword + proximity weighting
    - imperative/modal detection (POS/sentence-level)
    - sentiment cue (VADER)
    - date proximity boosting
    Returns:
    {
        "priority": "High" | "Medium" | "Low",
        "entities": [list of extracted entities]
    }
    """
    nlp = get_nlp()
    text = email_text.strip()
    doc = nlp(text)

    # --- Keyword-based heuristic rules ---

    HIGH_KW = {"urgent", "asap", "immediately", "critical", "important", "deadline", "due", "submit", "due by", "action required"}
    MED_KW = {"update", "review", "schedule", "meeting", "reminder", "follow up", "follow-up"}
    LOW_KW = {"newsletter", "thanks", "thank you", "invitation", "fyi"}

    lower = text.lower()

    def count_kw_set(kwset):
        count = 0
        for token in doc:
            if token.lemma_ and token.lemma_.lower() in kwset:
                count += 1
        for phrase in [p for p in kwset if " " in p]:
            if phrase in lower:
                count += 1
        return count

    high_count = count_kw_set(HIGH_KW)
    medium_count = count_kw_set(MED_KW)
    low_count = count_kw_set(LOW_KW)

    # entity extraction
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents if ent.label_ in {"DATE", "MONEY", "ORG", "PERSON", "TIME"}]

    # imperative & modal detection
    imperative_score = 0
    modal_score = 0
    modal_words = {"must", "should", "need to", "have to","required to", "ought to", "please", "kindly"}
    for sent in doc.sents:
        first = sent[0]
        if first.pos_ == "VB" and not sent.text.lower().startswith(("please", "just", "kindly")):
            imperative_score += 2
            print(f"[DEBUG] Imperative detected: '{sent.text}'")
        sent_lower = sent.text.lower()
        if any(m in sent_lower for m in modal_words):
            modal_score += 1

    # sentiment analysis (VADER)
    vader_res = _vader.polarity_scores(text)
    neg = vader_res['neg']
    compound = vader_res['compound']
    sentiment_boost = 0
    if compound <= -0.45:
        sentiment_boost += 2  # strongly negative
    elif compound <= -0.2:
        sentiment_boost += 1  # moderately negative

    # date proximity boosting
    date_boost = 0
    parsed_dates = []
    now = datetime.now()
    for ent in doc.ents:
        if ent.label_ == "DATE":
            parsed_date = dateparser.parse(
                ent.text,
                settings={
                    'RELATIVE_BASE': now,
                    'PREFER_DATES_FROM': 'future'
                }
            )
            if parsed_date:
                delta_days = (parsed_date - now).days
                print(delta_days)
                if 0 <= delta_days <= 30:
                    parsed_dates.append(parsed_date)

    for d in parsed_dates:
        if d:
            delta_days = (d - now).days
            if delta_days <= 7:
                date_boost += 3
            elif 7 < delta_days <= 21:
                date_boost += 1
            else:
                continue

    if parsed_dates:
        date_token_idxs = set()
        for ent in doc.ents:
            if ent.label_ == "DATE":
                for token in ent:
                    date_token_idxs.add(token.i)
        deadline_idxs = [token.i for token in doc if token.lemma_ in {
            "deadline", "due", "submit"}]
        for di in deadline_idxs:
            for ti in date_token_idxs:
                if abs(di - ti) <= 6:
                    date_boost += 2

    # final score calculation
    score = high_count * 4 + medium_count * 2 - low_count
    score += imperative_score * 2
    score += modal_score
    score += sentiment_boost
    score += date_boost
    print(f"[DEBUG] score breakdown: high={high_count*4}, medium={medium_count*2}, low={-low_count}, imperative={imperative_score*2}, modal={modal_score}, sentiment={sentiment_boost}, date={date_boost}")

    if score >= 7:
        priority = "High"
    elif score >= 3:
        priority = "Medium"
    else:
        priority = "Low"
    return {
        "priority": priority,
        "entities": entities,
        "score": score
    }


if __name__ == "__main__":
    test_email = """The deadline for the NLP Project is on Oct 27th,2025. Please patch up all the remaining work and get your code and presentation ready."""
    test_email_2 = """This delay is unacceptable. The client is furious, and we need to resolve it now."""
    test_email_3 = """Fix the server issue immediately and restart all services."""
    test_email_4 = "Resolve this issue immediately! The client is angry about repeated delays."
    test_email_5 = """Just a friendly reminder about our meeting next month. Looking forward to catching up!"""

    print("Priority Detection Test:")
    try:
        result = detect_priority(test_email_5)
        print("\nInput Email:")
        print(f"> {test_email_5}")
        print("\nDetection Result:")
        print(result)
    except Exception as e:
        print(f"\n[ERROR] An exception occurred during execution: {e}")
