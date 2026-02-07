# data_store.py

import time
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import *

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

def fetch_movies(language_code, pages=PAGES_PER_LANGUAGE):
    movies = []

    for page in range(1, pages + 1):
        try:
            response = session.get(
                f"{BASE_URL}/discover/movie",
                params={
                    "api_key": API_KEY,
                    "language": language_code,
                    "sort_by": "popularity.desc",
                    "page": page
                },
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                print(f"⚠️ Failed {language_code} page {page}")
                break

            data = response.json()
            if "results" not in data:
                break
            for m in data.get("results", []):
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


def load_movies():
    all_movies = []

    for _, lang_code in LANGUAGES.items():
        all_movies.extend(fetch_movies(lang_code))

    df = pd.DataFrame(all_movies)

    # IMPORTANT: stable index
    df = df.dropna(subset=["title"]).reset_index(drop=True)

    return df
