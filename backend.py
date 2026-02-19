from data_store import load_movies
from text_similarity import build_text_similarity
movies_df = load_movies()
movies_df.reset_index(drop=True, inplace=True)  
tfidf, cosine_sim = build_text_similarity(movies_df)
