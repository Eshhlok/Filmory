from text_similarity import get_story_recommendations
from people_similarity import get_people_recommendations
from genre_similarity import get_genre_similarities

def recommend(
    movies_df,
    cosine_sim,
    movie_title,
    top_n=30,
    language_filter=None,
    mode="story"
):
    titles = movies_df["title"].str.lower()
    movie_title = movie_title.lower().strip()

    matches = movies_df[titles == movie_title]

    if matches.empty:
        matches = movies_df[titles.str.contains(movie_title, regex=False)]

    if matches.empty:
        return []

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
        raise ValueError("Unknown recommendation mode")
