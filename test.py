# test_data_store.py
from data_store import load_movies

df = load_movies()
print(df.head())
print(len(df))
print(df.columns)
