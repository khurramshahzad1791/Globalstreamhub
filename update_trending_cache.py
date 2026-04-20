# update_trending_cache.py
import requests
import json
import os
from datetime import datetime

def fetch_trending_movies():
    """Fetch trending movies from IMDb Scraper API (free, no credit card)."""
    api_key = os.environ.get("IMDB_API_KEY")
    if not api_key:
        raise Exception("IMDB_API_KEY environment variable not set")
    
    url = "https://imdb-scraper-api.omkar.cloud/imdb/most-popular-movies"
    headers = {"API-Key": api_key}
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    # The API returns a list of movies. We'll map fields to match what app.py expects.
    movies = []
    for item in data[:50]:  # Limit to 50
        movies.append({
            "title": item.get("title", "Unknown"),
            "year": item.get("release_date", "")[:4] if item.get("release_date") else "N/A",
            "imdbRating": item.get("rating", "N/A"),
            "posterPath": item.get("poster", "")  # Poster URL
        })
    return movies

def save_trending_cache(movies):
    """Save trending movies to JSON file with metadata."""
    cache_data = {
        "last_updated": datetime.now().isoformat(),
        "movie_count": len(movies),
        "movies": movies
    }
    with open('trending_movies.json', 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(movies)} trending movies to trending_movies.json")

if __name__ == "__main__":
    print("🔄 Fetching trending movies from IMDb Scraper API...")
    trending = fetch_trending_movies()
    save_trending_cache(trending)
    print("🎉 Done!")
