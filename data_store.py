import sys
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

# ─────────────────────────────────────────────
# SQLite setup
# ─────────────────────────────────────────────
DB_FILE = "movies.db"

def init_db():
    """Create the movies table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id          INTEGER PRIMARY KEY,
            title       TEXT,
            overview    TEXT,
            poster_url  TEXT,
            rating      REAL,
            release_date TEXT,
            language    TEXT,
            genre_ids   TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialised.")


def save_movies(movies: list[dict]):
    """
    Insert movies into the DB.
    INSERT OR IGNORE skips duplicates — safe to call repeatedly.
    """
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
    """Load all movies from the SQLite DB into a DataFrame."""
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
    """Return the set of movie IDs already stored in the DB."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT id FROM movies")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


# ─────────────────────────────────────────────
# TMDB fetching
# ─────────────────────────────────────────────
def fetch_movies(language_code: str, genre_id: int, pages: int) -> list[dict]:
    """
    Fetch movies from TMDB for a given language + genre combination.

    Key fix vs the old version:
      - Uses ORIGINAL_LANG_MAP so we only get movies *originally* in that
        language (not just translated/dubbed versions).
      - Uses per-language page count from PAGES_PER_LANGUAGE_dict.
    """
    movies = []
    base_lang = language_code.split("-")[0]          # "hi-IN" → "hi"
    original_lang = ORIGINAL_LANG_MAP.get(language_code)  # e.g. "hi"

    for page in range(1, pages + 1):
        try:
            params = {
                "api_key":   API_KEY,
                "language":  base_lang,
                "with_genres": genre_id,
                "sort_by":   "vote_count.desc",
                "page":      page
            }

            # ✅ This is the key fix — restrict to movies originally in this language
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
            print(
                f"  {language_code} | Genre {genre_id} | Page {page}"
                f" → {len(results)} movies"
            )

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
    """
    Fetch movies for all languages and genres and save to SQLite.

    Args:
        incremental: If True (default), skip movies already in the DB.
                     If False, re-fetch everything (slow, use rarely).
    """
    init_db()
    existing_ids = get_existing_ids() if incremental else set()

    if incremental and existing_ids:
        print(f"📦 Incremental mode: {len(existing_ids)} movies already in DB. Skipping duplicates.")
    else:
        print("🔄 Full fetch mode.")

    total_tasks = len(LANGUAGES) * len(GENRE_MAP)
    current_task = 0
    total_new = 0

    for lang_name, lang_code in LANGUAGES.items():
        # Use per-language page count from config
        pages = PAGES_PER_LANGUAGE_dict.get(lang_code, 5)

        for genre_id, genre_name in GENRE_MAP.items():
            current_task += 1
            print(
                f"\n[{current_task}/{total_tasks}] {lang_name} - {genre_name}"
                f" ({pages} pages)",
                flush=True
            )

            movies = fetch_movies(lang_code, genre_id, pages)

            # Filter out movies already in DB (incremental update)
            new_movies = [m for m in movies if m["id"] not in existing_ids]
            existing_ids.update(m["id"] for m in new_movies)

            save_movies(new_movies)
            total_new += len(new_movies)
            print(f"   → {len(new_movies)} new movies saved (skipped {len(movies) - len(new_movies)})")

    print(f"\n✅ Done. {total_new} new movies added to database.")