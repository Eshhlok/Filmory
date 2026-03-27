"""
migrate_to_postgres.py
----------------------
One-time script: copies all data from your local movies.db (SQLite)
into a Supabase/PostgreSQL database.

Run this ONCE from your local machine before deploying.

Prerequisites:
    pip install psycopg2-binary

Usage:
    DATABASE_URL="postgresql://..." python migrate_to_postgres.py
"""

import os
import json
import sqlite3
import psycopg2
import psycopg2.extras

SQLITE_FILE  = "movies.db"
DATABASE_URL = os.environ["DATABASE_URL"]


def migrate():
    print("🔌 Connecting to PostgreSQL...")
    pg = psycopg2.connect(DATABASE_URL)
    pg_cur = pg.cursor()

    print("📂 Opening SQLite...")
    sq = sqlite3.connect(SQLITE_FILE)
    sq.row_factory = sqlite3.Row

    # ── Create tables ─────────────────────────────────────────────────
    print("🏗️  Creating tables...")
    pg_cur.execute("""
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

    pg_cur.execute("""
        CREATE TABLE IF NOT EXISTS credits (
            movie_id         INTEGER PRIMARY KEY,
            top_billed_actor TEXT,
            full_cast        TEXT,
            directors        TEXT
        )
    """)

    pg_cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id         SERIAL PRIMARY KEY,
            rating     SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            comment    VARCHAR(500),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    pg.commit()

    # ── Migrate movies ────────────────────────────────────────────────
    movies = sq.execute("SELECT * FROM movies").fetchall()
    print(f"🎬 Migrating {len(movies)} movies...")

    rows = [
        (
            m["id"], m["title"], m["overview"],
            m["poster_url"], m["backdrop_url"] if "backdrop_url" in m.keys() else None,
            m["rating"], m["release_date"],
            m["language"], m["genre_ids"]
        )
        for m in movies
    ]

    psycopg2.extras.execute_batch(
        pg_cur,
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
    pg.commit()
    print(f"   ✅ {len(movies)} movies migrated.")

    # ── Migrate credits ───────────────────────────────────────────────
    credits = sq.execute("SELECT * FROM credits").fetchall()
    print(f"🎭 Migrating {len(credits)} credit rows...")

    credit_rows = [
        (c["movie_id"], c["top_billed_actor"], c["full_cast"], c["directors"])
        for c in credits
    ]

    psycopg2.extras.execute_batch(
        pg_cur,
        """
        INSERT INTO credits (movie_id, top_billed_actor, full_cast, directors)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (movie_id) DO NOTHING
        """,
        credit_rows,
        page_size=500
    )
    pg.commit()
    print(f"   ✅ {len(credits)} credit rows migrated.")

    sq.close()
    pg_cur.close()
    pg.close()

    print("\n✅ Migration complete. Your PostgreSQL database is ready.")
    print("   You can now deploy to Render and set DATABASE_URL in environment variables.")


if __name__ == "__main__":
    migrate()