"""
Rhea Noir Module: actions.py
Auto-generated docstring.
"""
import os
import requests
from typing import Dict, Any, List, Optional
from ..base import Skill

class TmdbSkill(Skill):
    """
    Integration with The Movie Database (TMDB) API.
    """
    name = "tmdb"
    description = "Search and retrieve movie metadata from TMDB."
    version = "1.0.0"

    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

    @property
    def actions(self) -> List[str]:
        return ["search_movie", "get_movie_details", "search_person"]

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        api_key = os.getenv("TMDB_API_KEY")
        read_token = os.getenv("TMDB_READ_TOKEN")

        # Prefer Read Token (Bearer) if available, else API Key
        self.headers = {
            "Authorization": f"Bearer {read_token}",
            "Content-Type": "application/json;charset=utf-8"
        } if read_token else {}

        self.params = {"api_key": api_key} if not read_token else {}

        if not api_key and not read_token:
            return self._error("Missing TMDB_API_KEY or TMDB_READ_TOKEN")

        try:
            if action == "search_movie":
                return self._search_movie(kwargs.get("query"), kwargs.get("year"))
            elif action == "get_movie_details":
                return self._get_movie_details(kwargs.get("tmdb_id"))
            elif action == "search_person":
                return self._search_person(kwargs.get("query"))
            elif action == "discover_movies":
                return self._discover_movies(kwargs.get("start_date"), kwargs.get("end_date"), kwargs.get("page", 1))
            else:
                return self._action_not_found(action)
        except Exception as e:
            return self._error(f"TMDB Error: {str(e)}")

    def _search_movie(self, query: str, year: Optional[str] = None) -> Dict[str, Any]:
        if not query: return self._error("Query is required")

        url = f"{self.BASE_URL}/search/movie"
        params = {**self.params, "query": query}
        if year:
            params["year"] = year

        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()

        return self._success(resp.json())

    def _discover_movies(self, start_date: str, end_date: str, page: int = 1) -> Dict[str, Any]:
        """Discover movies released within a date range (YYYY-MM-DD)"""
        if not start_date or not end_date:
            return self._error("start_date and end_date required")

        url = f"{self.BASE_URL}/discover/movie"
        # US region for theatrical releases
        params = {
            **self.params,
            "primary_release_date.gte": start_date,
            "primary_release_date.lte": end_date,
            "region": "US",
            "sort_by": "popularity.desc",
            "vote_count.gte": 0, # Allow 0 votes for upcoming/future movies
            "include_adult": False,
            "page": page
        }

        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return self._success(resp.json())

    def _get_movie_details(self, tmdb_id: int) -> Dict[str, Any]:
        if not tmdb_id: return self._error("tmdb_id is required")

        # Append extra info: credits (cast/crew), release_dates (certification), external_ids (imdb), keywords
        url = f"{self.BASE_URL}/movie/{tmdb_id}"
        params = {**self.params, "append_to_response": "credits,release_dates,external_ids,keywords,videos"}

        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()

        data = resp.json()

        # Process data for easier consumption
        processed = self._process_movie_data(data)

        return self._success(processed)

    def _process_movie_data(self, data: Dict) -> Dict:
        """Helper to extract and format key fields for Notion"""

        # Base URLs for images (using original quality)
        poster_path = data.get("poster_path")
        backdrop_path = data.get("backdrop_path")

        # Credits
        cast = sorted(data.get("credits", {}).get("cast", []), key=lambda x: x['order'])[:10]
        crew = data.get("credits", {}).get("crew", [])

        directors = [c['name'] for c in crew if c['job'] == 'Director']
        producers = [c['name'] for c in crew if c['job'] == 'Producer']
        writers = [c['name'] for c in crew if c['job'] in ['Screenplay', 'Writer']]
        editors = [c['name'] for c in crew if c['job'] == 'Editor']
        dp = [c['name'] for c in crew if c['job'] == 'Director of Photography']
        composers = [c['name'] for c in crew if c['job'] == 'Original Music Composer']

        # Certification (MPAA) - US priority
        certification = ""
        releases = data.get("release_dates", {}).get("results", [])
        for r in releases:
            if r['iso_3166_1'] == 'US':
                for d in r['release_dates']:
                    if d['certification']:
                        certification = d['certification']
                        break

        # Processed entry
        return {
            "tmdb_id": data.get("id"),
            "imdb_id": data.get("external_ids", {}).get("imdb_id"),
            "title": data.get("title"),
            "original_title": data.get("original_title"),
            "tagline": data.get("tagline"),
            "overview": data.get("overview"),
            "status": data.get("status"),
            "release_date": data.get("release_date"),
            "revenue": data.get("revenue"),
            "budget": data.get("budget"),
            "runtime": data.get("runtime"),
            "vote_average": data.get("vote_average"),
            "popularity": data.get("popularity"),
            "poster_url": f"{self.IMAGE_BASE_URL}{poster_path}" if poster_path else None,
            "backdrop_url": f"{self.IMAGE_BASE_URL}{backdrop_path}" if backdrop_path else None,
            "genres": [g['name'] for g in data.get("genres", [])],
            "production_companies": [c['name'] for c in data.get("production_companies", [])],
            "production_countries": [c['name'] for c in data.get("production_countries", [])],
            "spoken_languages": [l['english_name'] for l in data.get("spoken_languages", [])],
            "website": data.get("homepage"),
            # People
            "directors": directors,
            "producers": producers,
            "writers": writers,
            "editors": editors,
            "cinematographers": dp,
            "composers": composers,
            "cast": [c['name'] for c in cast],
            # Meta
            "certification": certification,
            "collection": data.get("belongs_to_collection", {}).get("name") if data.get("belongs_to_collection") else None
        }

    def _search_person(self, query: str) -> Dict[str, Any]:
        if not query: return self._error("Query required")
        url = f"{self.BASE_URL}/search/person"
        resp = requests.get(url, headers=self.headers, params={**self.params, "query": query})
        return self._success(resp.json())

skill = TmdbSkill()
