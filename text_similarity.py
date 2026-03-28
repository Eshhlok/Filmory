from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import spmatrix
import pandas as pd
import numpy as np


def build_features(movies_df: pd.DataFrame) -> pd.DataFrame:
    """Build combined_features column for TF-IDF."""

    def build_row_features(row):
        overview   = (row.get("overview") or "") * 3
        genre_text = " ".join(str(g) for g in row.get("genre_ids", []))
        genre_text = (genre_text + " ") * 2
        language   = row.get("language", "")
        return f"{overview} {genre_text} {language}"

    movies_df["combined_features"] = movies_df.apply(build_row_features, axis=1)
    return movies_df


def build_text_similarity(movies_df: pd.DataFrame):
    """
    Build TF-IDF matrix only — no cosine similarity matrix stored.
    Returns (tfidf_vectorizer, tfidf_matrix_sparse)

    Memory comparison:
      Old: 8000×8000 float64 dense matrix  = ~512 MB
      New: 8000×10000 sparse TF-IDF matrix = ~5–10 MB
    """
    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=10000
    )

    tfidf_matrix = tfidf.fit_transform(movies_df["combined_features"])
    print(f"✅ TF-IDF matrix built: {tfidf_matrix.shape} | "
          f"nnz={tfidf_matrix.nnz} | "
          f"~{tfidf_matrix.data.nbytes / 1024 / 1024:.1f} MB")

    return tfidf, tfidf_matrix


def get_story_recommendations(
    movies_df: pd.DataFrame,
    tfidf_matrix,           # sparse matrix — NOT cosine_sim anymore
    movie_title: str,
    top_n: int = 30,
    language_filter: str | None = None
) -> list[dict]:
    """
    Compute cosine similarity ON DEMAND for just the seed movie row.
    ~50ms for 8000 movies — imperceptible to users.
    """
    movie_title_lower = movie_title.lower().strip()
    titles = movies_df["title"].str.lower()

    # Find seed movie
    matched = movies_df.index[titles == movie_title_lower]
    if len(matched) == 0:
        matched = movies_df.index[
            titles.str.contains(movie_title_lower, regex=False, na=False)
        ]
    if len(matched) == 0:
        return []

    seed_idx   = int(matched[0])
    seed_title = movies_df.loc[seed_idx]["title"]

    # ✅ Compute similarity for seed row only — 1 × N instead of N × N
    seed_vec   = tfidf_matrix[seed_idx]
    sim_scores = cosine_similarity(seed_vec, tfidf_matrix).flatten()

    # Sort by similarity descending
    similar_indices = np.argsort(sim_scores)[::-1]

    recommendations = []
    seen_titles     = set()

    for idx in similar_indices:
        movie = movies_df.iloc[idx]

        if movie["title"] == seed_title:
            continue
        if language_filter and movie["language"] != language_filter:
            continue
        if movie["title"] in seen_titles:
            continue

        seen_titles.add(movie["title"])
        recommendations.append({
            "title":        movie["title"],
            "overview":     movie["overview"],
            "poster_url":   movie["poster_url"],
            "rating":       movie["rating"],
            "release_date": movie["release_date"],
            "language":     movie["language"],
            "genre_ids":    movie.get("genre_ids", [])
        })

        if len(recommendations) >= top_n:
            break

    return recommendations