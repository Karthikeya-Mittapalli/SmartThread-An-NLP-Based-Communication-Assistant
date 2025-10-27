import heapq
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def extractive_email_summary(raw_text, num_sentences=3):
    """
    Performs extractive summarization on a given text.

    Args:
        raw_text (str): The email text to be summarized.
        num_sentences (int): The number of sentences desired in the summary.

    Returns:
        str: The generated summary.
    """
    # 1. Tokenize text into words and get English stop words
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(raw_text.lower())

    # 2. Calculate word frequencies, ignoring stop words and punctuation
    word_frequencies = {}
    for word in words:
        if word.isalnum() and word not in stop_words:
            if word not in word_frequencies:
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
    
    # Get the frequency of the most common word
    if not word_frequencies:
        return "Cannot summarize empty or stop-word-only text."
    max_frequency = max(word_frequencies.values())

    # 3. Normalize frequencies (from 0 to 1)
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / max_frequency)

    # 4. Tokenize the original text into sentences
    sentences = sent_tokenize(raw_text)

    # 5. Score sentences based on the frequency of words they contain
    sentence_scores = {}
    for sent in sentences:
        # Tokenize the sentence into words
        sentence_words = word_tokenize(sent.lower())
        for word in sentence_words:
            if word in word_frequencies:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]
    
    # 6. Find the N sentences with the highest scores
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)

    # 7. Join the sentences to form the final summary
    summary = ' '.join(summary_sentences)
    return summary

# --- Example Usage ---

# Sample Email Text 📧
sample_email = """
Subject: Urgent: Q4 Project Phoenix Update and Final Review Meeting

Hi Team,

I hope this email finds you well.

This is a critical update regarding the final stages of Project Phoenix for Q4. The project deadline is fast approaching, and we need to ensure all components are finalized and tested before the client presentation next Friday. The successful completion of Project Phoenix is our top priority for this quarter.

I have scheduled a final review meeting for this Wednesday, October 29th, at 10:00 AM in Conference Room 3. Attendance is mandatory for all key stakeholders. During this meeting, we will go over the final deployment checklist, address any last-minute blockers, and assign roles for the presentation day. Please come prepared with your team's progress reports and a list of any outstanding issues.

The marketing team has already prepared the initial draft of the launch announcement. They require our final feature list by the end of Wednesday's meeting to proceed. Let's make sure we provide them with accurate information.

Thank you for your hard work and dedication to Project Phoenix. Let's push through this final week and deliver an exceptional product.

Best regards,

Alex
Project Manager
"""

# Generate the summary
summary = extractive_email_summary(sample_email, num_sentences=3)

# Print the results ✨
print("--- ORIGINAL EMAIL ---")
print(sample_email)
print(f"\nOriginal Length (chars): {len(sample_email)}")
print("\n" + "="*30 + "\n")
print("--- GENERATED SUMMARY ---")
print(summary)
print(f"\nSummary Length (chars): {len(summary)}")