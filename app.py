import streamlit as st
from recommender import recommend
from backend import movies_df, cosine_sim
from tmdb_client import search_movies_tmdb
from data_store import load_credits
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
# Load credits cache once
# ─────────────────────────────────────────────
@st.cache_resource
def get_credits_cache():
    return load_credits()

credits_cache = get_credits_cache()

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
    "last_rec_mode":             "story",
    "last_filter_option":        "All",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# Search input + TMDB suggestions
# ─────────────────────────────────────────────
movie_name = st.text_input(
    "🔍 Search for a movie",
    placeholder="Type a movie name (e.g. Interstellar, Dangal, Conjuring)"
)

# ── TMDB suggestions as you type ─────────────────────────────────────
if movie_name.strip():
    with st.spinner("Fetching suggestions..."):
        suggestions = search_movies_tmdb(movie_name, page=1)

    if suggestions:
        st.caption("💡 Did you mean:")
        sug_cols = st.columns(min(len(suggestions[:5]), 5))
        for i, sug in enumerate(suggestions[:5]):
            with sug_cols[i]:
                label = sug.get("title", "")
                year  = (sug.get("release_date") or "")[:4]
                btn_label = f"{label} ({year})" if year else label
                if st.button(btn_label, key=f"sug_{sug['id']}", use_container_width=True):
                    st.session_state["_suggestion_clicked"] = sug["title"]
                    st.rerun()

# Handle suggestion click
if "_suggestion_clicked" in st.session_state:
    movie_name = st.session_state.pop("_suggestion_clicked")
    st.session_state.last_query               = ""
    st.session_state.search_results           = []
    st.session_state.display_count            = 5
    st.session_state.has_more_search_results  = True
    st.session_state.should_fetch_search_page = True

# ── Reset on query change ─────────────────────────────────────────────
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
                    st.session_state.selected_movie      = movie["title"]
                    st.session_state.rec_display_count   = 5
                    st.session_state.is_fallback         = False
                    st.session_state.selected_rec_mode   = "Story (Plot based)"
                    st.session_state.selected_filter     = "All"
                    st.session_state.last_rec_mode       = "story"
                    st.session_state.last_filter_option  = "All"

                    with st.spinner(f"🎬 Finding recommendations for '{movie['title']}'..."):
                        results = recommend(
                            movies_df,
                            cosine_sim,
                            movie["title"]
                        )

                    # Detect fallback
                    titles_lower = movies_df["title"].str.lower()
                    title_lower  = movie["title"].lower()
                    in_db = (
                        any(titles_lower == title_lower) or
                        any(titles_lower.str.contains(title_lower, regex=False))
                    )
                    st.session_state.is_fallback         = not in_db
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

    # ── Recommendation mode ───────────────────────────────────────────
    rec_mode_label = st.selectbox(
        "🎯 Recommendation type",
        list(REC_MODE_MAP.keys()),
        index=list(REC_MODE_MAP.keys()).index(
            st.session_state.get("selected_rec_mode", "Story (Plot based)")
        )
    )
    rec_mode = REC_MODE_MAP[rec_mode_label]

    # ── Language filter ───────────────────────────────────────────────
    language_options = ["All"] + list(LANGUAGE_MAP.values())
    filter_option = st.selectbox(
        "Filter by language",
        options=language_options,
        index=language_options.index(
            st.session_state.get("selected_filter", "All")
        )
    )

    # ── Re-fetch if mode or filter changed ────────────────────────────
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

    # ✅ REMOVED the rating re-sort — backend ordering is always correct

    if not results:
        st.info("No close matches found.")
    else:
        for movie in results[:st.session_state.rec_display_count]:
            col1, col2 = st.columns([1, 3])

            with col1:
                if movie.get("poster_url"):
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

                # ── Cast / Director info based on mode ────────────────
                if rec_mode in ("cast", "director"):
                    movie_row = movies_df[movies_df["title"] == movie["title"]]
                    if not movie_row.empty:
                        mid = int(movie_row.iloc[0]["id"])
                        mc  = credits_cache.get(mid)
                        if mc:
                            if rec_mode == "cast" and mc["full_cast"]:
                                st.write("🎭 Cast: " + ", ".join(mc["full_cast"][:6]))
                            elif rec_mode == "director" and mc["directors"]:
                                st.write("🎬 Director: " + ", ".join(mc["directors"]))

                # ── Genre tags ────────────────────────────────────────
                if rec_mode == "genre":
                    genre_names = [
                        GENRE_MAP.get(gid, str(gid))
                        for gid in movie.get("genre_ids", [])
                    ]
                    st.write("🎭 Genres: " + ", ".join(genre_names))

                st.write(movie["overview"])

        # Load more recommendations
        if st.session_state.rec_display_count < len(results):
            left, center, right = st.columns([3, 2, 3])
            with center:
                if st.button("Load more recommendations", use_container_width=True):
                    st.session_state.rec_display_count += 5
                    st.rerun()