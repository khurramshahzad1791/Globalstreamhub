import json
import requests
from datetime import datetime

# ============================================================
# STATIC FALLBACK LIST (used if online sources fail)
# ============================================================
FALLBACK_MOVIES = [
    {"title": "The Shawshank Redemption", "year": "1994", "imdbRating": "9.3", "posterPath": "https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_UX182_CR0,0,182,268_AL_.jpg"},
    {"title": "The Godfather", "year": "1972", "imdbRating": "9.2", "posterPath": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UY268_CR3,0,182,268_AL_.jpg"},
    {"title": "The Dark Knight", "year": "2008", "imdbRating": "9.0", "posterPath": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_UX182_CR0,0,182,268_AL_.jpg"},
    {"title": "Pulp Fiction", "year": "1994", "imdbRating": "8.9", "posterPath": "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_UY268_CR7,0,182,268_AL_.jpg"},
    {"title": "Schindler's List", "year": "1993", "imdbRating": "8.9", "posterPath": "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_UX182_CR0,0,182,268_AL_.jpg"},
    # Add more movies here (you can easily add up to 50)
]

def fetch_online_movies():
    """Try to get movies from public JSON sources. Return None if all fail."""
    urls = [
        "https://raw.githubusercontent.com/atul-g/IMDb-Top-250-Movies/master/top250.json",
        "https://raw.githubusercontent.com/harsh4870/IMDB-Top-250/master/top250.json",
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
        except:
            continue
    return None

def convert_to_unified_format(raw_movies):
    """Convert various JSON structures to our unified format."""
    unified = []
    for item in raw_movies[:50]:
        title = item.get('title') or item.get('Title') or 'Unknown'
        year_raw = item.get('year') or item.get('Year') or ''
        year = str(year_raw)[:4] if year_raw else 'N/A'
        rating = item.get('rating') or item.get('Rating') or item.get('imdbRating') or 'N/A'
        poster = item.get('poster') or item.get('Poster') or item.get('image') or ''
        unified.append({
            "title": title,
            "year": year,
            "imdbRating": rating,
            "posterPath": poster
        })
    return unified

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
    print("🔄 Fetching trending movies...")
    online_movies = fetch_online_movies()
    if online_movies:
        print("✅ Using online data.")
        movies = convert_to_unified_format(online_movies)
    else:
        print("⚠️ Online sources failed. Using fallback list.")
        movies = FALLBACK_MOVIES
    save_trending_cache(movies)
    print("🎉 Done!")
