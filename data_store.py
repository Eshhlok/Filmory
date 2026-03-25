import time
import os
import json
import sqlite3
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import (
    API_KEY, BASE_URL, IMAGE_BASE_URL,
    REQUEST_TIMEOUT, REQUEST_SLEEP,
    LANGUAGES, GENRE_MAP,
    PAGES_PER_LANGUAGE_dict,
    ORIGINAL_LANG_MAP
)

# ─────────────────────────────────────────────
# HTTP Session with retry
# ─────────────────────────────────────────────
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

DB_FILE = "movies.db"


# ─────────────────────────────────────────────
# SQLite setup
# ─────────────────────────────────────────────
def init_db():
    """Create movies and credits tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id           INTEGER PRIMARY KEY,
            title        TEXT,
            overview     TEXT,
            poster_url   TEXT,
            rating       REAL,
            release_date TEXT,
            language     TEXT,
            genre_ids    TEXT
        )
    """)

    # ✅ Credits table — persistent cast/director cache
    conn.execute("""
        CREATE TABLE IF NOT EXISTS credits (
            movie_id         INTEGER PRIMARY KEY,
            top_billed_actor TEXT,
            full_cast        TEXT,
            directors        TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialised.")


def save_movies(movies: list[dict]):
    """Insert movies into DB. INSERT OR IGNORE skips duplicates."""
    if not movies:
        return

    rows = [
        {
            "id":           m["id"],
            "title":        m["title"],
            "overview":     m["overview"],
            "poster_url":   m["poster_url"],
            "rating":       m["rating"],
            "release_date": m["release_date"],
            "language":     m["language"],
            "genre_ids":    json.dumps(m["genre_ids"])
        }
        for m in movies
    ]

    conn = sqlite3.connect(DB_FILE)
    conn.executemany(
        """
        INSERT OR IGNORE INTO movies
            (id, title, overview, poster_url, rating, release_date, language, genre_ids)
        VALUES
            (:id, :title, :overview, :poster_url, :rating, :release_date, :language, :genre_ids)
        """,
        rows
    )
    conn.commit()
    conn.close()


def load_movies() -> pd.DataFrame:
    """Load all movies from SQLite into a DataFrame."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM movies", conn)
    conn.close()

    if df.empty:
        raise RuntimeError("❌ No movies in database. Run fetch_all_movies() first.")

    df["genre_ids"] = df["genre_ids"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else []
    )
    print(f"✅ Loaded {len(df)} movies from database.")
    return df


def get_existing_ids() -> set:
    """Return the set of movie IDs already in the movies table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT id FROM movies")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def get_cached_credit_ids() -> set:
    """Return the set of movie IDs that already have credits cached."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT movie_id FROM credits")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def save_credits(movie_id: int, top_billed_actor: str, full_cast: list, directors: list):
    """Save credits for a single movie to the credits table."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        INSERT OR REPLACE INTO credits (movie_id, top_billed_actor, full_cast, directors)
        VALUES (?, ?, ?, ?)
        """,
        (
            movie_id,
            top_billed_actor,
            json.dumps(full_cast),
            json.dumps(directors)
        )
    )
    conn.commit()
    conn.close()


def load_credits() -> dict:
    """
    Load all credits from SQLite into a dict keyed by movie_id.
    Returns: { movie_id: { top_billed_actor, full_cast, directors } }
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute(
        "SELECT movie_id, top_billed_actor, full_cast, directors FROM credits"
    )
    rows = cursor.fetchall()
    conn.close()

    credits = {}
    for movie_id, top_billed_actor, full_cast, directors in rows:
        credits[int(movie_id)] = {
            "top_billed_actor": top_billed_actor,
            "full_cast":        json.loads(full_cast)  if full_cast  else [],
            "directors":        json.loads(directors)  if directors  else []
        }
    return credits


def cache_all_credits(movies_df: pd.DataFrame):
    """
    Pre-fetch and cache cast + director for all movies in DB.
    Only fetches movies not already in the credits table — safe to call
    repeatedly, acts as incremental update.
    """
    from tmdb_client import get_cast_and_director

    cached_ids  = get_cached_credit_ids()
    missing     = [
        int(row["id"])
        for _, row in movies_df.iterrows()
        if int(row["id"]) not in cached_ids
    ]

    if not missing:
        print("✅ All credits already cached.")
        return

    print(f"🎬 Caching credits for {len(missing)} movies...")

    for i, movie_id in enumerate(missing, 1):
        cast, directors = get_cast_and_director(movie_id)

        # cast is already sorted by billing order in tmdb_client
        top_billed = cast[0] if cast else None
        save_credits(movie_id, top_billed, cast, directors)

        if i % 50 == 0:
            print(f"   → {i}/{len(missing)} cached...")

    print(f"✅ Credits cached for {len(missing)} movies.")


# ─────────────────────────────────────────────
# TMDB fetching
# ─────────────────────────────────────────────
def fetch_movies(language_code: str, genre_id: int, pages: int) -> list[dict]:
    """Fetch movies from TMDB for a given language + genre combination."""
    movies    = []
    base_lang = language_code.split("-")[0]
    original_lang = ORIGINAL_LANG_MAP.get(language_code)

    for page in range(1, pages + 1):
        try:
            params = {
                "api_key":     API_KEY,
                "language":    base_lang,
                "with_genres": genre_id,
                "sort_by":     "vote_count.desc",
                "page":        page
            }
            if original_lang:
                params["with_original_language"] = original_lang

            response = session.get(
                f"{BASE_URL}/discover/movie",
                params=params,
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 429:
                print("⚠️  Rate limited. Sleeping 5 seconds...")
                time.sleep(5)
                continue

            if response.status_code != 200:
                print(f"⚠️  Failed {language_code} page {page} (status {response.status_code})")
                break

            results = response.json().get("results", [])
            print(f"  {language_code} | Genre {genre_id} | Page {page} → {len(results)} movies")

            if not results:
                break

            for m in results:
                movies.append({
                    "id":           m.get("id"),
                    "title":        m.get("title"),
                    "overview":     m.get("overview") or "",
                    "poster_url":   (
                        IMAGE_BASE_URL + m["poster_path"]
                        if m.get("poster_path") else None
                    ),
                    "rating":       m.get("vote_average"),
                    "release_date": m.get("release_date"),
                    "language":     m.get("original_language"),
                    "genre_ids":    m.get("genre_ids", [])
                })

            time.sleep(REQUEST_SLEEP)

        except Exception as e:
            print(f"❌ Error fetching {language_code} page {page}: {e}")
            break

    return movies


def fetch_all_movies(incremental: bool = True):
    """Fetch movies for all languages and genres and save to SQLite."""
    init_db()
    existing_ids = get_existing_ids() if incremental else set()

    total_tasks  = len(LANGUAGES) * len(GENRE_MAP)
    current_task = 0
    total_new    = 0

    for lang_name, lang_code in LANGUAGES.items():
        pages = PAGES_PER_LANGUAGE_dict.get(lang_code, 5)

        for genre_id, genre_name in GENRE_MAP.items():
            current_task += 1
            print(
                f"\n[{current_task}/{total_tasks}] {lang_name} - {genre_name} ({pages} pages)",
                flush=True
            )

            movies     = fetch_movies(lang_code, genre_id, pages)
            new_movies = [m for m in movies if m["id"] not in existing_ids]
            existing_ids.update(m["id"] for m in new_movies)

            save_movies(new_movies)
            total_new += len(new_movies)
            print(f"   → {len(new_movies)} new movies saved (skipped {len(movies) - len(new_movies)})")

    print(f"\n✅ Done. {total_new} new movies added to database.")