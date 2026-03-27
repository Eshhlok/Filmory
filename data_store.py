import time
import os
import json
import requests
import pandas as pd
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
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
# PostgreSQL connection pool
# ─────────────────────────────────────────────
DATABASE_URL = os.environ["DATABASE_URL"]   # set in Render environment variables

_pool: ThreadedConnectionPool | None = None


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
    return _pool


@contextmanager
def get_conn():
    """Borrow a connection from the pool, commit on success, rollback on error."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


# ─────────────────────────────────────────────
# Schema setup
# ─────────────────────────────────────────────
def init_db():
    """Create all tables if they don't exist."""
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id           INTEGER PRIMARY KEY,
                title        TEXT,
                overview     TEXT,
                poster_url   TEXT,
                backdrop_url TEXT,
                rating       REAL,
                release_date TEXT,
                language     TEXT,
                genre_ids    TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS credits (
                movie_id         INTEGER PRIMARY KEY,
                top_billed_actor TEXT,
                full_cast        TEXT,
                directors        TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id         SERIAL PRIMARY KEY,
                rating     SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                comment    VARCHAR(500),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

    print("✅ Database initialised.")


# ─────────────────────────────────────────────
# Movies
# ─────────────────────────────────────────────
def save_movies(movies: list[dict]):
    """Bulk-insert movies — ON CONFLICT DO NOTHING skips duplicates."""
    if not movies:
        return

    rows = [
        (
            m["id"], m["title"], m["overview"],
            m["poster_url"], m.get("backdrop_url"),
            m["rating"], m["release_date"],
            m["language"], json.dumps(m["genre_ids"])
        )
        for m in movies
    ]

    with get_conn() as conn:
        psycopg2.extras.execute_batch(
            conn.cursor(),
            """
            INSERT INTO movies
                (id, title, overview, poster_url, backdrop_url,
                 rating, release_date, language, genre_ids)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            rows,
            page_size=500
        )


def load_movies() -> pd.DataFrame:
    """Load all movies from PostgreSQL into a DataFrame."""
    with get_conn() as conn:
        df = pd.read_sql("SELECT * FROM movies", conn)

    if df.empty:
        raise RuntimeError("❌ No movies in database. Run fetch_all_movies() first.")

    df["genre_ids"] = df["genre_ids"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else []
    )
    print(f"✅ Loaded {len(df)} movies from database.")
    return df


def get_existing_ids() -> set:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM movies")
        return {row[0] for row in cur.fetchall()}


# ─────────────────────────────────────────────
# Credits
# ─────────────────────────────────────────────
def get_cached_credit_ids() -> set:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT movie_id FROM credits")
        return {row[0] for row in cur.fetchall()}


def save_credits(movie_id: int, top_billed_actor: str, full_cast: list, directors: list):
    with get_conn() as conn:
        conn.cursor().execute(
            """
            INSERT INTO credits (movie_id, top_billed_actor, full_cast, directors)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (movie_id) DO UPDATE SET
                top_billed_actor = EXCLUDED.top_billed_actor,
                full_cast        = EXCLUDED.full_cast,
                directors        = EXCLUDED.directors
            """,
            (movie_id, top_billed_actor, json.dumps(full_cast), json.dumps(directors))
        )


def load_credits() -> dict:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT movie_id, top_billed_actor, full_cast, directors FROM credits")
        rows = cur.fetchall()

    return {
        int(movie_id): {
            "top_billed_actor": top_billed_actor,
            "full_cast":        json.loads(full_cast) if full_cast else [],
            "directors":        json.loads(directors) if directors else []
        }
        for movie_id, top_billed_actor, full_cast, directors in rows
    }


def cache_all_credits(movies_df: pd.DataFrame):
    from tmdb_client import get_cast_and_director

    cached_ids = get_cached_credit_ids()
    missing = [
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
        save_credits(movie_id, cast[0] if cast else None, cast, directors)
        if i % 50 == 0:
            print(f"   → {i}/{len(missing)} cached...")

    print(f"✅ Credits cached for {len(missing)} movies.")


# ─────────────────────────────────────────────
# Feedback
# ─────────────────────────────────────────────
def save_feedback(rating: int, comment: str | None):
    """Save a global site feedback entry."""
    with get_conn() as conn:
        conn.cursor().execute(
            "INSERT INTO feedback (rating, comment) VALUES (%s, %s)",
            (rating, comment)
        )


# ─────────────────────────────────────────────
# TMDB fetching
# ─────────────────────────────────────────────
def fetch_movies(language_code: str, genre_id: int, pages: int) -> list[dict]:
    movies = []
    original_lang = ORIGINAL_LANG_MAP.get(language_code)

    for page in range(1, pages + 1):
        try:
            params = {
                "api_key":     API_KEY,
                "language":    "en-US",
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
            if not results:
                break

            for m in results:
                movies.append({
                    "id":           m.get("id"),
                    "title":        m.get("title"),
                    "overview":     m.get("overview") or "",
                    "poster_url":   IMAGE_BASE_URL + m["poster_path"] if m.get("poster_path") else None,
                    "backdrop_url": "https://image.tmdb.org/t/p/w1280" + m["backdrop_path"] if m.get("backdrop_path") else None,
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
    init_db()
    existing_ids = get_existing_ids() if incremental else set()

    total_tasks = len(LANGUAGES) * len(GENRE_MAP)
    current_task = total_new = 0

    for lang_name, lang_code in LANGUAGES.items():
        pages = PAGES_PER_LANGUAGE_dict.get(lang_code, 5)

        for genre_id, genre_name in GENRE_MAP.items():
            current_task += 1
            print(f"\n[{current_task}/{total_tasks}] {lang_name} - {genre_name} ({pages} pages)", flush=True)

            movies     = fetch_movies(lang_code, genre_id, pages)
            new_movies = [m for m in movies if m["id"] not in existing_ids]
            existing_ids.update(m["id"] for m in new_movies)

            save_movies(new_movies)
            total_new += len(new_movies)
            print(f"   → {len(new_movies)} new movies saved (skipped {len(movies) - len(new_movies)})")

    print(f"\n✅ Done. {total_new} new movies added to database.")