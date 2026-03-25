import pandas as pd
from tmdb_client import get_cast_and_director


def get_people_recommendations(
    movies_df: pd.DataFrame,
    movie_title: str,
    top_n: int = 30,
    language_filter: str | None = None,
    mode: str = "cast"
) -> list[dict]:
    """
    Recommend movies based on shared cast or director.

    Scoring (cast mode):
      - Lead actor match (index 0)  → 10 points  ⭐ highest weight
      - 2nd actor match (index 1)   → 6 points
      - 3rd actor match (index 2)   → 4 points
      - Any other cast match        → 1 point each

    Scoring (director mode):
      - Each shared director        → 10 points

    Results sorted by: score first, then rating.
    """

    movie_title_lower = movie_title.lower().strip()
    titles = movies_df["title"].str.lower()

    # ── Find seed movie ───────────────────────────────────────────────
    matched = movies_df.index[titles == movie_title_lower]
    if len(matched) == 0:
        matched = movies_df.index[
            titles.str.contains(movie_title_lower, regex=False)
        ]
    if len(matched) == 0:
        return []

    seed_idx   = int(matched[0])
    seed_movie = movies_df.loc[seed_idx]
    seed_id    = seed_movie.get("id")

    if pd.isna(seed_id):
        return []

    # ── Fetch seed cast / director ────────────────────────────────────
    seed_cast, seed_director = get_cast_and_director(seed_id)

    if mode == "cast" and not seed_cast:
        return []
    if mode == "director" and not seed_director:
        return []

    # Pre-build lead actor weights for cast mode
    # { actor_name: points }
    cast_weights: dict[str, int] = {}
    if mode == "cast":
        for i, actor in enumerate(seed_cast):
            if i == 0:
                cast_weights[actor] = 10   # lead actor
            elif i == 1:
                cast_weights[actor] = 6    # 2nd billed
            elif i == 2:
                cast_weights[actor] = 4    # 3rd billed
            else:
                cast_weights[actor] = 1    # supporting

    seed_directors = set(seed_director)

    # ── Score every other movie ───────────────────────────────────────
    scored: list[tuple[dict, float, float]] = []  # (entry, score, rating)

    for _, row in movies_df.iterrows():
        if row["title"] == seed_movie["title"]:
            continue
        if pd.isna(row.get("id")):
            continue
        if language_filter and row["language"] != language_filter:
            continue

        cast, director = get_cast_and_director(row["id"])
        score = 0.0

        if mode == "cast":
            for actor in cast:
                if actor in cast_weights:
                    score += cast_weights[actor]

        elif mode == "director":
            shared_directors = seed_directors & set(director)
            score = len(shared_directors) * 10.0

        if score > 0:
            scored.append((row, score, row.get("rating") or 0))

    # ── Sort: score first, then rating ───────────────────────────────
    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # ── Build recommendations ─────────────────────────────────────────
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