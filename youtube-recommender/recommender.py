from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


def recommend(user_query, df, top_n=6):
    df = df.copy()

    # Combine title + description + topic for richer context
    df["content"] = (
        df["title"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["topic"].fillna("")
    )

    all_text = [user_query] + df["content"].tolist()

    # TF-IDF vectorization with bigrams
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=15000
    )
    tfidf_matrix = vectorizer.fit_transform(all_text)

    # Cosine similarity: query vs all videos
    scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    df["score"] = scores

    # Filter out very low relevance
    df = df[df["score"] > 0.01]

    return df.sort_values("score", ascending=False).head(top_n)