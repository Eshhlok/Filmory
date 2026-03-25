import pandas as pd
from data_store import load_credits


def get_people_recommendations(
    movies_df: pd.DataFrame,
    movie_title: str,
    top_n: int = 30,
    language_filter: str | None = None,
    mode: str = "cast"
) -> list[dict]:
    """
    Recommend movies based on shared cast or director.
    Reads from the SQLite credits cache — no live TMDB API calls.

    Scoring (cast mode):
      - Top billed actor match  → 10 points  ⭐ (from TMDB billing order)
      - 2nd billed actor match  →  6 points
      - 3rd billed actor match  →  4 points
      - Any other cast match    →  1 point each

    Scoring (director mode):
      - Each shared director    → 10 points

    Results sorted by: score first, then rating.
    """

    # ── Load credits cache from SQLite ────────────────────────────────
    credits_cache = load_credits()

    if not credits_cache:
        print("⚠️  Credits cache is empty. Run cache_all_credits() in backend.py first.")
        return []

    # ── Find seed movie ───────────────────────────────────────────────
    title_lower = movie_title.lower().strip()
    titles      = movies_df["title"].str.lower()

    matched = movies_df.index[titles == title_lower]
    if len(matched) == 0:
        matched = movies_df.index[titles.str.contains(title_lower, regex=False)]
    if len(matched) == 0:
        return []

    seed_idx   = int(matched[0])
    seed_movie = movies_df.loc[seed_idx]
    seed_id    = int(seed_movie["id"])

    seed_credits = credits_cache.get(seed_id)
    if not seed_credits:
        print(f"⚠️  No credits found for '{seed_movie['title']}' (id={seed_id})")
        return []

    seed_cast      = seed_credits["full_cast"]
    seed_directors = set(seed_credits["directors"])

    if mode == "cast" and not seed_cast:
        return []
    if mode == "director" and not seed_directors:
        print(f"⚠️  No director found for '{seed_movie['title']}'")
        return []

    # ── Build cast weight map for seed movie ──────────────────────────
    # Based on billing order: index 0 = top billed = lead actor
    cast_weights: dict[str, int] = {}
    if mode == "cast":
        for i, actor in enumerate(seed_cast):
            if i == 0:
                cast_weights[actor] = 10   # top billed / lead
            elif i == 1:
                cast_weights[actor] = 6    # 2nd billed
            elif i == 2:
                cast_weights[actor] = 4    # 3rd billed
            else:
                cast_weights[actor] = 1    # supporting

    # ── Score every other movie from cache ────────────────────────────
    scored: list[tuple[pd.Series, float, float]] = []

    for _, row in movies_df.iterrows():
        if row["title"] == seed_movie["title"]:
            continue
        if language_filter and row["language"] != language_filter:
            continue

        movie_id = int(row["id"])
        movie_credits = credits_cache.get(movie_id)
        if not movie_credits:
            continue

        score = 0.0

        if mode == "cast":
            for actor in movie_credits["full_cast"]:
                if actor in cast_weights:
                    score += cast_weights[actor]

        elif mode == "director":
            shared = seed_directors & set(movie_credits["directors"])
            score  = len(shared) * 10.0

        if score > 0:
            scored.append((row, score, row.get("rating") or 0))

    # ── Sort: score first, then rating ───────────────────────────────
    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # ── Build output ──────────────────────────────────────────────────
    recommendations = []
    seen_titles     = set()

    for row, score, rating in scored:
        title = row["title"]
        if title in seen_titles:
            continue
        seen_titles.add(title)

        recommendations.append({
            "title":        title,
            "overview":     row["overview"],
            "poster_url":   row["poster_url"],
            "rating":       rating,
            "release_date": row["release_date"],
            "language":     row["language"],
            "genre_ids":    row.get("genre_ids", [])
        })

        if len(recommendations) >= top_n:
            break

    return recommendations