import pandas as pd
from text_similarity import get_story_recommendations
from people_similarity import get_people_recommendations, _find_seed_movie
from genre_similarity import get_genre_similarities
from tmdb_client import search_movies_tmdb


def _get_tmdb_metadata(movie_title: str) -> dict | None:
    """Fetch genre_ids, overview and language for a movie from TMDB."""
    results = search_movies_tmdb(movie_title)
    if not results:
        return None

    movie_title_lower = movie_title.lower().strip()
    for r in results:
        if r.get("title", "").lower().strip() == movie_title_lower:
            return {
                "genre_ids": r.get("genre_ids", []),
                "overview":  r.get("overview", ""),
                "language":  r.get("original_language", "")
            }

    r = results[0]
    return {
        "genre_ids": r.get("genre_ids", []),
        "overview":  r.get("overview", ""),
        "language":  r.get("original_language", "")
    }


def _fallback_recommend(
    movies_df: pd.DataFrame,
    tfidf_matrix,           # ✅ sparse matrix
    movie_title: str,
    top_n: int = 30
) -> list[dict]:
    """
    Called when movie is not found in DB.
    Uses TMDB genre + plot to find similar movies, same language first.
    """
    print(f"⚠️  '{movie_title}' not found in DB. Fetching metadata from TMDB for fallback...")
    metadata = _get_tmdb_metadata(movie_title)

    if not metadata:
        print("❌ Could not fetch metadata from TMDB either.")
        return []

    seed_genres   = set(metadata["genre_ids"])
    seed_overview = metadata["overview"]
    seed_language = metadata["language"]

    print(f"   → Genres: {seed_genres}, Language: {seed_language}")

    # Genre scores
    genre_scores: dict[int, float] = {}
    for idx, row in movies_df.iterrows():
        row_genres = set(row.get("genre_ids", []))
        shared = seed_genres & row_genres
        if shared:
            genre_scores[idx] = len(shared) * 2

    # TF-IDF story scores — compute on demand against TMDB overview
    story_scores: dict[int, float] = {}
    if seed_overview.strip():
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = list(movies_df["combined_features"]) + [seed_overview]
        tfidf  = TfidfVectorizer(stop_words="english", max_features=10000)
        matrix = tfidf.fit_transform(corpus)

        seed_vec  = matrix[-1]
        db_matrix = matrix[:-1]
        sims      = cosine_similarity(seed_vec, db_matrix).flatten()

        for idx, score in enumerate(sims):
            if score > 0.01:
                story_scores[idx] = float(score)

    # Combine
    all_indices = set(genre_scores) | set(story_scores)
    combined    = sorted(
        [(idx, genre_scores.get(idx, 0) + story_scores.get(idx, 0)) for idx in all_indices],
        key=lambda x: x[1],
        reverse=True
    )

    # Same language first
    same_lang   = []
    other_lang  = []
    seen_titles = set()

    for idx, score in combined:
        row   = movies_df.iloc[idx]
        title = row["title"]

        if title in seen_titles:
            continue
        seen_titles.add(title)

        entry = {
            "title":        title,
            "overview":     row["overview"],
            "poster_url":   row["poster_url"],
            "rating":       row["rating"],
            "release_date": row["release_date"],
            "language":     row["language"],
            "genre_ids":    row.get("genre_ids", [])
        }

        if row["language"] == seed_language:
            same_lang.append(entry)
        else:
            other_lang.append(entry)

        if len(same_lang) + len(other_lang) >= top_n * 2:
            break

    return (same_lang + other_lang)[:top_n]


def recommend(
    movies_df: pd.DataFrame,
    tfidf_matrix,           # ✅ sparse matrix instead of cosine_sim
    movie_title: str,
    top_n: int = 30,
    language_filter: str | None = None,
    mode: str = "story"
) -> list[dict]:
    """
    Main recommendation entry point.

    Flow:
      1. Smart 4-step lookup via _find_seed_movie()
      2. If found → route to correct mode
      3. If NOT found → TMDB metadata fallback
    """

    # Smart lookup — handles regional titles
    seed_idx, seed_movie = _find_seed_movie(movies_df, movie_title)

    # Not in DB → fallback
    if seed_idx is None:
        results = _fallback_recommend(movies_df, tfidf_matrix, movie_title, top_n)
        if language_filter:
            results = [r for r in results if r["language"] == language_filter]
        return results

    # Found → use actual DB title for downstream lookups
    db_title = seed_movie["title"]

    if mode == "story":
        return get_story_recommendations(
            movies_df,
            tfidf_matrix,   # ✅ sparse matrix
            db_title,
            top_n,
            language_filter
        )

    elif mode in ("cast", "director"):
        return get_people_recommendations(
            movies_df,
            db_title,
            top_n,
            language_filter,
            mode
        )

    elif mode == "genre":
        return get_genre_similarities(
            movies_df=movies_df,
            seed_movie=seed_movie,
            language_filter=language_filter,
            top_n=top_n
        )

    else:
        raise ValueError(f"Unknown recommendation mode: {mode}")