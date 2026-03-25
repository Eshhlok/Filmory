from data_store import init_db, load_movies
from text_similarity import build_text_similarity, build_features

init_db()
movies_df = load_movies()
movies_df.reset_index(drop=True, inplace=True)
movies_df = build_features(movies_df)
tfidf, cosine_sim = build_text_similarity(movies_df)