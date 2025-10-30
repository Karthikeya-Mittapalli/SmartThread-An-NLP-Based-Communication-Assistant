import os
import requests # type: ignore
import json
import time
from dotenv import load_dotenv # type: ignore

from src.key_manager import key_manager
from src.priority_detection_flask import detect_priority
from src.text_rank_summarization import textrank_summary
import google.generativeai as genai # type: ignore

# Load environment variables
load_dotenv()



def analyze_email(text: str) -> dict:
    """
    Perform email analysis combining:
    1. LLM-based summarization
    2. NLP-based manual priority detection
    """
    # ---- Step 1: Summarize using LLM ----
    summary = summarize_email(text)

    # ---- Step 2: Manual Priority Detection (NER + Rules) ----
    priority = detect_priority(text)

    # ---- Step 3: Return unified output ----
    return {
        "summary": summary,
        "priority": priority["priority"],
        "entities": priority["entities"]
    }


def summarize_email(text: str) -> str:
    """
    Generate a short summary using Google Gemini API.
    Fallback gracefully to local TextRank summarization if API fails.
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            "You are an assistant that summarizes emails clearly and concisely."
            "Provide the key points and tone of the email in 2 sentences. \n\n"
            f"Email content:\n{text}"
        )
        response = model.generate_content(prompt)
        
        if response and hasattr(response, "text"):
            return response.text.strip()

        print("Gemini response empty, failing back to TextRank.")
        return textrank_summary(text)
    except Exception as e:
        print(f"Gemini API summarization failed: {e}. Falling back to TextRank.")
        return textrank_summary(text)
