# update_trending_cache.py
import requests
import json
import os
from datetime import datetime

def fetch_trending_movies():
    """Fetch trending movies using Streaming Availability API via RapidAPI."""
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        raise Exception("RAPIDAPI_KEY environment variable not set")
    
    url = "https://streaming-availability.p.rapidapi.com/search/title"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
    }
    
    # Search for popular movies (using a generic popular keyword)
    # Note: The API doesn't have a dedicated 'trending' endpoint, so we search for 'popular' 
    # and take the results. You can adjust the query to 'top', 'trending', etc.
    params = {
        "title": "popular",  # This returns popular results
        "country": "us",
        "show_type": "movie",
        "output_language": "en"
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    results = data.get('result', [])
    return results[:50]  # Keep top 50

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
    print("🔄 Fetching trending movies from RapidAPI...")
    trending = fetch_trending_movies()
    save_trending_cache(trending)
    print("🎉 Done!")
