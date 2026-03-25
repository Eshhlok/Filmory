#When you want to update → manually run python update_db.py,
# it only fetches new movies and adds them to the DB
from data_store import fetch_all_movies

print("🔄 Updating database with new movies...")
fetch_all_movies(incremental=True)
print("✅ Done!")