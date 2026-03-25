# data_store.py
import sys
import time
import os
from urllib import response
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import *
import ast

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)



def fetch_movies(language_code, genre_id, pages=PAGES_PER_LANGUAGE):
    movies = []

    for page in range(1, pages + 1):
        try:
            base_lang = language_code.split("-")[0]
            response = session.get(
                f"{BASE_URL}/discover/movie",
                params={
                    "api_key": API_KEY,
                    "language": base_lang,
                    "with_genres": genre_id,
                    "sort_by": "vote_count.desc",
                    "page": page
                },
                timeout=REQUEST_TIMEOUT
            )
            #print("STATUS:", response.status_code)
            #print("URL:", response.url)
            #print("RAW:", response.text[:200])


            if response.status_code == 429:
                print("Rate limited. Sleeping 5 seconds...")
                time.sleep(5)
                continue

            if response.status_code != 200:
                print(f"⚠️ Failed {language_code} page {page}")
                break

            data = response.json()
            results = data.get("results", [])

            print(
                f"{language_code} | Genre {genre_id} | Page {page} "
                f"→ {len(results)} movies"
            )

            if not results:
                break

            for m in results:
                movies.append({
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "overview": m.get("overview") or "",
                    "poster_url": (
                        IMAGE_BASE_URL + m["poster_path"]
                        if m.get("poster_path") else None
                    ),
                    "rating": m.get("vote_average"),
                    "release_date": m.get("release_date"),
                    "language": m.get("original_language"),
                    "genre_ids": m.get("genre_ids", [])
                })

            time.sleep(REQUEST_SLEEP)

        except Exception as e:
            print(f"❌ Error fetching {language_code} page {page}: {e}")
            break

    return movies


CACHE_FILE = "movies_cache.csv"
def load_movies(force_refresh=True):
    all_movies = []
    if os.path.exists(CACHE_FILE) and not force_refresh:
        print("Loading movies from local cache...")
        df = pd.read_csv(CACHE_FILE)
        required_columns = {"id", "title", "overview", "genre_ids"}
        if required_columns.issubset(df.columns):
            if "genre_ids" in df.columns:
                df["genre_ids"] = df["genre_ids"].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                )
            print(f"Loaded {len(df)} movies from cache.")
            return df
        else:
            print("⚠️ Cache schema outdated. Rebuilding dataset...")
    
    print("Fetching movies from TMDB...")

    total_tasks = len(LANGUAGES) * len(GENRE_MAP)
    current_task = 0

    for lang_name, lang_code in LANGUAGES.items():
        for genre_id, genre_name in GENRE_MAP.items():
            current_task += 1

            print(
                f"[{current_task}/{total_tasks}] "
                f"{lang_name} - {genre_name}",
                flush=True
            )

            movies = fetch_movies(lang_code, genre_id, pages=PAGES_PER_LANGUAGE)
            print(f"   → Fetched {len(movies)} movies")

            all_movies.extend(movies)



    movies_df = pd.DataFrame(all_movies)
    if movies_df.empty:
        raise RuntimeError("❌ No movies fetched. Aborting cache save.")

    # IMPORTANT: stable index
    movies_df.drop_duplicates(subset=["id"], inplace=True)
    movies_df.to_csv(CACHE_FILE, index=False)
    print("Columns:", movies_df.columns)
    print("Total movies:", len(movies_df))

    print("Saved dataset to cache.")
    return movies_df
