from people_similarity import _find_seed_movie
from data_store import load_movies, load_credits

movies_df = load_movies()
credits = load_credits()

# Step 1: Check what seed movie is found
idx, movie = _find_seed_movie(movies_df, "Pirates of the Caribbean: The Curse of the Black Pearl")
print("Found:", movie["title"] if movie is not None else "NOT FOUND")
print("ID:", movie["id"] if movie is not None else "N/A")

if movie is not None:
    seed_credits = credits.get(int(movie["id"]))
    print("Cast:", seed_credits)

    # Step 2: Check top scoring movies
    from people_similarity import get_people_recommendations
    results = get_people_recommendations(movies_df, movie["title"], top_n=5, mode="cast")
    for r in results:
        mid = movies_df[movies_df["title"] == r["title"]].iloc[0]["id"]
        c = credits.get(int(mid))
        print(f"\n→ {r['title']}")
        print(f"  Cast: {c['full_cast'] if c else 'NO CREDITS'}")