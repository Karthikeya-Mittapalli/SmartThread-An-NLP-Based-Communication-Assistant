import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ Please set GEMINI_API_KEY in your .env file")

# --- Configure Gemini API ---
genai.configure(api_key=API_KEY)


def suggest_reply(summary_data: dict, model="gemini-2.0-flash"):
    """
    Generate a smart reply suggestion based on summary data.
    summary_data should be a dict with keys:
    - Decisions
    - Action Items
    - Deadlines
    - Urgency
    - Open Issues
    """

    prompt = f"""
    You are a helpful assistant that suggests smart replies based on conversation summaries.

    Here is the summary of the conversation:
    - Decisions: {summary_data.get("Decisions", "None")}
    - Action Items: {summary_data.get("Action Items", "None")}
    - Deadlines: {summary_data.get("Deadlines", "None")}
    - Urgency: {summary_data.get("Urgency", "None")}
    - Open Issues: {summary_data.get("Open Issues", "None")}

    Based on this, suggest a short, professional reply that acknowledges the decisions,
    confirms the action items, and sets expectations clearly.
    """

    response = genai.GenerativeModel(model).generate_content(prompt)
    return response.text.strip()


# --- Example Run ---
if __name__ == "__main__":
    summary_example = {
        "Decisions": "Finalize Q3 report today.",
        "Action Items": "Charlie to add sales data; team to send completed version to Alice.",
        "Deadlines": "Sales data by 2 PM; final report by 5 PM today.",
        "Urgency": "High",
        "Open Issues": "None"
    }

    reply = suggest_reply(summary_example)
    print("\n💡 Suggested Reply:\n", reply)
