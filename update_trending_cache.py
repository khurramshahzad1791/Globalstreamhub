import requests
import json
from datetime import datetime

def fetch_trending_movies():
    # Working public JSON of IMDb Top 250 movies
    url = "https://raw.githubusercontent.com/ShariqAnsari/IMDB-Top-250-Movies/master/top250.json"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    movies = []
    for item in data[:50]:
        title = item.get("Title", "Unknown")
        year = item.get("Year", "N/A")
        rating = item.get("Rating", "N/A")
        poster = item.get("Poster", "")
        movies.append({
            "title": title,
            "year": str(year)[:4],
            "imdbRating": rating,
            "posterPath": poster
        })
    return movies

def save_trending_cache(movies):
    cache_data = {
        "last_updated": datetime.now().isoformat(),
        "movie_count": len(movies),
        "movies": movies
    }
    with open('trending_movies.json', 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(movies)} movies to trending_movies.json")

if __name__ == "__main__":
    print("🔄 Fetching top movies from public dataset...")
    movies = fetch_trending_movies()
    save_trending_cache(movies)
    print("🎉 Done!")
