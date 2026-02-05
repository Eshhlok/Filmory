import requests
import pandas as pd
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIG
# =========================
API_KEY = "47972814d2bdf0a22af797337fe5f25f"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

LANGUAGES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Korean": "ko-KR"
}

GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science-Fiction",
    10770: "Tv-Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}

PAGES_PER_LANGUAGE ={
    "en-US": 6,
    "hi-IN": 12,
    "ta-IN": 10,
    "te-IN": 10,
    "ko-KR": 8
}

ORIGINAL_LANG_MAP = {
    "en-US": None,   # English → no restriction
    "hi-IN": "hi",
    "ta-IN": "ta",
    "te-IN": "te",
    "ko-KR": "ko"
}

session = requests.Session()

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
# =========================
# FETCH MOVIES
# =========================
def fetch_movies(language_code, pages=5):
    movies = []

    for page in range(1, pages + 1):
        params={
                "api_key": API_KEY,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "page": page
            }
        original_lang= ORIGINAL_LANG_MAP.get(language_code)
        if original_lang:
            params["with_original_language"] = original_lang
        response = session.get(
            f"{BASE_URL}/discover/movie",
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            print(f"⚠️ Failed request for {language_code}, page {page}")
            continue

        data = response.json()
        if "results" not in data:
            continue
        


        for m in data["results"]:
                genre_ids = m.get("genre_ids", [])
                genre_names = [GENRE_MAP.get(g) for g in genre_ids if g in GENRE_MAP]
                genre_text = " ".join(genre_names)

                combined_text = (m.get("overview") or "") or " " + genre_text

                movies.append({
                    "title": m.get("title"),
                    "overview": combined_text,
                    "poster_url": IMAGE_BASE_URL + m["poster_path"] if m.get("poster_path") else None,
                    "rating": m.get("vote_average"),
                    "release_date": m.get("release_date"),
                    "language": m.get("original_language")
                })
        time.sleep(0.5)
    return movies

def search_movie_tmdb(movie_name):
    response = session.get(
        f"{BASE_URL}/search/movie",
        params={
            "api_key": API_KEY,
            "query": movie_name
        },
        timeout=10
    )

    if response.status_code != 200:
        return None

    data = response.json()
    if data["results"]:
        return data["results"][0]  # best match
    return None

def search_movies_tmdb(movie_name, page=1):
    response = session.get(
        f"{BASE_URL}/search/movie",
        params={
            "api_key": API_KEY,
            "query": movie_name,
            "page": page,
            "include_adult": True
        },
        timeout=10
    )

    if response.status_code != 200:
        return []

    data = response.json()
    return data.get("results", [])

# =========================
# BUILD DATASET
# =========================
all_movies = []

for lang, code in LANGUAGES.items():
    pages = PAGES_PER_LANGUAGE.get(code, 5)
    print(f"Fetching {lang} movies...")
    all_movies.extend(fetch_movies(code, pages))

movies_df = pd.DataFrame(all_movies)
movies_df.dropna(subset=["overview"], inplace=True)
movies_df.reset_index(drop=True, inplace=True)

print(f"Total movies loaded: {len(movies_df)}")

def rebuild_similarity():
    global tfidf_matrix, cosine_sim
    tfidf_matrix = tfidf.fit_transform(movies_df["overview"])
    cosine_sim = cosine_similarity(tfidf_matrix)


# =========================
# ML PIPELINE
# =========================
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(movies_df["overview"])

cosine_sim = cosine_similarity(tfidf_matrix)

# =========================
# RECOMMENDATION FUNCTION
# =========================
def recommend(movie_title, top_n=30,language_filter=None):
    movie_title = movie_title.lower().strip()
    titles = movies_df["title"].str.lower()

    if movie_title not in titles.values:
        tmdb_movie = search_movie_tmdb(movie_title)
        if not tmdb_movie:
            return []

    # temporarily add searched movie
        movies_df.loc[len(movies_df)] = {
            "title": tmdb_movie["title"],
            "overview": tmdb_movie["overview"],
            "poster_url": IMAGE_BASE_URL + tmdb_movie["poster_path"]
            if tmdb_movie.get("poster_path") else None,
            "rating": tmdb_movie["vote_average"],
            "release_date": tmdb_movie["release_date"],
            "language": tmdb_movie["original_language"]
            
        }

        rebuild_similarity()
        titles = movies_df["title"].str.lower()
        movie_title = tmdb_movie["title"].lower()

    matched_indices = titles[titles.str.contains(movie_title, regex=False)].index

    if len(matched_indices) == 0:
        return []   # no match found safely

    idx = matched_indices[0]
    selected_title = movies_df.iloc[idx]["title"]

    similarity_scores = list(enumerate(cosine_sim[idx]))

    # apply language conditioning
    if language_filter:
        similarity_scores = [
            (i, score)
            for i, score in similarity_scores
            if movies_df.iloc[i]["language"] == language_filter
            and movies_df.iloc[i]["title"] != selected_title
        ]
    else:
        similarity_scores = [
            (i, score)
            for i, score in similarity_scores
            if movies_df.iloc[i]["title"] != selected_title
        ]
    # sort after conditioning
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []
    seen_titles = set()
    for i, _ in similarity_scores:
        movie = movies_df.iloc[i]
        if movie["title"] in seen_titles:
            continue
        seen_titles.add(movie["title"])
        recommendations.append({
            "title": movie["title"],
            "overview": movie["overview"],
            "poster_url": movie["poster_url"],
            "rating": movie["rating"],
            "release_date": movie["release_date"],
            "language": movie["language"]
        })
        if len(recommendations) >= top_n:
            break

    return recommendations


# =========================
# TEST BACKEND
# =========================
if __name__ == "__main__":
    movie_name = input("Enter a movie name: ")
    results = recommend(movie_name)

    if not results:
        print("Movie not found.")
    else:
        for r in results:
            print("\n🎬", r["title"])
            print("⭐ Rating:", r["rating"])
            print("📅 Release:", r["release_date"])
            print("🌍 Language:", r["language"])
            print("📝", r["overview"][:150], "...")
# Feature branch: experimenting with advanced recommendations
