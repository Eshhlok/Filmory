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

# ─────────────────────────────────────────────
# Premium UI Design System (Glassmorphism & Depth)
# ─────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">

<style>
    /* Global Styles & Typography */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif !important;
        background: radial-gradient(circle at top center, #1e293b 0%, #0e1117 100%) !important;
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6, .stMarkdown {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Glassmorphism Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(22, 27, 34, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-8px) !important;
        border-color: rgba(229, 9, 20, 0.5) !important;
        box-shadow: 0 12px 40px 0 rgba(229, 9, 20, 0.2) !important;
    }

    /* Center Titles & Typography Hierarchy */
    .centered-title {
        text-align: center;
        background: linear-gradient(135deg, #ffffff 0%, #9ca3af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
        text-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .centered-subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1.4rem;
        font-weight: 300;
        margin-bottom: 3rem;
        letter-spacing: 1px;
    }

    /* Premium Search Input */
    .stTextInput > div > div > input {
        background: rgba(28, 34, 48, 0.8) !important;
        backdrop-filter: blur(4px) !important;
        color: #ffffff !important;
        border: 2px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #e50914 !important;
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.3), inset 0 2px 4px rgba(0,0,0,0.2) !important;
        background: rgba(28, 34, 48, 1) !important;
    }

    /* Refined Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1c2230 0%, #0e1117 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.85rem !important;
    }
    .stButton > button:hover {
        background: #e50914 !important;
        border-color: #e50914 !important;
        transform: scale(1.05) !important;
        box-shadow: 0 10px 20px rgba(229, 9, 20, 0.4) !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Premium Selectbox */
    .stSelectbox > div > div > div {
        background: rgba(28, 34, 48, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* Rating Badge Premium */
    .rating-badge-premium {
        background: linear-gradient(90deg, #e50914 0%, #9e060d 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 100px;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3);
        display: inline-block;
        margin-bottom: 12px;
    }

    /* Genre Tags Premium */
    code {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e5e5e5 !important;
        padding: 4px 10px !important;
        border-radius: 100px !important;
        font-size: 0.75rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-family: 'Outfit', sans-serif !important;
        margin-right: 6px !important;
        transition: all 0.2s ease !important;
    }
    code:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }

    /* Custom Fallback Warning */
    .premium-warning {
        background: rgba(229, 9, 20, 0.05) !important;
        border-left: 5px solid #e50914 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        color: #ffffff !important;
        margin-bottom: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
    }

    /* Spinner Redesign */
    .stSpinner > div {
        border-top-color: #e50914 !important;
        width: 40px !important;
        height: 40px !important;
    }

    /* Hide Streamlit Header/Footer for clean look */
    header, footer {visibility: hidden;}
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {width: 8px;}
    ::-webkit-scrollbar-track {background: #0e1117;}
    ::-webkit-scrollbar-thumb {
        background: #1c2230; 
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {background: #e50914;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="centered-title">🎬 Movie Recommendation System</h1>', unsafe_allow_html=True)
st.markdown('<p class="centered-subtitle">Find movies similar to your favorite one</p>', unsafe_allow_html=True)

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
# Use a column to limit the width of the search box for better look
_, search_col, _ = st.columns([1, 2, 1])
with search_col:
    movie_name = st.text_input(
        "🔍 Search for a movie",
        placeholder="Type a movie name (e.g. Interstellar, Dangal, Conjuring)",
        label_visibility="collapsed"
    )

# ── Search suggestions ────────────────────────────────────────────────
if movie_name.strip():
    suggestions = get_local_suggestions(movie_name)
    if suggestions:
        st.markdown('<p style="text-align: center; color: #9ca3af; font-size: 0.9rem; margin-top: 10px;">💡 Suggestions from our database:</p>', unsafe_allow_html=True)
        # Use a centered row for suggestions
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
        st.markdown('<p style="color: #9ca3af; margin-bottom: 10px;">Select the movie you meant:</p>', unsafe_allow_html=True)
        
        # 5-column grid for search results
        cols = st.columns(5)
        for idx, movie in enumerate(
            st.session_state.search_results[:st.session_state.display_count]
        ):
            with cols[idx % 5]:
                with st.container(border=True):
                    if movie.get("poster_path"):
                        st.image(
                            "https://image.tmdb.org/t/p/w300" + movie["poster_path"],
                            use_container_width=True
                        )
                    else:
                        st.markdown('<div style="height: 225px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; border-radius: 12px; margin-bottom: 10px;">No Image</div>', unsafe_allow_html=True)
                    
                    if st.button(movie["title"], key=f"select_{movie['id']}", use_container_width=True):
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
                        st.rerun()

        # Load more button
        if st.session_state.has_more_search_results:
            _, center, _ = st.columns([3, 2, 3])
            with center:
                if st.button("Load more", use_container_width=True, key="load_more_search"):
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
    st.divider()
    selected_movie_title = st.session_state.selected_movie
    st.markdown(f'<h2 style="margin-top: 0;">Recommendations based on: <span style="color: #e50914;">{selected_movie_title}</span></h2>', unsafe_allow_html=True)

    # ── Fallback warning ──────────────────────────────────────────────
    if st.session_state.get("is_fallback"):
        st.markdown(f"""
        <div class="premium-warning">
            🎭 <strong>Exclusive Discovery Mode</strong><br>
            This cinematic masterpiece isn't in our local vault yet. 
            We've unlocked similar horizons from our global TMDB archives just for you.
        </div>
        """, unsafe_allow_html=True)

    # ── Controls row (Side-by-side) ───────────────────────────────────
    col1, col2 = st.columns(2)
    
    with col1:
        rec_mode_label = st.selectbox(
            "🎯 Recommendation type",
            list(REC_MODE_MAP.keys()),
            index=list(REC_MODE_MAP.keys()).index(
                st.session_state.get("selected_rec_mode", "Story (Plot based)")
            )
        )
        rec_mode = REC_MODE_MAP[rec_mode_label]

    with col2:
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

    if not results:
        st.info("No close matches found.")
    else:
        # 2-column grid for recommendations
        rec_cols = st.columns(2)
        for idx, movie in enumerate(results[:st.session_state.rec_display_count]):
            with rec_cols[idx % 2]:
                # Card container
                with st.container(border=True):
                    inner_col1, inner_col2 = st.columns([1, 2])
                    
                    with inner_col1:
                        if movie.get("poster_url"):
                            st.image(movie["poster_url"], use_container_width=True)
                        else:
                            st.markdown('<div style="height: 200px; background-color: #2b2b2b; display: flex; align-items: center; justify-content: center; border-radius: 4px;">No Image</div>', unsafe_allow_html=True)
                    
                    with inner_col2:
                        st.markdown(f"### {movie['title']}")
                        
                        # Rating Badge
                        rating = movie.get('rating', 0)
                        st.markdown(f'<div class="rating-badge-premium">⭐ {rating:.1f} / 10</div>', unsafe_allow_html=True)
                        
                        st.markdown(f"📅 **Release:** {movie.get('release_date', 'N/A')}")
                        
                        lang_code = movie.get("language", "N/A")
                        lang_name = LANGUAGE_MAP.get(lang_code, lang_code.upper())
                        st.markdown(f"🔊 **Audio:** {lang_name}")
                        
                        # Overview (limit to roughly 2 lines)
                        overview = movie.get("overview", "")
                        if len(overview) > 150:
                            overview = overview[:147] + "..."
                        st.markdown(f'<p style="font-size: 0.9rem; color: #9ca3af; margin-bottom: 10px;">{overview}</p>', unsafe_allow_html=True)
                        
                        # Genre Chips
                        genre_ids = movie.get("genre_ids", [])
                        genre_names = [GENRE_MAP.get(gid, str(gid)) for gid in genre_ids]
                        if genre_names:
                            # Use inline code blocks for chips
                            chips_html = " ".join([f"`{name}`" for name in genre_names])
                            st.markdown(chips_html)

        # Load more recommendations
        if st.session_state.rec_display_count < len(results):
            _, center, _ = st.columns([3, 2, 3])
            with center:
                if st.button("Load more recommendations", use_container_width=True, key="load_more_rec"):
                    st.session_state.rec_display_count += 5
                    st.rerun()