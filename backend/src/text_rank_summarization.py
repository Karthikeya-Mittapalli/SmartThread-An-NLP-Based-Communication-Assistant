import numpy as np
import networkx as nx

from src.nltk_downloader import ensure_nltk_data
ensure_nltk_data()

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import re

def textrank_summary(raw_text, num_sentences=3):
    """
    Performs extractive summarization using the TextRank algorithm.

    Args:
        raw_text (str): The email text to be summarized.
        num_sentences (int): The number of sentences desired in the summary.

    Returns:
        str: The generated summary.
    """
    # 1. Tokenize text into sentences
    sentences = sent_tokenize(raw_text)
    if len(sentences) <= num_sentences:
        return raw_text # Return original text if it's short

    # 2. Pre-process sentences: clean and tokenize into words
    stop_words = set(stopwords.words('english'))
    clean_sentences = []
    for sentence in sentences:
        # Remove punctuation and convert to lower case
        clean = re.sub(r'[^\w\s]', '', sentence).lower()
        words = [word for word in word_tokenize(clean) if word not in stop_words]
        clean_sentences.append(words)

    # 3. Create the similarity matrix
    num_sents = len(sentences)
    similarity_matrix = np.zeros((num_sents, num_sents))

    for i in range(num_sents):
        for j in range(num_sents):
            if i == j:  # Sentences can't be similar to themselves in this context
                continue
            
            # Calculate similarity based on common words
            words_i = set(clean_sentences[i])
            words_j = set(clean_sentences[j])
            
            if len(words_i) == 0 or len(words_j) == 0:
                similarity_matrix[i][j] = 0
            else:
                # Jaccard similarity
                similarity = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                similarity_matrix[i][j] = similarity

    # 4. Create a graph from the similarity matrix
    graph = nx.from_numpy_array(similarity_matrix)

    # 5. Apply the PageRank algorithm to the graph
    # This gives a score to each sentence (node)
    scores = nx.pagerank(graph)

    # 6. Rank sentences by their score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    # 7. Extract the top N sentences
    top_sentences = []
    for i in range(min(num_sentences, len(ranked_sentences))):
        top_sentences.append(ranked_sentences[i][1])
        
    # 8. Re-order sentences to their original sequence and join
    summary = ' '.join(sorted(top_sentences, key=lambda s: raw_text.find(s)))

    return summary
