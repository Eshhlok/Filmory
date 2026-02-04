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

PAGES_PER_LANGUAGE = 5
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
        response = session.get(
            f"{BASE_URL}/discover/movie",
            params={
                "api_key": API_KEY,
                "language": language_code,
                "sort_by": "popularity.desc",
                "page": page
            },
            timeout=10
        )
        if response.status_code != 200:
            print(f"⚠️ Failed request for {language_code}, page {page}")
            continue

        data = response.json()
        if "results" not in data:
            continue
        


        for m in data["results"]:
                movies.append({
                    "title": m.get("title"),
                    "overview": m.get("overview", ""),
                    "poster_url": IMAGE_BASE_URL + m["poster_path"] if m.get("poster_path") else None,
                    "rating": m.get("vote_average"),
                    "release_date": m.get("release_date"),
                    "language": language_code
                })
        time.sleep(1.5)
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


# =========================
# BUILD DATASET
# =========================
all_movies = []

for lang, code in LANGUAGES.items():
    print(f"Fetching {lang} movies...")
    all_movies.extend(fetch_movies(code, PAGES_PER_LANGUAGE))

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
def recommend(movie_title, top_n=5):
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
    idx = titles[titles == movie_title.lower()].index[0]

    similarity_scores = list(enumerate(cosine_sim[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i in similarity_scores[1:top_n + 1]:
        movie = movies_df.iloc[i[0]]
        recommendations.append({
            "title": movie["title"],
            "overview": movie["overview"],
            "poster_url": movie["poster_url"],
            "rating": movie["rating"],
            "release_date": movie["release_date"],
            "language": movie["language"]
        })

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
