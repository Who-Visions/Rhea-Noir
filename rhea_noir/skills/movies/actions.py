"""
Rhea Noir Module: actions.py
Auto-generated docstring.
"""

"""
Movies Skill - Find movies and shows.
Ported from fmovies-api.
"""

import requests
from typing import Dict, List, Any
from ..base import Skill

class MoviesSkill(Skill):
    """
    Search and browse movies from Fmovies.
    """

    name = "movies"
    description = "Find movies and TV shows"
    version = "1.0.0"

    BASE_URL = "https://fmoviesz.to"

    @property
    def actions(self) -> List[str]:
        return ["search", "trending"]

    def _lazy_load(self):
        try:
            from bs4 import BeautifulSoup
            self._bs4 = BeautifulSoup
        except ImportError:
            self._bs4 = None

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()
        if not self._bs4:
            return self._error("BeautifulSoup not installed")

        if action == "search":
            return self._search(kwargs.get("query", ""), kwargs.get("page"))
        elif action == "trending":
            return self._trending()
        else:
            return self._action_not_found(action)

    def _search(self, query: str, page: str = None) -> Dict[str, Any]:
        if not query:
            return self._error("Query required")

        url = f"{self.BASE_URL}/search?keyword={query}"
        if page:
            url += f"&page={page}"

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = self._bs4(resp.content, 'lxml')

            items = []
            for item in soup.find_all('div', class_='item'):
                items.append(self._parse_item(item))

            return self._success({"query": query, "results": items})
        except Exception as e:
            return self._error(f"Search failed: {e}")

    def _trending(self) -> Dict[str, Any]:
        try:
            url = f"{self.BASE_URL}/home"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = self._bs4(resp.content, 'lxml')

            # Tab 2 is usually trending/movies in standard templates, but fmovies changes.
            # We'll just grab the first 'tab-content' we find or all items
            items = []
            for item in soup.find_all('div', class_='item'):
                items.append(self._parse_item(item))
                if len(items) >= 20: break # Limit

            return self._success({"results": items})
        except Exception as e:
            return self._error(f"Trending failed: {e}")

    def _parse_item(self, item) -> Dict[str, Any]:
        data = {}
        try:
            a = item.find('a')
            data['link'] = f"{self.BASE_URL}{a.get('href')}" if a else None
            data['title'] = a.get('title') if a else "Unknown"

            img = item.find('img')
            data['cover'] = img['src'] if img else None

            qual = item.find('div', class_="quality")
            data['quality'] = qual.text if qual else None

            imdb = item.find('span', class_='imdb')
            data['imdb'] = imdb.text if imdb else None

            files = item.find('div', class_='meta')
            if files:
                data['meta'] = files.text.strip()
        except:
            pass
        return data

skill = MoviesSkill()
