**Enron Email AI Processing**

This project provides tools to preprocess Enron emails, detect email priority, and summarize email threads using AI models via OpenRouter.

**Setup**

1. Clone the repository

git clone <your-repo-url>
cd <repo-folder>

1. Create and activate a virtual environment

python -m venv venv  
source venv/bin/activate (Linux / Mac)  
venv\\Scripts\\activate (Windows)

1. Install required packages

pip install -r requirements.txt

Minimal requirements.txt for this project includes:

pymongo==4.14.1  
python-dotenv==1.1.1  
requests==2.32.5  
certifi==2025.8.3  
charset-normalizer==3.4.3  
idna==3.10  
urllib3==2.5.0

1. Set your OpenRouter API keys by creating a .env file

OPENROUTER_API_KEY=your_key

**Step 1: Preprocess Emails**

Ensure you have already set up MongoDB with the Enron email dataset (in enron_email/mails).

Preprocess raw emails in MongoDB and generate clean_message, from, and to fields.

1. Run pre-processing.py
2. Make sure to update the ObjectId in the code to the email you want to preprocess. For example, replace the ObjectId in:

email = emails_col.find_one({"\_id": ObjectId("6892fe052589ce0138d7759f")})

**Step 2: Priority Detection**

Classify preprocessed emails into High, Medium, or Low priority using OpenRouter.

1. Run priority_detection.py
2. Update the ObjectId in the code to the email you want to classify:

sample_email_id = "6892fe052589ce0138d7759f"  
process_email_by_id(sample_email_id)

**Step 3: Thread Summarization**

Summarize a list of emails in a conversation thread.

1. Run thread_summarization.py
2. Provide the thread as a list of messages with sender, role, timestamp, and text. Example:

sample_thread = \[  
{"sender": "Bob", "role": "Engineer", "timestamp": "2025-08-19 09:12", "text": "..."},  
{"sender": "Charlie", "role": "Analyst", "timestamp": "2025-08-19 09:30", "text": "..."}  
\]  
summary = summarize_thread(sample_thread)  
print(summary)

**Optional: Batch Processing**

Instead of manually changing ObjectIds, you can process all emails without priority:

for email_doc in emails_col.find({"priority": {"$exists": False}}):  
process_email_by_id(email_doc\["\_id"\])

**Workflow Summary**

1. Run pre-processing.py → adds clean_message, sender, recipient info
2. Run priority_detection.py → adds priority field (High/Medium/Low)
3. Optionally, run thread_summarization.py for email threads
4. Repeat for additional emails as needed
