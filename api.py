from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from backend import movies_df, cosine_sim
from recommender import recommend
from tmdb_client import search_movies_tmdb, get_cast_and_director
from data_store import load_credits, save_feedback
from config import GENRE_MAP

app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://filmory-movies.vercel.app",
                    "http://localhost:3000",
                    "http://localhost:5173"
                  ], 
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

IMAGE_BASE     = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE  = "https://image.tmdb.org/t/p/w1280"


def extract_poster_path(poster_url):
    if not poster_url or not isinstance(poster_url, str):
        return None
    if poster_url.startswith(IMAGE_BASE):
        return poster_url[len(IMAGE_BASE):]
    return poster_url


def extract_backdrop_path(backdrop_url):
    if not backdrop_url or not isinstance(backdrop_url, str):
        return None
    if backdrop_url.startswith(BACKDROP_BASE):
        return backdrop_url[len(BACKDROP_BASE):]
    return backdrop_url


def format_movie(movie: dict, mode: str = "story") -> dict:
    poster_path   = extract_poster_path(movie.get("poster_url"))
    backdrop_path = extract_backdrop_path(movie.get("backdrop_url"))

    entry = {
        "id":                movie.get("id"),
        "title":             movie.get("title"),
        "overview":          movie.get("overview", ""),
        "release_date":      movie.get("release_date", ""),
        "original_language": movie.get("language", ""),
        "vote_average":      movie.get("rating") or 0,
        "vote_count":        0,
        "poster_path":       poster_path,
        "backdrop_path":     backdrop_path,
        "genre_ids":         movie.get("genre_ids", []),
        "genre_names":       movie.get("genre_names", []),
        "language_name":     LANGUAGE_MAP.get(movie.get("language", ""), ""),
    }

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
            "poster_path":       r.get("poster_path"),
            "backdrop_path":     r.get("backdrop_path"),
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
        movies_df, cosine_sim, title,
        top_n=top_n, language_filter=language, mode=mode
    )

    titles_lower = movies_df["title"].str.lower()
    title_lower  = title.lower().strip()
    in_db = (
        any(titles_lower == title_lower) or
        any(titles_lower.str.contains(title_lower, regex=False, na=False))
    )
    is_fallback = not in_db

    for movie in results:
        mid = movie.get("id")

        if mid is not None:
            row = movies_df[movies_df["id"] == mid]

            if not row.empty:
                db_row = row.iloc[0]

                movie["genre_ids"] = db_row.get("genre_ids", [])
                movie["genre_names"] = db_row.get("genre_names", [])
                movie["backdrop_url"] = db_row.get("backdrop_url")

                mc = credits_cache.get(int(mid))
                if mc:
                    movie["cast"] = mc["full_cast"][:6]
                    movie["directors"] = mc["directors"]

        # fallback if still missing
        if not movie.get("genre_names"):
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


# ─────────────────────────────────────────────
# /feedback
# ─────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    rating:  int   = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=500)


@app.post("/feedback", status_code=201)
def submit_feedback(body: FeedbackRequest):
    try:
        save_feedback(body.rating, body.comment)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save feedback.")
    return {"status": "ok"}