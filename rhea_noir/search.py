"""
Rhea Noir Search - RAG and Vertex AI Search integration
Enables knowledge retrieval from documents and web search
"""

from typing import Optional, List, Dict, Any
from services.memory import LoreMemoryService

# Vertex AI Search availability
VERTEX_SEARCH_AVAILABLE = False
try:
    from google.cloud import discoveryengine_v1 as discoveryengine
    VERTEX_SEARCH_AVAILABLE = True
except ImportError:
    pass


class RheaSearch:
    """
    Unified search interface for Rhea Noir.
    Supports:
    - Vertex AI Search (for knowledge bases)
    - Google Search grounding (via Gemini)
    - Local memory search (SQLite)
    """

    def __init__(
        self,
        project_id: str = "rhea-noir",
        location: str = "global",
        data_store_id: Optional[str] = None,
    ):
        """
        Initialize search.

        Args:
            project_id: GCP project ID
            location: Search location (default: global)
            data_store_id: Vertex AI Search data store ID (optional)
        """
        self.project_id = project_id
        self.location = location
        self.data_store_id = data_store_id
        self.client = None

        if VERTEX_SEARCH_AVAILABLE and data_store_id:
            try:
                self.client = discoveryengine.SearchServiceClient()
            except Exception as e:
                print(f"⚠️ Vertex AI Search init failed: {e}")

        # Initialize Lore Memory (Local SQL)
        self.lore = LoreMemoryService()

    def search_knowledge(
        self,
        query: str,
        page_size: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base using Vertex AI Search.

        Args:
            query: Search query
            page_size: Number of results to return

        Returns:
            List of search results with snippets
        """
        if not self.client or not self.data_store_id:
            return []

        try:
            # Build serving config path
            serving_config = (
                f"projects/{self.project_id}/locations/{self.location}"
                f"/dataStores/{self.data_store_id}/servingConfigs/default_search"
            )

            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=page_size,
            )

            response = self.client.search(request)

            results = []
            for result in response.results:
                doc = result.document
                results.append({
                    "id": doc.id,
                    "title": doc.derived_struct_data.get("title", ""),
                    "snippet": doc.derived_struct_data.get("snippets", [{}])[0].get("snippet", ""),
                    "link": doc.derived_struct_data.get("link", ""),
                    "score": result.relevance_score if hasattr(result, 'relevance_score') else 0,
                })

            return results

        except Exception as e:
            print(f"⚠️ Search error: {e}")
            return []

    def search_with_grounding(
        self,
        query: str,
        model_name: str = "gemini-2.5-flash",
    ) -> Dict[str, Any]:
        """
        Search using Gemini with Google Search grounding.

        Args:
            query: Search query
            model_name: Gemini model to use

        Returns:
            Response with grounded answer and sources
        """
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel, Tool
            from vertexai.generative_models import grounding

            vertexai.init(project=self.project_id, location="us-central1")

            # Create grounding tool
            google_search_tool = Tool.from_google_search_retrieval(
                grounding.GoogleSearchRetrieval()
            )

            model = GenerativeModel(
                model_name,
                tools=[google_search_tool],
            )

            response = model.generate_content(query)

            # Extract grounding metadata
            sources = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    for chunk in candidate.grounding_metadata.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            sources.append({
                                "title": chunk.web.title,
                                "uri": chunk.web.uri,
                            })

            return {
                "answer": response.text,
                "sources": sources,
                "grounded": len(sources) > 0,
            }

        except Exception as e:
            return {
                "answer": f"Search error: {e}",
                "sources": [],
                "grounded": False,
            }

    def search_memory(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search local memory (SQLite).

        Args:
            query: Search query
            limit: Number of results

        Returns:
            List of memory entries
        """
        try:
            from rhea_noir.memory import ShortTermMemory

            memory = ShortTermMemory()
            return memory.recall(query, limit=limit)
        except Exception:
            return []

    async def search_lore(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search Lore Memory (Veillore DB / Notion Mirror).
        """
        try:
            return await self.lore.search_lore(query, limit=limit)
        except Exception as e:
            print(f"⚠️ Lore search error: {e}")
            return []

    @property
    def lore_memory(self) -> LoreMemoryService:
        """Expose LoreMemoryService for direct access/init."""
        return self.lore

    def unified_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict]]:
        """
        Search across multiple sources.

        Args:
            query: Search query
            sources: List of sources to search ("memory", "knowledge", "web")

        Returns:
            Dict with results from each source
        """
        results = {}
        if sources is None:
            sources = ["memory", "knowledge", "web"]

        if "memory" in sources:
            results["memory"] = self.search_memory(query)

        if "knowledge" in sources:
            results["knowledge"] = self.search_knowledge(query)

        if "web" in sources:
            web_result = self.search_with_grounding(query)
            results["web"] = web_result.get("sources", [])
            results["web_answer"] = web_result.get("answer", "")

        return results

    async def unified_search_async(
        self,
        query: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict]]:
        """
        Async unified search prioritizing Local SQL (Lore).
        """
        print(f"🔍 DEBUG: unified_search_async called for '{query}'")
        results = {}
        if sources is None:
            sources = ["lore", "memory", "knowledge", "web"]
        
        print(f"🔍 DEBUG: Sources: {sources}")

        # 1. Local Lore SQL (Priority)
        if "lore" in sources:
            print("🔍 DEBUG: Searching Lore...")
            results["lore"] = await self.search_lore(query)
            print(f"🔍 DEBUG: Lore results found: {len(results['lore'])}")

        # 2. Short Term Memory
        if "memory" in sources:
            results["memory"] = self.search_memory(query)

        # 3. Knowledge Base (Vertex)
        if "knowledge" in sources:
            results["knowledge"] = self.search_knowledge(query)

        # 4. Web Grounding (Fallback/Supplement)
        if "web" in sources:
            # Note: This is blocking, might want to make async if possible
            web_result = self.search_with_grounding(query)
            results["web"] = web_result.get("sources", [])
            results["web_answer"] = web_result.get("answer", "")

        return results

    def unified_search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict]]:
        """Synchronous wrapper for unified search (for backward compat)."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(self.unified_search_async(query, sources))


# Global search instance (initialized without data store)
search = RheaSearch()
