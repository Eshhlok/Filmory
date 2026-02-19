from config import GENRE_MAP
def get_genre_similarities(
    movies_df,
    seed_movie,
    language_filter=None,
    top_n=30
):
    seed_genres = set(seed_movie.get("genre_ids", []))

    if not seed_genres:
        return []

    results = []
    seen_titles = set()

    for _, row in movies_df.iterrows():
        if row["title"] == seed_movie["title"]:
            continue

        if language_filter and row["language"] != language_filter:
            continue

        row_genres = set(row.get("genre_ids", []))
        shared_genres = seed_genres & row_genres

        if shared_genres:
            results.append({
                "row": row,
                "score": len(shared_genres)
            })

    results.sort(
        key=lambda x: (
            x["score"],
            x["row"].get("rating", 0)
        ),
        reverse=True
    )

    recommendations = []
    for item in results:
        row = item["row"]

        if row["title"] in seen_titles:
            continue

        seen_titles.add(row["title"])
        recommendations.append({
            "title": row["title"],
            "overview": row["overview"],
            "poster_url": row["poster_url"],
            "rating": row["rating"],
            "release_date": row["release_date"],
            "language": row["language"],
            "genre_ids": row.get("genre_ids", [])
        })

        if len(recommendations) >= top_n:
            break

    return recommendations
