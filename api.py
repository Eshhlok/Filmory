from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from backend import movies_df, cosine_sim
from recommender import recommend
from tmdb_client import search_movies_tmdb
from data_store import load_credits
from config import GENRE_MAP

app = FastAPI(title="Movie Recommender API")

# ── CORS — allow Next.js dev server to call this API ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load credits once at startup
credits_cache = load_credits()

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


# ─────────────────────────────────────────────
# /search  — TMDB movie search
# ─────────────────────────────────────────────
@app.get("/search")
def search(query: str, page: int = 1):
    """
    Search TMDB for movies matching the query.
    Returns list of movies with poster_path, title, release_date, vote_average.
    """
    results = search_movies_tmdb(query, page=page)
    return [
        {
            "id":           r.get("id"),
            "title":        r.get("title"),
            "release_date": r.get("release_date"),
            "poster_path":  r.get("poster_path"),
            "vote_average": r.get("vote_average"),
            "overview":     r.get("overview"),
            "original_language": r.get("original_language"),
        }
        for r in results
    ]


# ─────────────────────────────────────────────
# /recommend  — get recommendations
# ─────────────────────────────────────────────
@app.get("/recommend")
def get_recommendations(
    title:    str,
    mode:     str = "story",
    language: Optional[str] = None,
    top_n:    int = 30
):
    """
    Get movie recommendations.

    Args:
        title:    Movie title (English or regional script)
        mode:     story | cast | director | genre
        language: ISO language code filter e.g. "hi", "en" (optional)
        top_n:    Max results to return

    Returns:
        {
          is_fallback: bool,
          results: [...movies with credits if cast/director mode...]
        }
    """
    results = recommend(
        movies_df,
        cosine_sim,
        title,
        top_n=top_n,
        language_filter=language,
        mode=mode
    )

    # Detect if fallback was used
    titles_lower = movies_df["title"].str.lower()
    title_lower  = title.lower().strip()
    in_db = (
        any(titles_lower == title_lower) or
        any(titles_lower.str.contains(title_lower, regex=False, na=False))
    )
    is_fallback = not in_db

    # Enrich results with credits for cast/director modes
    enriched = []
    for movie in results:
        entry = {**movie}

        if mode in ("cast", "director"):
            # Find movie ID from DB
            row = movies_df[movies_df["title"] == movie["title"]]
            if not row.empty:
                mid = int(row.iloc[0]["id"])
                mc  = credits_cache.get(mid)
                if mc:
                    entry["cast"]      = mc["full_cast"][:6] if mode == "cast" else []
                    entry["directors"] = mc["directors"]     if mode == "director" else []

        # Map language code to name
        lang_code = movie.get("language", "")
        entry["language_name"] = LANGUAGE_MAP.get(lang_code, lang_code.upper())

        # Map genre IDs to names
        entry["genre_names"] = [
            GENRE_MAP.get(gid, str(gid))
            for gid in movie.get("genre_ids", [])
        ]

        enriched.append(entry)

    return {
        "is_fallback": is_fallback,
        "results":     enriched
    }


# ─────────────────────────────────────────────
# /languages  — list available languages
# ─────────────────────────────────────────────
@app.get("/languages")
def get_languages():
    """Returns list of languages present in the DB."""
    lang_codes = movies_df["language"].dropna().unique().tolist()
    return [
        {"code": code, "name": LANGUAGE_MAP.get(code, code.upper())}
        for code in sorted(lang_codes)
        if code in LANGUAGE_MAP
    ]