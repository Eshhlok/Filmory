import streamlit as st
from backend import recommend,search_movies_tmdb

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "ko": "Korean",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese",
    "tl": "Tagalog",
    "it": "Italian",
    "ru": "Russian",
    "pt": "Portuguese",
    "ar": "Arabic",
    "tr": "Turkish",
    "sv": "Swedish",
    "nl": "Dutch",
    "pl": "Polish",
    "id": "Indonesian",
    "vi": "Vietnamese",
    "fa": "Persian",
    "he": "Hebrew",
    "cs": "Czech",
    "ro": "Romanian",
    "da": "Danish",
    "fi": "Finnish",
    "no": "Norwegian",
    "hu": "Hungarian",
    "el": "Greek",
    "bg": "Bulgarian",
    "uk": "Ukrainian",
    "sr": "Serbian",
    "hr": "Croatian",
    "sk": "Slovak",
    "lt": "Lithuanian",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "ml": "Malayalam",
    "bn": "Bengali",
    "mr": "Marathi",
    "pa": "Punjabi",
    "th": "Thai",
    "kn": "Kannada"
}

st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommendation System")
st.write("Find movies similar to your favorite one!")

if "search_page" not in st.session_state:
    st.session_state.search_page = 1

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "display_count" not in st.session_state:
    st.session_state.display_count = 5

if "rec_display_count" not in st.session_state:
    st.session_state.rec_display_count = 5

if "all_recommendations" not in st.session_state:
    st.session_state.all_recommendations = []

# User input
movie_name = st.text_input(
    "🔍 Search for a movie",
    placeholder="Type a movie name (e.g. Interstellar, Conjuring, URI)"
)

if movie_name != st.session_state.last_query:
    st.session_state.search_page = 1
    st.session_state.search_results = []
    st.session_state.display_count = 5
    st.session_state.last_query = movie_name


# ======================
# SEARCH RESULTS STAGE
# ======================
if movie_name.strip():
    new_results = search_movies_tmdb(
        movie_name,
        page=st.session_state.search_page
    )

    # append new results (avoid duplicates)
    existing_ids = {m["id"] for m in st.session_state.search_results}
    for movie in new_results:
        if movie["id"] not in existing_ids:
            st.session_state.search_results.append(movie)

    if st.session_state.search_results:
        st.caption("Select the movie you meant:")

        cols = st.columns(5)
        for idx, movie in enumerate(st.session_state.search_results[:st.session_state.display_count]):
            with cols[idx % 5]:
                if movie.get("poster_path"):
                    st.image(
                        "https://image.tmdb.org/t/p/w300" + movie["poster_path"],
                        use_container_width=True
                    )
                else:
                    st.write("No Image")

                if st.button(
                    movie["title"],
                    key=f"select_{movie['id']}"
                ):
                    st.session_state.selected_movie = movie["title"]
                    st.session_state.rec_display_count = 5
                    st.session_state.all_recommendations = recommend(movie["title"])


        # LOAD MORE BUTTON
        left, center, right = st.columns([3, 2, 3])

        with center:
            if st.button("Load more", use_container_width=True):
                if st.session_state.display_count < len(st.session_state.search_results):
                    st.session_state.display_count += 5
                else:
                    st.session_state.search_page += 1

                st.rerun()

# ======================
# RECOMMENDATION STAGE
# ======================

if "selected_movie" in st.session_state:
    selected_movie_title = st.session_state.selected_movie
    st.subheader(f"Recommendations based on: **{selected_movie_title}**")

    # 🔽 Language filter
    filter_option = st.selectbox(
        "Filter by language",
        options=["All"] + list(LANGUAGE_MAP.values())
    )

    if "last_filter_option" not in st.session_state:
        st.session_state.last_filter_option = "All"

    results = st.session_state.all_recommendations

    if filter_option != st.session_state.last_filter_option:
        st.session_state.last_filter_option = filter_option

        if filter_option == "All":
            st.session_state.all_recommendations = recommend(
                selected_movie_title
            )
        else:
            selected_lang_code = next(
                (k for k, v in LANGUAGE_MAP.items() if v == filter_option),
                None
            )
            st.session_state.all_recommendations = recommend(
                selected_movie_title,
                language_filter=selected_lang_code
            )

        st.session_state.rec_display_count = 5  # 🔑 reset ONLY on change

    results = st.session_state.all_recommendations

    if not results:
        st.info("No close matches found.")
    else:
        for movie in results[:st.session_state.rec_display_count]:
            col1, col2 = st.columns([1, 3])

            with col1:
                if movie["poster_url"]:
                    st.image(movie["poster_url"], use_container_width=True)
                else:
                    st.write("No Image")

            with col2:
                st.markdown(f"### {movie['title']}")
                st.write(f"⭐ Rating: {movie['rating']}")
                st.write(f"📅 Release Date: {movie['release_date']}")
                lang_code = movie.get("language", "N/A")
                lang_name = LANGUAGE_MAP.get(lang_code, lang_code.upper())
                st.write(f"🔊 Original Audio: {lang_name}")
                st.write(movie["overview"])

        # LOAD MORE RECOMMENDATIONS (CENTERED)
        if st.session_state.rec_display_count < len(results):
            left, center, right = st.columns([3, 2, 3])
            with center:
                if st.button(
                    "Load more recommendations",
                    use_container_width=True
                ):
                    st.session_state.rec_display_count += 5
                    st.rerun()

