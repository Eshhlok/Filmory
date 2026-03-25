import pandas as pd
from data_store import load_credits


def _find_seed_movie(movies_df: pd.DataFrame, movie_title: str):
    """
    Find seed movie in DB using a 4-step strategy:

      1. Exact title match (case-insensitive)
      2. Partial title match
      3. TMDB search → match by TMDB movie ID in DB
      4. TMDB search → match by TMDB result's original_title in DB
         (handles regional titles like दंगल stored under a different TMDB ID)

    Returns (seed_idx, seed_movie) or (None, None) if not found.
    """
    title_lower = movie_title.lower().strip()
    titles      = movies_df["title"].str.lower()

    # ── 1. Exact match ────────────────────────────────────────────────
    matched = movies_df.index[titles == title_lower]
    if len(matched) > 0:
        idx = int(matched[0])
        return idx, movies_df.loc[idx]

    # ── 2. Partial match ──────────────────────────────────────────────
    matched = movies_df.index[titles.str.contains(title_lower, regex=False)]
    if len(matched) > 0:
        idx = int(matched[0])
        return idx, movies_df.loc[idx]

    # ── 3 & 4. TMDB search fallback ───────────────────────────────────
    try:
        from tmdb_client import search_movies_tmdb
        print(f"🔍 '{movie_title}' not found locally. Searching TMDB...")

        results = search_movies_tmdb(movie_title)
        if not results:
            return None, None

        db_ids = set(movies_df["id"].astype(int))

        for result in results:
            tmdb_id        = result.get("id")
            tmdb_title     = (result.get("title") or "").lower().strip()
            tmdb_orig      = (result.get("original_title") or "").lower().strip()

            # Step 3: match by TMDB ID
            if tmdb_id and int(tmdb_id) in db_ids:
                matched = movies_df.index[
                    movies_df["id"].astype(int) == int(tmdb_id)
                ]
                if len(matched) > 0:
                    idx = int(matched[0])
                    print(f"✅ Matched via TMDB ID: '{movies_df.loc[idx]['title']}'")
                    return idx, movies_df.loc[idx]

            # Step 4: match by original_title stored in DB
            # e.g. TMDB returns original_title="दंगल" → find that in DB titles
            if tmdb_orig:
                matched = movies_df.index[titles == tmdb_orig]
                if len(matched) > 0:
                    idx = int(matched[0])
                    print(f"✅ Matched via original title: '{movies_df.loc[idx]['title']}'")
                    return idx, movies_df.loc[idx]

            # Also try matching TMDB english title against DB
            if tmdb_title:
                matched = movies_df.index[titles == tmdb_title]
                if len(matched) > 0:
                    idx = int(matched[0])
                    print(f"✅ Matched via TMDB title: '{movies_df.loc[idx]['title']}'")
                    return idx, movies_df.loc[idx]

    except Exception as e:
        print(f"⚠️  TMDB fallback search failed: {e}")

    return None, None


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
      - Top 2 billed actors     → 10 points each  ⭐ both leads equally weighted
      - 3rd billed actor        →  4 points
      - Any other cast match    →  1 point each

    Scoring (director mode):
      - Each shared director    → 10 points

    Sorting: score ONLY. Rating is completely ignored for ordering.
    Within same score, order is stable (preserves DB order).
    """

    # ── Load credits cache ────────────────────────────────────────────
    credits_cache = load_credits()
    if not credits_cache:
        print("⚠️  Credits cache is empty. Run cache_all_credits() in backend.py first.")
        return []

    # ── Find seed movie ───────────────────────────────────────────────
    seed_idx, seed_movie = _find_seed_movie(movies_df, movie_title)
    if seed_idx is None:
        return []

    seed_id      = int(seed_movie["id"])
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

    # ── Build cast weight map ─────────────────────────────────────────
    cast_weights: dict[str, int] = {}
    if mode == "cast":
        for i, actor in enumerate(seed_cast):
            if i <= 1:
                cast_weights[actor] = 10   # ⭐ top 2 leads equally weighted
            elif i == 2:
                cast_weights[actor] = 4    # 3rd billed
            else:
                cast_weights[actor] = 1    # supporting

    # ── Score every other movie ───────────────────────────────────────
    scored: list[tuple[pd.Series, float]] = []   # (row, score) — no rating

    for _, row in movies_df.iterrows():
        if row["title"] == seed_movie["title"]:
            continue
        if language_filter and row["language"] != language_filter:
            continue

        movie_id      = int(row["id"])
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
            scored.append((row, score))

    # ── Sort by score ONLY — rating plays no role ─────────────────────
    scored.sort(key=lambda x: x[1], reverse=True)

    # ── Build output ──────────────────────────────────────────────────
    recommendations = []
    seen_titles     = set()

    for row, score in scored:
        title = row["title"]
        if title in seen_titles:
            continue
        seen_titles.add(title)

        recommendations.append({
            "title":        title,
            "overview":     row["overview"],
            "poster_url":   row["poster_url"],
            "rating":       float(row.get("rating") or 0),
            "release_date": row["release_date"],
            "language":     row["language"],
            "genre_ids":    row.get("genre_ids", [])
        })

        if len(recommendations) >= top_n:
            break

    return recommendations