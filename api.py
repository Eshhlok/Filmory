from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from backend import movies_df, cosine_sim
from recommender import recommend
from tmdb_client import search_movies_tmdb, get_cast_and_director
from data_store import load_credits
from config import GENRE_MAP

app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"

def extract_poster_path(poster_url: str | None) -> str | None:
    """
    Convert full poster URL back to just the path.
    e.g. "https://image.tmdb.org/t/p/w500/abc123.jpg" → "/abc123.jpg"
    MovieCard expects just the path, not the full URL.
    """
    if not poster_url:
        return None
    if poster_url.startswith(IMAGE_BASE):
        return poster_url[len(IMAGE_BASE):]
    return poster_url


def extract_backdrop_path(backdrop_url: str | None) -> str | None:
    """
    Convert full backdrop URL back to just the path.
    e.g. "https://image.tmdb.org/t/p/w1280/abc123.jpg" → "/abc123.jpg"
    """
    if not backdrop_url:
        return None
    if backdrop_url.startswith(BACKDROP_BASE):
        return backdrop_url[len(BACKDROP_BASE):]
    return backdrop_url


def format_movie(movie: dict, mode: str = "story") -> dict:
    """
    Convert a recommendation result dict into the shape
    that the MovieCard and MovieDetail components expect.
    """
    poster_path   = extract_poster_path(movie.get("poster_url"))
    backdrop_path = extract_backdrop_path(movie.get("backdrop_url"))

    entry = {
        "id":                movie.get("id"),
        "title":             movie.get("title"),
        "overview":          movie.get("overview", ""),
        "release_date":      movie.get("release_date", ""),
        "original_language": movie.get("language", ""),
        "vote_average":      movie.get("rating") or 0,
        "vote_count":        0,                          # not stored in our DB
        "poster_path":       poster_path,                # ✅ path only, not full URL
        "backdrop_path":     backdrop_path,              # ✅ populated from DB
        "genre_ids":         movie.get("genre_ids", []),
        "genre_names":       movie.get("genre_names", []),
        "language_name":     LANGUAGE_MAP.get(movie.get("language", ""), ""),
    }

    # Add cast/director for relevant modes
    if mode == "cast":
        entry["cast"] = movie.get("cast", [])
    elif mode == "director":
        entry["directors"] = movie.get("directors", [])

    return entry


# ─────────────────────────────────────────────
# /search
# ─────────────────────────────────────────────
@app.get("/search")
def search(query: str, page: int = 1):
    """Search TMDB for movies — returns fields matching Movie type."""
    results = search_movies_tmdb(query, page=page)
    return [
        {
            "id":                r.get("id"),
            "title":             r.get("title"),
            "overview":          r.get("overview", ""),
            "release_date":      r.get("release_date", ""),
            "original_language": r.get("original_language", ""),
            "vote_average":      r.get("vote_average", 0),
            "vote_count":        r.get("vote_count", 0),
            "poster_path":       r.get("poster_path"),       # ✅ TMDB already returns path
            "backdrop_path":     r.get("backdrop_path"),     # ✅ available from TMDB search
            "genre_ids":         r.get("genre_ids", []),
        }
        for r in results
    ]


# ─────────────────────────────────────────────
# /recommend
# ─────────────────────────────────────────────
@app.get("/recommend")
def get_recommendations(
    title:    str,
    mode:     str = "story",
    language: Optional[str] = None,
    top_n:    int = 30
):
    results = recommend(
        movies_df,
        cosine_sim,
        title,
        top_n=top_n,
        language_filter=language,
        mode=mode
    )

    # Detect fallback
    titles_lower = movies_df["title"].str.lower()
    title_lower  = title.lower().strip()
    in_db = (
        any(titles_lower == title_lower) or
        any(titles_lower.str.contains(title_lower, regex=False, na=False))
    )
    is_fallback = not in_db

    # Enrich with credits + backdrop
    for movie in results:
        row = movies_df[movies_df["title"] == movie["title"]]
        if not row.empty:
            mid = int(row.iloc[0]["id"])

            # ✅ Pull backdrop_url stored in DB
            movie["backdrop_url"] = row.iloc[0].get("backdrop_url")

            mc  = credits_cache.get(mid)
            if mc:
                movie["cast"]      = mc["full_cast"][:6]
                movie["directors"] = mc["directors"]

        movie["genre_names"] = [
            GENRE_MAP.get(gid, str(gid))
            for gid in movie.get("genre_ids", [])
        ]

    return {
        "is_fallback": is_fallback,
        "results":     [format_movie(m, mode) for m in results]
    }


# ─────────────────────────────────────────────
# /languages
# ─────────────────────────────────────────────
@app.get("/languages")
def get_languages():
    lang_codes = movies_df["language"].dropna().unique().tolist()
    return [
        {"code": code, "name": LANGUAGE_MAP.get(code, code.upper())}
        for code in sorted(lang_codes)
        if code in LANGUAGE_MAP
    ]