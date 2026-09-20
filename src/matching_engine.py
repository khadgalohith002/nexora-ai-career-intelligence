from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(resume_text, job_text):
    """
    Calculate Resume ↔ Job Description similarity
    using TF-IDF and cosine similarity.

    Returns a percentage from 0 to 100.
    """

    if not resume_text or not job_text:
        return 0.0

    documents = [resume_text, job_text]

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), max_features=5000
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        similarity_percentage = similarity * 100

        return round(similarity_percentage, 2)

    except ValueError:

        return 0.0
