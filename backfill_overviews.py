"""
backfill_overviews.py
---------------------
Fetches English overviews from TMDB for movies that have a blank/missing
overview. Uses the /movie/{id} endpoint with language=en-US.

Safe to run multiple times — only processes rows where overview is empty.
Does NOT overwrite existing overviews.

Usage:
    python backfill_overviews.py
"""

import sqlite3
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import API_KEY, BASE_URL

DB_FILE = "movies.db"

session = requests.Session()
retry = Retry(total=5, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


def fetch_overview(movie_id: int) -> str | None:
    """Fetch English overview for a movie from TMDB."""
    try:
        r = session.get(
            f"{BASE_URL}/movie/{movie_id}",
            params={"api_key": API_KEY, "language": "en-US"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json().get("overview") or None
    except Exception as e:
        print(f"  ⚠️  Error fetching overview for {movie_id}: {e}")
    return None


def backfill():
    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        "SELECT id, title, language FROM movies WHERE overview IS NULL OR overview = ''"
    ).fetchall()

    if not rows:
        print("✅ All movies already have overviews — nothing to backfill.")
        conn.close()
        return

    # Summary before starting
    from collections import Counter
    lang_counts = Counter(r[2] for r in rows)
    print(f"📋 Movies missing overviews: {len(rows)}")
    for lang, count in lang_counts.most_common():
        print(f"   {lang}: {count}")
    print()

    updated  = 0
    still_empty = 0

    for i, (movie_id, title, lang) in enumerate(rows, 1):
        overview = fetch_overview(movie_id)

        if overview and overview.strip():
            conn.execute(
                "UPDATE movies SET overview = ? WHERE id = ?",
                (overview.strip(), movie_id)
            )
            updated += 1
        else:
            still_empty += 1

        if i % 100 == 0:
            conn.commit()
            print(f"   → {i}/{len(rows)} processed | {updated} filled | {still_empty} still empty")

        time.sleep(0.25)

    conn.commit()
    conn.close()

    print(f"\n✅ Done.")
    print(f"   {updated} movies now have an overview.")
    print(f"   {still_empty} movies have no English overview on TMDB (will be excluded from story mode).")

    if still_empty > 0:
        print(f"\n💡 Tip: movies with no overview anywhere are best excluded from story mode.")
        print(f"   Consider filtering them out in text_similarity.py when building the TF-IDF matrix.")


if __name__ == "__main__":
    backfill()