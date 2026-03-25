from text_similarity import get_story_recommendations, build_text_similarity, build_features
from people_similarity import get_people_recommendations
from genre_similarity import get_genre_similarities
from tmdb_client import search_movies_tmdb
import pandas as pd


def _get_tmdb_metadata(movie_title: str) -> dict | None:
    """
    Fetch genre_ids, overview and original_language for a movie from TMDB.
    Returns None if not found.
    """
    results = search_movies_tmdb(movie_title)
    if not results:
        return None

    # Pick the best match — exact title match preferred
    movie_title_lower = movie_title.lower().strip()
    for r in results:
        if r.get("title", "").lower().strip() == movie_title_lower:
            return {
                "genre_ids": r.get("genre_ids", []),
                "overview":  r.get("overview", ""),
                "language":  r.get("original_language", "")
            }

    # Fall back to first result
    r = results[0]
    return {
        "genre_ids": r.get("genre_ids", []),
        "overview":  r.get("overview", ""),
        "language":  r.get("original_language", "")
    }


def _fallback_recommend(
    movies_df: pd.DataFrame,
    cosine_sim,
    movie_title: str,
    top_n: int = 30
) -> list[dict]:
    """
    Called when the movie is not found in local DB.

    Strategy:
      1. Fetch genre + plot from TMDB
      2. Score all DB movies by:
           - Genre overlap (weighted 2x)
           - TF-IDF cosine similarity against the TMDB overview (weighted 1x)
      3. Return same-language results first, then others, sorted by score
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

    # ── Genre scores ──────────────────────────────────────────────────
    genre_scores: dict[int, float] = {}
    for idx, row in movies_df.iterrows():
        row_genres = set(row.get("genre_ids", []))
        shared = seed_genres & row_genres
        if shared:
            genre_scores[idx] = len(shared) * 2   # weight 2x

    # ── Story / TF-IDF scores ─────────────────────────────────────────
    story_scores: dict[int, float] = {}
    if seed_overview.strip():
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = list(movies_df["combined_features"]) + [seed_overview]
        tfidf  = TfidfVectorizer(stop_words="english", max_features=10000)
        matrix = tfidf.fit_transform(corpus)

        seed_vec  = matrix[-1]                      # last row = seed overview
        db_matrix = matrix[:-1]
        sims      = cosine_similarity(seed_vec, db_matrix).flatten()

        for idx, score in enumerate(sims):
            if score > 0.01:                         # ignore noise
                story_scores[idx] = float(score)    # weight 1x

    # ── Combine scores ────────────────────────────────────────────────
    all_indices = set(genre_scores) | set(story_scores)
    combined: list[tuple[int, float]] = []

    for idx in all_indices:
        total = genre_scores.get(idx, 0) + story_scores.get(idx, 0)
        combined.append((idx, total))

    combined.sort(key=lambda x: x[1], reverse=True)

    # ── Build results: same language first, then others ───────────────
    same_lang   = []
    other_lang  = []
    seen_titles = set()

    for idx, score in combined:
        row = movies_df.iloc[idx]
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

    results = same_lang + other_lang
    return results[:top_n]


def recommend(
    movies_df: pd.DataFrame,
    cosine_sim,
    movie_title: str,
    top_n: int = 30,
    language_filter: str | None = None,
    mode: str = "story"
) -> list[dict]:
    """
    Main recommendation entry point.

    Flow:
      1. Try to find the movie in the local DB
      2. If found → use the requested mode (story / cast / director / genre)
      3. If NOT found → fallback using TMDB metadata (genre + plot),
         same language first then others
    """
    titles      = movies_df["title"].str.lower()
    title_lower = movie_title.lower().strip()

    # ── Check if movie exists in DB ───────────────────────────────────
    matches = movies_df[titles == title_lower]
    if matches.empty:
        matches = movies_df[titles.str.contains(title_lower, regex=False)]

    # ── Movie NOT in DB → fallback ────────────────────────────────────
    if matches.empty:
        results = _fallback_recommend(movies_df, cosine_sim, movie_title, top_n)

        # Apply language filter on top of fallback if user selected one
        if language_filter:
            results = [r for r in results if r["language"] == language_filter]

        return results

    # ── Movie found in DB → normal recommendation ─────────────────────
    seed_movie = matches.iloc[0]

    if mode == "story":
        return get_story_recommendations(
            movies_df,
            cosine_sim,
            movie_title,
            top_n,
            language_filter
        )

    elif mode in ("cast", "director"):
        return get_people_recommendations(
            movies_df,
            movie_title,
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