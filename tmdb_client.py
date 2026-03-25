import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from functools import lru_cache
from config import API_KEY, BASE_URL

session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


def search_movies_tmdb(query, page=1):
    try:
        response = session.get(
            f"{BASE_URL}/search/movie",
            params={"api_key": API_KEY, "query": query},
            timeout=10
        )
        time.sleep(0.3)
        if response.status_code != 200:
            return []
        return response.json().get("results", [])
    except requests.exceptions.RequestException:
        return []


@lru_cache(maxsize=4096)
def get_cast_and_director(movie_id):
    """
    Returns (cast_list, director_list) for a movie.
    cast_list is sorted by TMDB's official billing order field.
    So index 0 is always the top billed actor.
    """
    if not movie_id:
        return [], []

    try:
        response = session.get(
            f"{BASE_URL}/movie/{movie_id}/credits",
            params={"api_key": API_KEY},
            timeout=10
        )
        time.sleep(0.1)

        if response.status_code != 200:
            return [], []

        data = response.json()

        # ✅ Sort by TMDB's 'order' field — official billing order
        cast_sorted = sorted(
            data.get("cast", []),
            key=lambda x: x.get("order", 9999)
        )
        cast = [c["name"] for c in cast_sorted[:10]]

        director = [
            c["name"] for c in data.get("crew", [])
            if c.get("job") == "Director"
        ]

        return cast, director

    except Exception:
        return [], []