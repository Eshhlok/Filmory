from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = None
cosine_sim = None


def build_text_similarity(movies_df):
    global tfidf_matrix, cosine_sim
    tfidf_matrix = tfidf.fit_transform(movies_df["overview"])
    cosine_sim = cosine_similarity(tfidf_matrix)


def get_story_similarities(seed_index):
    if cosine_sim is None:
        return []
    return list(enumerate(cosine_sim[seed_index]))
