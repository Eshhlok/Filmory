from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from backend import movies_df, tfidf_matrix
from recommender import recommend
from tmdb_client import search_movies_tmdb
from data_store import load_credits, save_feedback
from config import GENRE_MAP,API_KEY

app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://filmory-movies.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
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
    poster_path = extract_poster_path(movie.get("poster_url"))
    backdrop_path = extract_backdrop_path(movie.get("backdrop_url"))

    entry = {
        "id": movie.get("id"),
        "title": movie.get("title"),
        "overview": movie.get("overview", ""),
        "release_date": movie.get("release_date", ""),
        "original_language": movie.get("language", ""),
        "vote_average": movie.get("rating") or 0,
        "vote_count": 0,
        "poster_path": poster_path,
        "backdrop_path": backdrop_path,
        "genre_ids": movie.get("genre_ids", []),
        "genre_names": movie.get("genre_names", []),
        "language_name": LANGUAGE_MAP.get(movie.get("language", ""), ""),
    }

    if mode == "cast":
        entry["cast"] = movie.get("cast", [])
    elif mode == "director":
        entry["directors"] = movie.get("directors", [])

    return entry


# ---------------------------
# /search
# ---------------------------
@app.get("/search")
def search(query: str, page: int = 1):
    results = search_movies_tmdb(query, page=page)
    return [
        {
            "id": r.get("id"),
            "title": r.get("title"),
            "overview": r.get("overview", ""),
            "release_date": r.get("release_date", ""),
            "original_language": r.get("original_language", ""),
            "vote_average": r.get("vote_average", 0),
            "vote_count": r.get("vote_count", 0),
            "poster_path": r.get("poster_path"),
            "backdrop_path": r.get("backdrop_path"),
            "genre_ids": r.get("genre_ids", []),
        }
        for r in results
    ]


# ---------------------------
# /recommend
# ---------------------------
@app.get("/recommend")
def get_recommendations(
    title: str,
    mode: str = "story",
    language: Optional[str] = None,
    top_n: int = 30,
):
    results = recommend(
        movies_df, tfidf_matrix, title,
        top_n=top_n, language_filter=language, mode=mode
    )

    titles_lower = movies_df["title"].str.lower()
    title_lower = title.lower().strip()

    in_db = (
        any(titles_lower == title_lower) or
        any(titles_lower.str.contains(title_lower, regex=False, na=False))
    )

    is_fallback = not in_db

    for movie in results:
        row = movies_df[movies_df["title"] == movie["title"]]

        if not row.empty:
            db_row = row.iloc[0]
            mid = int(db_row["id"])

            movie["id"] = mid
            movie["genre_ids"] = db_row.get("genre_ids", [])
            movie["backdrop_url"] = db_row.get("backdrop_url")

            mc = credits_cache.get(mid)
            if mc:
                movie["cast"] = mc["full_cast"][:6]
                movie["directors"] = mc["directors"]

        movie["genre_names"] = [
            GENRE_MAP.get(gid, str(gid))
            for gid in movie.get("genre_ids", [])
        ]

    return {
        "is_fallback": is_fallback,
        "results": [format_movie(m, mode) for m in results],
    }

# Add this new endpoint - place it after /recommend and before /languages

@app.get("/movie/{movie_id}")
def get_movie_details(movie_id: int):
    """
    Get full movie details including cast and directors.
    Fetches from TMDB if movie not in database.
    """
    import requests
    
    # First, check if movie exists in your database
    movie_row = movies_df[movies_df["id"] == movie_id]
    
    if not movie_row.empty:
        # Movie is in your database - use local data
        row = movie_row.iloc[0]
        credits = credits_cache.get(movie_id, {})
        
        # Parse genre_ids if stored as string
        genre_ids = row.get("genre_ids", [])
        if isinstance(genre_ids, str):
            import json
            try:
                genre_ids = json.loads(genre_ids)
            except:
                genre_ids = []
        
        # Get genre names
        genre_names = []
        for gid in genre_ids:
            if gid in GENRE_MAP:
                genre_names.append(GENRE_MAP[gid])
        
        return {
            "id": movie_id,
            "title": row.get("title"),
            "overview": row.get("overview", ""),
            "release_date": row.get("release_date", ""),
            "original_language": row.get("language", ""),
            "vote_average": row.get("rating", 0),
            "vote_count": 0,
            "poster_path": extract_poster_path(row.get("poster_url")),
            "backdrop_path": extract_backdrop_path(row.get("backdrop_url")),
            "genre_ids": genre_ids,
            "genre_names": genre_names,
            "cast": credits.get("full_cast", [])[:5],
            "directors": credits.get("directors", []),
        }
    else:
        # Movie not in database - fetch from TMDB API
                
        tmdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        
        try:
            response = requests.get(tmdb_url, params={
                "api_key": API_KEY,
                "append_to_response": "credits"
            })
            
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Movie not found")
            
            tmdb_data = response.json()
            
            # Extract cast (top 5)
            cast = []
            for actor in tmdb_data.get("credits", {}).get("cast", [])[:5]:
                cast.append(actor.get("name"))
            
            # Extract directors
            directors = []
            for crew in tmdb_data.get("credits", {}).get("crew", []):
                if crew.get("job") == "Director":
                    directors.append(crew.get("name"))
            
            # Get genre names
            genre_names = []
            for genre in tmdb_data.get("genres", []):
                genre_names.append(genre.get("name"))
            
            return {
                "id": tmdb_data.get("id"),
                "title": tmdb_data.get("title"),
                "overview": tmdb_data.get("overview", ""),
                "release_date": tmdb_data.get("release_date", ""),
                "original_language": tmdb_data.get("original_language", ""),
                "vote_average": tmdb_data.get("vote_average", 0),
                "vote_count": tmdb_data.get("vote_count", 0),
                "poster_path": tmdb_data.get("poster_path"),
                "backdrop_path": tmdb_data.get("backdrop_path"),
                "genre_ids": [g.get("id") for g in tmdb_data.get("genres", [])],
                "genre_names": genre_names,
                "cast": cast,
                "directors": directors,
            }
        except requests.RequestException:
            raise HTTPException(status_code=500, detail="Error fetching from TMDB")

# ---------------------------
# /languages
# ---------------------------
@app.get("/languages")
def get_languages():
    lang_codes = movies_df["language"].dropna().unique().tolist()
    return [
        {"code": code, "name": LANGUAGE_MAP.get(code, code.upper())}
        for code in sorted(lang_codes)
        if code in LANGUAGE_MAP
    ]


# ---------------------------
# /feedback
# ---------------------------
class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: str | None = Field(None, max_length=500)


@app.post("/feedback", status_code=201)
def submit_feedback(body: FeedbackRequest):
    try:
        save_feedback(body.rating, body.feedback)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save feedback.")
    return {"status": "ok"}
