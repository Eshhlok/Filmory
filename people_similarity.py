import pandas as pd
from tmdb_client import get_cast_and_director


def get_people_similarities(
    movies_df,
    seed_index,
    mode="cast",
    language_filter=None
):
    seed_movie = movies_df.iloc[seed_index]

    if pd.isna(seed_movie.get("id")):
        return []

    seed_cast, seed_director = get_cast_and_director(seed_movie["id"])
    scored = []

    for idx, row in movies_df.iterrows():
        if idx == seed_index:
            continue

        if pd.isna(row.get("id")):
            continue

        if language_filter and row["language"] != language_filter:
            continue

        cast, director = get_cast_and_director(row["id"])
        score = 0

        if mode == "cast":
            shared_cast = set(seed_cast) & set(cast)

            for actor in shared_cast:
                if seed_cast and actor == seed_cast[0]:  # ⭐ lead actor
                    score += 5
                else:
                    score += 1

        else:  # director mode
            score = len(set(seed_director) & set(director)) * 5

        if score > 0:
            scored.append((
                idx,                 # 👈 IMPORTANT: index, not row
                score,
                row.get("rating", 0)
            ))

    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return scored

# people_similarity.py

import pandas as pd
from tmdb_client import get_cast_and_director


def get_people_recommendations(
    movies_df,
    movie_title,
    top_n=30,
    language_filter=None,
    mode="cast"
):
    movie_title = movie_title.lower().strip()
    titles = movies_df["title"].str.lower()

    # 1️⃣ Find seed movie safely
    matched_indices = movies_df.index[titles == movie_title]

    if len(matched_indices) == 0:
        matched_indices = movies_df.index[
            titles.str.contains(movie_title, regex=False)
        ]

    if len(matched_indices) == 0:
        return []

    seed_idx = int(matched_indices[0])
    seed_movie = movies_df.loc[seed_idx]

    seed_id = seed_movie.get("id")
    if pd.isna(seed_id):
        return []

    # 2️⃣ Get seed people
    seed_cast, seed_director = get_cast_and_director(seed_id)

    recommendations = []
    seen_titles = set()
    scored = []

    # 3️⃣ Score all other movies
    for _, row in movies_df.iterrows():
        if row["title"] == seed_movie["title"]:
            continue
        if language_filter and row["language"] != language_filter:
            continue
        if pd.isna(row.get("id")):
            continue

        cast, director = get_cast_and_director(row["id"])

        score = 0
        if mode == "cast":
            shared_cast = set(seed_cast) & set(cast)
            score = len(shared_cast)
        elif mode == "director":
            score = len(set(seed_director) & set(director)) * 5

        if score > 0:
            scored.append((row, score))

    # 4️⃣ Sort by score
    scored.sort(key=lambda x: x[1], reverse=True)

    # 5️⃣ Build recommendations
    for row, score in scored:
        if row["title"] in seen_titles:
            continue

        seen_titles.add(row["title"])
        recommendations.append({
            "title": row["title"],
            "overview": row["overview"],
            "poster_url": row["poster_url"],
            "rating": row["rating"],
            "release_date": row["release_date"],
            "language": row["language"]
        })

        if len(recommendations) >= top_n:
            break

    return recommendations

