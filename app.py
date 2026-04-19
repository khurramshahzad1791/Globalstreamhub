import streamlit as st
import requests
import re
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------
st.set_page_config(page_title="Global FAST Stream Hub", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .movie-card:hover { transform: scale(1.02); transition: transform 0.2s; }
    hr { margin-top: 1rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("🌍 Global FAST Stream Hub")
st.caption("Your passport to free, ad-supported movies & live TV from around the world.")

# -------------------------------
# RAPIDAPI SETUP
# -------------------------------
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "streaming-availability.p.rapidapi.com"

if not RAPIDAPI_KEY:
    st.error("⚠️ Missing RapidAPI key. Please add it to your Streamlit secrets (RAPIDAPI_KEY).")
    st.stop()

# -------------------------------
# COUNTRY SELECTION
# -------------------------------
countries = {
    "United States": "us", "United Kingdom": "gb", "Canada": "ca", "Australia": "au",
    "Germany": "de", "France": "fr", "India": "in", "Pakistan": "pk", "China": "cn",
    "Russia": "ru", "Philippines": "ph", "South Korea": "kr", "Japan": "jp",
    "Turkey": "tr", "UAE": "ae", "Saudi Arabia": "sa", "Vietnam": "vn",
    "Thailand": "th", "Indonesia": "id", "Malaysia": "my"
}
selected_country = st.sidebar.selectbox("🌍 Select your country", list(countries.keys()), index=0)
country_code = countries[selected_country]

# -------------------------------
# COUNTRY-SPECIFIC M3U PLAYLISTS
# -------------------------------
COUNTRY_PLAYLISTS = {
    "India": "https://iptv-org.github.io/iptv/countries/in.m3u",
    "Pakistan": "https://iptv-org.github.io/iptv/countries/pk.m3u",
    "Philippines": "https://iptv-org.github.io/iptv/countries/ph.m3u",
    "South Korea": "https://iptv-org.github.io/iptv/countries/kr.m3u",
    "Japan": "https://iptv-org.github.io/iptv/countries/jp.m3u",
    "Indonesia": "https://iptv-org.github.io/iptv/countries/id.m3u",
    "Vietnam": "https://iptv-org.github.io/iptv/countries/vn.m3u",
    "Thailand": "https://iptv-org.github.io/iptv/countries/th.m3u",
    "Malaysia": "https://iptv-org.github.io/iptv/countries/my.m3u",
    "China": "https://iptv-org.github.io/iptv/countries/cn.m3u",
    "Russia": "https://iptv-org.github.io/iptv/countries/ru.m3u",
    "Turkey": "https://iptv-org.github.io/iptv/countries/tr.m3u",
    "UAE": "https://iptv-org.github.io/iptv/countries/ae.m3u",
    "Saudi Arabia": "https://iptv-org.github.io/iptv/countries/sa.m3u",
    "Germany": "https://iptv-org.github.io/iptv/countries/de.m3u",
    "France": "https://iptv-org.github.io/iptv/countries/fr.m3u",
    "United States": "https://iptv-org.github.io/iptv/countries/us.m3u",
    "United Kingdom": "https://iptv-org.github.io/iptv/countries/gb.m3u",
    "Canada": "https://iptv-org.github.io/iptv/countries/ca.m3u",
    "Australia": "https://iptv-org.github.io/iptv/countries/au.m3u",
}
GLOBAL_PLAYLIST = "https://iptv-org.github.io/iptv/index.m3u"

# -------------------------------
# FREE STREAMING SERVICES
# -------------------------------
FREE_SERVICES = {
    "Tubi": "https://tubitv.com", "Plex": "https://watch.plex.tv", "Pluto TV": "https://pluto.tv",
    "Crackle": "https://www.crackle.com", "Xumo Play": "https://play.xumo.com",
    "Popcornflix": "https://popcornflix.com", "Kanopy": "https://www.kanopy.com",
    "Roku Channel": "https://therokuchannel.roku.com"
}

# -------------------------------
# SESSION & CACHING
# -------------------------------
session = requests.Session()
retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

# -------------------------------
# FUNCTION: LOAD TRENDING MOVIES FROM LOCAL JSON
# -------------------------------
@st.cache_data(ttl=43200, show_spinner=False)  # 12 hours cache
def load_trending_movies():
    """Load trending movies from the locally cached JSON file (updated daily by GitHub Action)."""
    try:
        with open('trending_movies.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('movies', [])
    except FileNotFoundError:
        st.warning("⚠️ Trending movies list is being prepared. Please check back later.")
        return []
    except json.JSONDecodeError:
        st.error("⚠️ Error reading trending movies cache.")
        return []

# -------------------------------
# FUNCTION: FETCH M3U PLAYLIST (unchanged)
# -------------------------------
@st.cache_data(ttl=7200, show_spinner=False)
def fetch_m3u_playlist(url):
    try:
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            return []
        content = response.text
        channels = []
        lines = content.split('\n')
        current = {}
        for line in lines:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                name_match = re.search(r'#EXTINF:-1.*?,(.*?)$', line)
                if name_match:
                    current['name'] = name_match.group(1).strip()
                logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                if logo_match:
                    current['logo'] = logo_match.group(1)
                group_match = re.search(r'group-title="([^"]+)"', line)
                if group_match:
                    current['group'] = group_match.group(1)
            elif line.startswith('http') and current:
                current['stream_url'] = line
                if current.get('stream_url') and current.get('name'):
                    channels.append(current.copy())
                current = {}
        return channels[:300]
    except Exception as e:
        st.error(f"Error fetching playlist: {e}")
        return []

def fetch_all_country_channels(selected_country):
    playlist_url = COUNTRY_PLAYLISTS.get(selected_country)
    if playlist_url:
        channels = fetch_m3u_playlist(playlist_url)
        if channels:
            return channels
    st.info(f"Using global playlist filtered for {selected_country}...")
    all_channels = fetch_m3u_playlist(GLOBAL_PLAYLIST)
    filtered = []
    for ch in all_channels:
        name = ch.get('name', '').lower()
        if country_code in name or selected_country.lower() in name:
            filtered.append(ch)
    return filtered

# -------------------------------
# MOVIE SEARCH FUNCTION (RapidAPI)
# -------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def search_movies_rapidapi(query, country):
    if not RAPIDAPI_KEY:
        return []
    try:
        url = "https://streaming-availability.p.rapidapi.com/search/title"
        params = {"title": query, "country": country, "show_type": "movie", "output_language": "en"}
        headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}
        resp = session.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('result', []) if isinstance(data, dict) else data
        return []
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

def get_streaming_link(movie_data, service_name):
    if not movie_data or 'streamingInfo' not in movie_data:
        return None
    mapping = {"tubi":"tubi","plex":"plex","pluto tv":"pluto","crackle":"crackle",
               "xumo play":"xumo","popcornflix":"popcornflix","kanopy":"kanopy","roku channel":"roku"}
    key = mapping.get(service_name.lower())
    if not key:
        return None
    info = movie_data.get('streamingInfo', {}).get(country_code, {})
    return info.get(key, {}).get('link')

# -------------------------------
# UI TABS (Now with Trending Tab)
# -------------------------------
tab_trending, tab_live, tab_movies, tab_search = st.tabs(["🔥 Trending Now", "📡 Live TV", "🎬 Free Services", "🔍 Search"])

# ========== TRENDING NOW TAB ==========
with tab_trending:
    st.subheader(f"🔥 Trending Movies in {selected_country}")
    st.caption("Popular movies updated daily. Click any movie to see where you can watch it for free.")
    
    trending_movies = load_trending_movies()
    
    if trending_movies:
        # Show first 20 trending movies in a grid
        for i in range(0, min(len(trending_movies), 20), 4):
            cols = st.columns(4)
            for j in range(4):
                idx = i + j
                if idx < len(trending_movies):
                    movie = trending_movies[idx]
                    title = movie.get('title', 'Unknown')
                    year = movie.get('year', 'N/A')
                    rating = movie.get('imdbRating', 'N/A')
                    poster = movie.get('posterPath', '')
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
                    
                    with cols[j]:
                        if poster_url:
                            st.image(poster_url, width=150)
                        else:
                            st.image("https://via.placeholder.com/150x225?text=No+Poster", width=150)
                        st.markdown(f"**{title}** ({year})")
                        st.caption(f"⭐ {rating}")
                        
                        # Button to search for this movie
                        if st.button(f"🔍 Find '{title}'", key=f"trending_{idx}_{title}"):
                            with st.spinner(f"Searching for {title}..."):
                                results = search_movies_rapidapi(title, country_code)
                                if results:
                                    movie_data = results[0]
                                    links = [(s, get_streaming_link(movie_data, s)) for s in FREE_SERVICES if get_streaming_link(movie_data, s)]
                                    if links:
                                        st.markdown("**🍿 Watch for free on:**")
                                        for srv, link in links[:4]:
                                            st.link_button(srv, link, use_container_width=True)
                                    else:
                                        st.info(f"⚠️ '{title}' not available on free services in {selected_country}.")
                                else:
                                    st.info(f"Could not find streaming info for '{title}'.")
                        st.divider()
    else:
        st.info("Trending movies will appear here after the first daily update. Please check back later.")

# ========== LIVE TV TAB (unchanged) ==========
with tab_live:
    st.subheader(f"📡 Live TV Channels - {selected_country}")
    if st.button("🔄 Refresh Channels"):
        st.cache_data.clear()
        st.rerun()
    with st.spinner(f"Loading channels for {selected_country}..."):
        channels = fetch_all_country_channels(selected_country)
    if channels:
        st.success(f"✅ {len(channels)} channels found")
        for i in range(0, min(len(channels), 100), 4):
            cols = st.columns(4)
            for j in range(4):
                idx = i+j
                if idx < len(channels):
                    ch = channels[idx]
                    with cols[j]:
                        with st.expander(f"📺 {ch.get('name','')[:50]}", expanded=False):
                            if ch.get('logo'):
                                st.image(ch['logo'], width=100)
                            if ch.get('group'):
                                st.caption(f"📁 {ch['group']}")
                            st.link_button("▶️ Watch", ch.get('stream_url','#'), use_container_width=True)
    else:
        st.warning(f"No channels found for {selected_country}. Try another country.")
        st.info("💡 Note: Free IPTV playlists rely on community-maintained sources.")

# ========== FREE SERVICES TAB (unchanged) ==========
with tab_movies:
    st.subheader("🎬 Browse Free Streaming Services")
    st.caption("These services are free, ad-supported, and available in select regions.")
    cols = st.columns(4)
    for idx, (name, url) in enumerate(FREE_SERVICES.items()):
        with cols[idx % 4]:
            st.markdown(f"### {name}")
            st.link_button(f"Open {name} →", url, use_container_width=True)
            st.caption("Free, ad-supported")

# ========== SEARCH TAB (unchanged) ==========
with tab_search:
    st.subheader(f"🔍 Search Movies in {selected_country}")
    st.caption("Search for any movie – we'll show you all free, legal places to watch it.")
    query = st.text_input("Enter movie title", placeholder="e.g., 3 Idiots, Parasite, Train to Busan...")
    if query:
        with st.spinner(f"Searching for '{query}' in {selected_country}..."):
            results = search_movies_rapidapi(query, country_code)
        if results:
            st.success(f"✨ Found {len(results)} results")
            for movie in results[:20]:
                title = movie.get('title', 'Unknown')
                year = movie.get('year', 'N/A')
                rating = movie.get('imdbRating', 'N/A')
                overview = movie.get('overview', '')[:300]
                poster = movie.get('posterPath', '')
                poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
                col1, col2 = st.columns([1,3])
                with col1:
                    st.image(poster_url or "https://via.placeholder.com/150x225?text=No+Poster", width=150)
                with col2:
                    st.markdown(f"### {title} ({year})")
                    st.caption(f"⭐ {rating}")
                    st.write(overview)
                    links = [(s, get_streaming_link(movie, s)) for s in FREE_SERVICES if get_streaming_link(movie, s)]
                    if links:
                        st.markdown("**🍿 Watch for free on:**")
                        for srv, link in links[:4]:
                            st.link_button(srv, link, use_container_width=True)
                    else:
                        st.info(f"⚠️ Not available on free services in {selected_country}.")
                st.divider()
        else:
            st.info(f"No movies found for '{query}' in {selected_country}.")

st.divider()
st.caption(f"Global FAST Stream Hub • Aggregates free ad-supported content • Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
