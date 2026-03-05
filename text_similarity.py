from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_features(movies_df):

    def build_row_features(row):

        overview = (row.get("overview") or "") * 3

        genre_text = " ".join(
            str(g) for g in row.get("genre_ids", [])
        )
        genre_text = (genre_text + " ") * 2

        language = row.get("language", "")

        combined = f"{overview} {genre_text} {language}"

        return combined

    movies_df["combined_features"] = movies_df.apply(
        build_row_features,
        axis=1
    )

    return movies_df




def build_text_similarity(movies_df):

    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=10000
    )

    tfidf_matrix = tfidf.fit_transform(
        movies_df["combined_features"]
    )

    global cosine_sim
    cosine_sim = cosine_similarity(tfidf_matrix)

    return tfidf, cosine_sim


def get_story_similarities(seed_index):
    if cosine_sim is None:
        return []
    return list(enumerate(cosine_sim[seed_index]))

def get_story_recommendations(
    movies_df,
    cosine_sim,
    movie_title,
    top_n=30,
    language_filter=None
):
    movie_title = movie_title.lower().strip()
    titles = movies_df["title"].str.lower()

    # 1️⃣ Find seed movie safely (numeric index only)
    matched_indices = movies_df.index[titles == movie_title]

    if len(matched_indices) == 0:
        matched_indices = movies_df.index[
            titles.str.contains(movie_title, regex=False)
        ]

    if len(matched_indices) == 0:
        return []

    seed_idx = int(matched_indices[0])
    seed_title = movies_df.loc[seed_idx]["title"]

    # 2️⃣ Get similarity scores
    similarity_scores = list(enumerate(cosine_sim[seed_idx]))

    # 3️⃣ Sort by similarity
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # 4️⃣ Build recommendations
    recommendations = []
    seen_titles = set()

    for i, score in similarity_scores:
        movie = movies_df.iloc[i]

        if movie["title"] == seed_title:
            continue
        if language_filter and movie["language"] != language_filter:
            continue
        if movie["title"] in seen_titles:
            continue

        seen_titles.add(movie["title"])

        recommendations.append({
            "title": movie["title"],
            "overview": movie["overview"],
            "poster_url": movie["poster_url"],
            "rating": movie["rating"],
            "release_date": movie["release_date"],
            "language": movie["language"]
        })

        if len(recommendations) >= top_n:
            break

    return recommendations
