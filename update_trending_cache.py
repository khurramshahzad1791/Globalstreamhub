import requests
import json
from datetime import datetime

def fetch_trending_movies():
    url = "https://raw.githubusercontent.com/sj611595/IMDB-Top-250/master/IMDB-Top-250.json"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    movies = []
    for item in data[:50]:
        year_str = item.get("year", "")
        year = year_str[:4] if year_str else "N/A"
        movies.append({
            "title": item.get("title", "Unknown"),
            "year": year,
            "imdbRating": item.get("rating", "N/A"),
            "posterPath": item.get("poster", "")
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
