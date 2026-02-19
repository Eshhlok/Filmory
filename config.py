API_KEY = "47972814d2bdf0a22af797337fe5f25f"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

REQUEST_TIMEOUT = 10
REQUEST_SLEEP = 0.3

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
PAGES_PER_LANGUAGE=5
PAGES_PER_LANGUAGE_dict ={
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