"""
backfill_backdrops.py
---------------------
Fetches backdrop_path from TMDB for all existing movies that have
backdrop_url = NULL, and saves them to the DB.

Run ONCE after migrate_backdrop.py.
After this, update_db.py will keep new movies up to date automatically.

Usage:
    python backfill_backdrops.py
"""

import sqlite3
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import API_KEY, BASE_URL, IMAGE_BASE_URL

DB_FILE = "movies.db"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"

session = requests.Session()
retry = Retry(total=5, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


def fetch_backdrop(movie_id: int) -> str | None:
    try:
        r = session.get(
            f"{BASE_URL}/movie/{movie_id}",
            params={"api_key": API_KEY, "fields": "backdrop_path"},
            timeout=10
        )
        if r.status_code == 200:
            path = r.json().get("backdrop_path")
            return BACKDROP_BASE_URL + path if path else None
    except Exception as e:
        print(f"  ⚠️  Error fetching backdrop for {movie_id}: {e}")
    return None


def backfill():
    conn = sqlite3.connect(DB_FILE)

    # Check migration has been run
    cols = [r[1] for r in conn.execute("PRAGMA table_info(movies)").fetchall()]
    if "backdrop_url" not in cols:
        print("❌ backdrop_url column not found. Run migrate_backdrop.py first.")
        conn.close()
        return

    rows = conn.execute(
        "SELECT id FROM movies WHERE backdrop_url IS NULL"
    ).fetchall()

    if not rows:
        print("✅ All movies already have backdrop_url — nothing to backfill.")
        conn.close()
        return

    print(f"🎬 Backfilling backdrops for {len(rows)} movies...")
    updated = 0

    for i, (movie_id,) in enumerate(rows, 1):
        backdrop = fetch_backdrop(movie_id)
        conn.execute(
            "UPDATE movies SET backdrop_url = ? WHERE id = ?",
            (backdrop, movie_id)
        )

        if i % 50 == 0:
            conn.commit()
            print(f"   → {i}/{len(rows)} done ({updated} with backdrops)")

        if backdrop:
            updated += 1

        time.sleep(0.25)  # stay well within TMDB rate limits

    conn.commit()
    conn.close()
    print(f"\n✅ Done. {updated}/{len(rows)} movies now have a backdrop_url.")


if __name__ == "__main__":
    backfill()