from text_similarity import get_story_recommendations
from people_similarity import get_people_recommendations

def recommend(
    movies_df,
    cosine_sim,
    movie_title,
    top_n=30,
    language_filter=None,
    mode="story"
):
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

    else:
        raise ValueError("Unknown recommendation mode")
