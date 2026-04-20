import requests
import json
from datetime import datetime

def fetch_trending_movies():
    """
    Fetch top movies from a reliable public JSON source.
    Uses multiple fallback URLs in case one fails.
    """
    # List of verified working URLs (all return IMDb Top 250 in JSON)
    urls = [
        "https://raw.githubusercontent.com/atul-g/IMDb-Top-250-Movies/master/top250.json",
        "https://raw.githubusercontent.com/harsh4870/IMDB-Top-250/master/top250.json",
        "https://raw.githubusercontent.com/sj611595/IMDB-Top-250/master/IMDB-Top-250.json"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully fetched from: {url}")
                break
        except:
            continue
    else:
        raise Exception("All movie data sources failed. Please check internet or URLs.")
    
    # Handle different JSON structures
    if isinstance(data, list):
        movies_list = data
    elif isinstance(data, dict):
        # Try common keys
        movies_list = data.get('items', data.get('movies', data.get('results', [])))
        if not movies_list:
            movies_list = list(data.values())[0] if data else []
    else:
        movies_list = []
    
    movies = []
    for item in movies_list[:50]:
        # Extract title
        title = item.get('title') or item.get('Title') or item.get('name') or 'Unknown'
        # Extract year
        year_raw = item.get('year') or item.get('Year') or item.get('release_date') or 'N/A'
        if isinstance(year_raw, str) and len(year_raw) > 4:
            year = year_raw[:4]
        else:
            year = str(year_raw)
        # Extract rating
        rating = item.get('rating') or item.get('Rating') or item.get('imdbRating') or 'N/A'
        # Extract poster
        poster = item.get('poster') or item.get('Poster') or item.get('image') or ''
        
        movies.append({
            "title": title,
            "year": year,
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
