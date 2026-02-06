import requests


session = requests.Session()
CAST_CACHE = {}
DIRECTOR_CACHE = {}

API_KEY = "47972814d2bdf0a22af797337fe5f25f"
BASE_URL = "https://api.themoviedb.org/3"

def search_movies_tmdb(query, page=1):
    response = session.get(
        f"{BASE_URL}/search/movie",
        params={
            "api_key": API_KEY,
            "query": query
        },
        timeout=10
    )

    if response.status_code != 200:
        return []

    return response.json().get("results", [])

def get_cast_and_director(movie_id):
    if not movie_id:
        return [], []

    if movie_id in CAST_CACHE:
        return CAST_CACHE[movie_id], DIRECTOR_CACHE[movie_id]
    
    response = session.get(
        f"{BASE_URL}/movie/{movie_id}/credits",
        params={"api_key": API_KEY},
        timeout=10
    )

    if response.status_code != 200:
        CAST_CACHE[movie_id] = []
        DIRECTOR_CACHE[movie_id] = []
        return [], []

    data = response.json()

    cast = [c["name"] for c in data.get("cast", [])[:10]]
    director = [
        c["name"] for c in data.get("crew", [])
        if c.get("job") == "Director"
    ]

    CAST_CACHE[movie_id] = cast
    DIRECTOR_CACHE[movie_id] = director

    return cast, director

