import streamlit as st
from recommender import recommend
from backend import movies_df, cosine_sim
from tmdb_client import search_movies_tmdb
from config import GENRE_MAP

LANGUAGE_MAP = {
    "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil",
    "ko": "Korean", "fr": "French", "es": "Spanish", "de": "German",
    "ja": "Japanese", "zh": "Chinese", "tl": "Tagalog", "it": "Italian",
    "ru": "Russian", "pt": "Portuguese", "ar": "Arabic", "tr": "Turkish",
    "sv": "Swedish", "nl": "Dutch", "pl": "Polish", "id": "Indonesian",
    "vi": "Vietnamese", "fa": "Persian", "he": "Hebrew", "cs": "Czech",
    "ro": "Romanian", "da": "Danish", "fi": "Finnish", "no": "Norwegian",
    "hu": "Hungarian", "el": "Greek", "bg": "Bulgarian", "uk": "Ukrainian",
    "sr": "Serbian", "hr": "Croatian", "sk": "Slovak", "lt": "Lithuanian",
    "sl": "Slovenian", "et": "Estonian", "lv": "Latvian", "ml": "Malayalam",
    "bn": "Bengali", "mr": "Marathi", "pa": "Punjabi", "th": "Thai",
    "kn": "Kannada"
}

REC_MODE_MAP = {
    "Story (Plot based)": "story",
    "Cast based":         "cast",
    "Director based":     "director",
    "Genre based":        "genre"
}

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommendation System")
st.write("Find movies similar to your favorite one!")

# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────
defaults = {
    "search_page":               1,
    "search_results":            [],
    "last_query":                "",
    "display_count":             5,
    "rec_display_count":         5,
    "all_recommendations":       [],
    "has_more_search_results":   True,
    "should_fetch_search_page":  True,
    "is_fallback":               False,
    "selected_rec_mode":         "Story (Plot based)",
    "selected_filter":           "All",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# Search suggestions from local DB
# ─────────────────────────────────────────────
def get_local_suggestions(query: str, max_results: int = 8) -> list[str]:
    """Fast local DB title search — no TMDB call needed."""
    if not query or len(query.strip()) < 1:
        return []
    q = query.lower().strip()
    matched = movies_df[
        movies_df["title"].str.lower().str.contains(q, regex=False, na=False)
    ]["title"].drop_duplicates()
    return matched.head(max_results).tolist()


# ─────────────────────────────────────────────
# Search input
# ─────────────────────────────────────────────
movie_name = st.text_input(
    "🔍 Search for a movie",
    placeholder="Type a movie name (e.g. Interstellar, Dangal, Conjuring)"
)

# ── Search suggestions ────────────────────────────────────────────────
if movie_name.strip():
    suggestions = get_local_suggestions(movie_name)
    if suggestions:
        st.caption("💡 Suggestions from our database:")
        suggestion_cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with suggestion_cols[i]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.last_query        = ""   # force reset
                    st.session_state.search_results    = []
                    st.session_state.display_count     = 5
                    st.session_state.has_more_search_results  = True
                    st.session_state.should_fetch_search_page = True
                    # Rerun with updated query via session state trick
                    st.session_state["_suggestion_clicked"] = suggestion
                    st.rerun()

# Handle suggestion click — inject into search
if "_suggestion_clicked" in st.session_state:
    movie_name = st.session_state.pop("_suggestion_clicked")

# ── Reset everything when query changes ───────────────────────────────
if movie_name != st.session_state.last_query:
    st.session_state.search_page              = 1
    st.session_state.search_results           = []
    st.session_state.display_count            = 5
    st.session_state.last_query               = movie_name
    st.session_state.has_more_search_results  = True
    st.session_state.should_fetch_search_page = True


# ─────────────────────────────────────────────
# SEARCH RESULTS STAGE
# ─────────────────────────────────────────────
if movie_name.strip():
    if st.session_state.should_fetch_search_page and st.session_state.has_more_search_results:
        with st.spinner("🔍 Searching for movies..."):
            new_results = search_movies_tmdb(movie_name, page=st.session_state.search_page)

        if not new_results:
            st.session_state.has_more_search_results = False
        else:
            existing_ids = {m["id"] for m in st.session_state.search_results}
            for movie in new_results:
                if movie["id"] not in existing_ids:
                    st.session_state.search_results.append(movie)

        st.session_state.should_fetch_search_page = False

    if st.session_state.search_results:
        st.caption("Select the movie you meant:")
        cols = st.columns(5)

        for idx, movie in enumerate(
            st.session_state.search_results[:st.session_state.display_count]
        ):
            with cols[idx % 5]:
                if movie.get("poster_path"):
                    st.image(
                        "https://image.tmdb.org/t/p/w300" + movie["poster_path"],
                        use_container_width=True
                    )
                else:
                    st.write("No Image")

                if st.button(movie["title"], key=f"select_{movie['id']}"):
                    # ✅ Reset ALL UI settings when a new movie is selected
                    st.session_state.selected_movie    = movie["title"]
                    st.session_state.rec_display_count = 5
                    st.session_state.is_fallback       = False
                    st.session_state.selected_rec_mode = "Story (Plot based)"
                    st.session_state.selected_filter   = "All"
                    st.session_state.last_rec_mode     = "story"
                    st.session_state.last_filter_option = "All"

                    with st.spinner(f"🎬 Finding recommendations for '{movie['title']}'..."):
                        results = recommend(
                            movies_df,
                            cosine_sim,
                            movie["title"]
                        )

                    # Check if fallback was used
                    st.session_state.is_fallback         = (len(results) > 0 and
                        not any(
                            movies_df["title"].str.lower() == movie["title"].lower()
                        ) and not any(
                            movies_df["title"].str.lower().str.contains(
                                movie["title"].lower(), regex=False
                            )
                        )
                    )
                    st.session_state.all_recommendations = results

        # Load more button
        if st.session_state.has_more_search_results:
            left, center, right = st.columns([3, 2, 3])
            with center:
                if st.button("Load more", use_container_width=True):
                    if st.session_state.display_count < len(st.session_state.search_results):
                        st.session_state.display_count += 5
                    else:
                        st.session_state.search_page += 1
                        st.session_state.should_fetch_search_page = True
                    st.rerun()


# ─────────────────────────────────────────────
# RECOMMENDATION STAGE
# ─────────────────────────────────────────────
if "selected_movie" in st.session_state:
    selected_movie_title = st.session_state.selected_movie
    st.subheader(f"Recommendations based on: **{selected_movie_title}**")

    # ── Fallback warning ──────────────────────────────────────────────
    if st.session_state.get("is_fallback"):
        st.warning(
            "⚠️ **This movie isn't in our database yet.** "
            "Showing similar movies based on genre and plot from TMDB — "
            "results may be less precise than usual.",
            icon="🎭"
        )

    # ── Recommendation mode — restored to last selected ───────────────
    rec_mode_label = st.selectbox(
        "🎯 Recommendation type",
        list(REC_MODE_MAP.keys()),
        index=list(REC_MODE_MAP.keys()).index(
            st.session_state.get("selected_rec_mode", "Story (Plot based)")
        )
    )
    rec_mode = REC_MODE_MAP[rec_mode_label]

    # ── Language filter — restored to last selected ───────────────────
    language_options = ["All"] + list(LANGUAGE_MAP.values())
    filter_option = st.selectbox(
        "Filter by language",
        options=language_options,
        index=language_options.index(
            st.session_state.get("selected_filter", "All")
        )
    )

    if "last_rec_mode" not in st.session_state:
        st.session_state.last_rec_mode = rec_mode

    if "last_filter_option" not in st.session_state:
        st.session_state.last_filter_option = "All"

    # ── Re-fetch recommendations if mode or filter changed ────────────
    if (
        filter_option != st.session_state.last_filter_option
        or rec_mode   != st.session_state.last_rec_mode
    ):
        st.session_state.selected_rec_mode  = rec_mode_label
        st.session_state.selected_filter    = filter_option
        st.session_state.rec_display_count  = 5

        selected_lang_code = None
        if filter_option != "All":
            selected_lang_code = next(
                (k for k, v in LANGUAGE_MAP.items() if v == filter_option), None
            )

        with st.spinner(f"🔄 Fetching {rec_mode_label.lower()} recommendations..."):
            st.session_state.all_recommendations = recommend(
                movies_df,
                cosine_sim,
                selected_movie_title,
                language_filter=selected_lang_code,
                mode=rec_mode
            )

        st.session_state.last_filter_option = filter_option
        st.session_state.last_rec_mode      = rec_mode
        st.rerun()

    # ── Display results ───────────────────────────────────────────────
    results = st.session_state.all_recommendations

    if rec_mode != "story":
        results = sorted(results, key=lambda x: x.get("rating") or 0, reverse=True)

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
                if rec_mode == "genre":
                    genre_names = [
                        GENRE_MAP.get(gid, str(gid))
                        for gid in movie.get("genre_ids", [])
                    ]
                    st.write("🎭 Genres:", ", ".join(genre_names))

        # Load more recommendations
        if st.session_state.rec_display_count < len(results):
            left, center, right = st.columns([3, 2, 3])
            with center:
                if st.button("Load more recommendations", use_container_width=True):
                    st.session_state.rec_display_count += 5
                    st.rerun()