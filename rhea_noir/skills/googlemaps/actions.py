"""
Gemini Google Maps Grounding Skill for Rhea-Noir
Location-aware AI responses using Google Maps data
"""
from typing import Optional, Dict, Any, List


class GoogleMapsSkill:
    """Skill for Gemini Google Maps grounding."""

    name = "googlemaps"
    version = "1.0.0"
    description = "Gemini Google Maps - Location-aware AI responses"

    # Note: Google Maps grounding is NOT available with Gemini 3
    MODEL = "gemini-2.5-flash"
    # pylint: disable=broad-exception-caught

    def __init__(self):
        self._client = None

    def _get_client(self):
        """Get Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client()
            except ImportError:
                raise ImportError("google-genai not installed")
        return self._client

    def _success(self, data: Any) -> Dict:
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        return {"success": False, "error": message}

    def _extract_sources(self, grounding_metadata) -> List[Dict]:
        """Extract sources from grounding metadata."""
        sources = []
        if grounding_metadata and grounding_metadata.grounding_chunks:
            for chunk in grounding_metadata.grounding_chunks:
                if chunk.maps:
                    sources.append({
                        "title": chunk.maps.title,
                        "uri": chunk.maps.uri,
                        "place_id": getattr(chunk.maps, 'place_id', None)
                    })
        return sources

    def search_places(
        self,
        query: str,
        latitude: float,
        longitude: float,
        enable_widget: bool = False
    ) -> Dict:
        """
        Search for places near a location.

        Args:
            query: What to search for (e.g., "coffee shops")
            latitude: User latitude
            longitude: User longitude
            enable_widget: Return widget context token

        Returns:
            Dict with places and sources
        """
        try:
            from google.genai import types
            client = self._get_client()

            response = client.models.generate_content(
                model=self.MODEL,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        google_maps=types.GoogleMaps(enable_widget=enable_widget)
                    )],
                    tool_config=types.ToolConfig(
                        retrieval_config=types.RetrievalConfig(
                            lat_lng=types.LatLng(
                                latitude=latitude,
                                longitude=longitude
                            )
                        )
                    )
                )
            )

            grounding = response.candidates[0].grounding_metadata if response.candidates else None
            sources = self._extract_sources(grounding)

            result = {
                "answer": response.text,
                "sources": sources,
                "location": {"lat": latitude, "lng": longitude}
            }

            if enable_widget and grounding:
                widget_token = getattr(grounding, 'google_maps_widget_context_token', None)
                if widget_token:
                    result["widget_token"] = widget_token

            return self._success(result)
        except Exception as e:
            return self._error(str(e))

    def get_recommendations(
        self,
        query: str,
        latitude: float,
        longitude: float
    ) -> Dict:
        """
        Get personalized recommendations based on location.

        Args:
            query: What to recommend (e.g., "best brunch spots")
            latitude: User latitude
            longitude: User longitude

        Returns:
            Dict with recommendations and sources
        """
        return self.search_places(query, latitude, longitude)

    def plan_itinerary(
        self,
        query: str,
        latitude: float,
        longitude: float,
        enable_widget: bool = True
    ) -> Dict:
        """
        Plan an itinerary for a location.

        Args:
            query: What to plan (e.g., "day trip to museums and dinner")
            latitude: Starting location latitude
            longitude: Starting location longitude
            enable_widget: Return widget context token

        Returns:
            Dict with itinerary and sources
        """
        try:
            client = self._get_client()

            prompt = f"Plan the following: {query}. Include specific places with addresses and opening hours."

            response = client.models.generate_content(
                model=self.MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        google_maps=types.GoogleMaps(enable_widget=enable_widget)
                    )],
                    tool_config=types.ToolConfig(
                        retrieval_config=types.RetrievalConfig(
                            lat_lng=types.LatLng(
                                latitude=latitude,
                                longitude=longitude
                            )
                        )
                    )
                )
            )

            grounding = response.candidates[0].grounding_metadata if response.candidates else None
            sources = self._extract_sources(grounding)

            result = {
                "itinerary": response.text,
                "places": sources,
                "location": {"lat": latitude, "lng": longitude}
            }

            if enable_widget and grounding:
                widget_token = getattr(grounding, 'google_maps_widget_context_token', None)
                if widget_token:
                    result["widget_token"] = widget_token

            return self._success(result)
        except Exception as e:
            return self._error(str(e))

    def ask_about_place(
        self,
        question: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict:
        """
        Ask a question about a specific place.

        Args:
            question: Question about a place
            latitude: Optional location context
            longitude: Optional location context

        Returns:
            Dict with answer and sources
        """
        try:
            client = self._get_client()

            config_opts = {
                'tools': [types.Tool(google_maps=types.GoogleMaps())]
            }

            if latitude and longitude:
                config_opts['tool_config'] = types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(
                            latitude=latitude,
                            longitude=longitude
                        )
                    )
                )

            response = client.models.generate_content(
                model=self.MODEL,
                contents=question,
                config=types.GenerateContentConfig(**config_opts)
            )

            grounding = response.candidates[0].grounding_metadata if response.candidates else None
            sources = self._extract_sources(grounding)

            return self._success({
                "answer": response.text,
                "sources": sources
            })
        except Exception as e:
            return self._error(str(e))


# Singleton instance
skill = GoogleMapsSkill()
