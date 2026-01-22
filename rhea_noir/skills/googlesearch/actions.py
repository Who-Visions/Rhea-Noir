"""
Gemini Google Search Grounding Skill for Rhea-Noir
Real-time web search for grounded responses
"""
from typing import Optional, Dict, Any, List


class GoogleSearchSkill:
    """Skill for Gemini Google Search grounding."""

    name = "googlesearch"
    version = "1.0.0"
    description = "Gemini Grounding with Google Search"

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client()
        return self._client

    def _success(self, data: Any) -> Dict:
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        return {"success": False, "error": message}

    def _extract_citations(self, grounding_metadata) -> List[Dict]:
        """Extract sources from grounding metadata."""
        sources = []
        if grounding_metadata and grounding_metadata.grounding_chunks:
            for chunk in grounding_metadata.grounding_chunks:
                if chunk.web:
                    sources.append({
                        "title": chunk.web.title,
                        "uri": chunk.web.uri
                    })
        return sources

    def search(
        self,
        query: str,
        model: str = "gemini-3-flash-preview"
    ) -> Dict:
        """
        Query with Google Search grounding.

        Args:
            query: Question or search query
            model: Gemini model to use

        Returns:
            Dict with answer and sources
        """
        try:
            from google.genai import types
            client = self._get_client()

            response = client.models.generate_content(
                model=model,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )

            grounding = response.candidates[0].grounding_metadata if response.candidates else None
            sources = self._extract_citations(grounding)

            return self._success({
                "answer": response.text,
                "sources": sources,
                "search_queries": grounding.web_search_queries if grounding else []
            })
        except Exception as e:
            return self._error(str(e))

    def search_with_urls(
        self,
        query: str,
        urls: List[str],
        model: str = "gemini-3-flash-preview"
    ) -> Dict:
        """
        Query with both Google Search and URL context.

        Args:
            query: Question or task
            urls: Additional URLs to include as context
            model: Gemini model to use

        Returns:
            Dict with answer and sources
        """
        try:
            from google.genai.types import GenerateContentConfig
            client = self._get_client()

            url_list = "\n".join([f"- {url}" for url in urls])
            prompt = f"{query}\n\nReference URLs:\n{url_list}"

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[
                        {"url_context": {}},
                        {"google_search": {}}
                    ]
                )
            )

            grounding = response.candidates[0].grounding_metadata if response.candidates else None

            return self._success({
                "answer": response.text,
                "sources": self._extract_citations(grounding),
                "urls_used": urls
            })
        except Exception as e:
            return self._error(str(e))


skill = GoogleSearchSkill()
