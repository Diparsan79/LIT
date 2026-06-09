import os
import requests
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def search_film(title):
    if not TMDB_API_KEY:
        return []
    
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            params ={
                "api_key": TMDB_API_KEY,
                "query": title,
            },
            timeout = 5
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])[:5]
    except Exception:
        return []
    
def get_film_details(tmdb_id):
    if not TMDB_API_KEY:
        return None
    
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={
                "api_key": TMDB_API_KEY,
                "append_to_response": "credits",
            },
            timeout = 5       
        )
        response.raise_for_status()
        data = response.json()

        director = ""
        crew = data.get("credits", {}).get("crew", [])
        for member in crew:
            if member.get("job") =="Director":
                director = member.get("name", "")
                break
        genres = [g["name"].lower() for g in data.get("genres", []) if "name" in g]

        release_date = str(data.get("release_date", ""))
        year_str = release_date[:4]
        year = int(year_str) if year_str.isdigit() else None

        return {
            "title": data.get("title", ""),
            "year": year,
            "director": director,
            "tags": genres,
            "poster_path": data.get("poster_path", "")
        }
    except Exception:
        return None
    
