"""
Gemini 3 Smart Router for Rhea Noir.

Routes queries to optimal model/thinking level:
- Flash (low/minimal thinking) → Fast responses
- Pro (high thinking) → Complex reasoning
- Parallel: Flash responds while Pro thinks deep

Voice stays on Gemini 2.5 Flash TTS (unchanged).
"""

from typing import Dict, Any, Optional, Tuple, Iterator, Union
from enum import Enum
from dataclasses import dataclass
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class ThinkingLevel(Enum):
    """Gemini 3 thinking levels (lowercase per docs)."""
    MINIMAL = "minimal"  # Flash only - almost no thinking
    LOW = "low"          # Flash/Pro - minimal latency
    MEDIUM = "medium"    # Flash only - balanced
    HIGH = "high"        # Flash/Pro - max reasoning (default)





class QueryComplexity(Enum):
    """Query complexity classification."""
    SIMPLE = "simple"      # Greetings, basic facts, short answers
    MODERATE = "moderate"  # Explanations, comparisons, advice
    COMPLEX = "complex"    # Math, code, multi-step reasoning, analysis


@dataclass
class RoutingDecision:
    """Routing decision from classifier."""
    model: str
    thinking_level: ThinkingLevel
    complexity: QueryComplexity
    parallel_deep_think: bool = False  # Run Pro in background?


# Model configuration - Gemini 3 requires GEMINI_API_KEY
# Falls back to Gemini 2.5 on VertexAI if not available
MODELS = {
    "flash": "gemini-3-flash-preview",
    "pro": "gemini-3-pro-preview",
    "tts": "gemini-2.5-flash-preview-tts",  # Voice - unchanged!
}

# Fallback models for VertexAI (when GEMINI_API_KEY not set)
MODELS_FALLBACK = {
    "flash": "gemini-2.5-flash",
    "pro": "gemini-2.5-pro",
    "tts": "gemini-2.5-flash-preview-tts",
    "search": "gemini-3-flash-preview", # For search tasks
}


# Keywords that suggest complex queries
# ... (same) ...


# Keywords that suggest complex queries
COMPLEX_INDICATORS = [
    "explain", "analyze", "compare", "calculate", "solve",
    "how does", "why does", "what if", "debug", "optimize",
    "implement", "design", "plan", "strategy", "evaluate",
    "code", "script", "algorithm", "function", "error",
    "math", "equation", "proof", "derive", "formula",
]

# Keywords that suggest simple queries
SIMPLE_INDICATORS = [
    "hi", "hello", "hey", "thanks", "bye", "yes", "no",
    "what is", "who is", "when", "where", "how are you",
    "tell me about", "quick", "short", "brief",
]


class Gemini3Router:
    """
    Smart router for Gemini 3 models.

    Routes queries to optimal model based on complexity:
    - Simple → Flash (minimal/low thinking) for speed
    - Complex → Pro (high thinking) OR parallel (Flash fast + Pro deep)
    """

    _instance: Optional["Gemini3Router"] = None

    @classmethod
    def get_instance(cls) -> "Gemini3Router":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._client_global = None   # For Gemini 3 (Thinking)
        self._client_regional = None # For Gemini 2.5 (Search/Grounding)
        self._types = None
        self._grounding_tool = None
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._use_gemini3 = True

    @property
    def models(self) -> Dict[str, str]:
        """Get current model configuration."""
        if self._use_gemini3:
            # Extend with search model
            m = MODELS.copy()
            m["search"] = "gemini-3-flash-preview"
            return m
        return MODELS_FALLBACK.copy()

    def _lazy_load(self):
        """Lazy load Gemini clients and tools."""
        if self._client_global is not None:
            return


        if genai is None:
            raise ImportError("google-genai package not found.")


        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "rhea-noir")
        location = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

        # 1. Global Client (Gemini 3 Thinking)
        self._client_global = genai.Client(
            vertexai=True,
            project=project_id,
            location="global"
        )

        # 2. Regional Client (Gemini 2.5 Search/Grounding)
        self._client_regional = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )

        self._types = types

        # Configure Search Tool (attached to Regional client usually?)
        # Tool definition is independent of client instance.
        self._grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        print(f"🧠 Gemini 3 Router Initialized (Global + {location})")


    def _get_client_for_model(self, model_name: str):
        """Select correct client based on model."""
        # Gemini 3 models must go to Global endpoint
        if "gemini-3" in model_name or "thinking" in model_name:
            return self._client_global
        return self._client_regional



    def classify_query(self, query: str) -> QueryComplexity:
        """Classify query complexity based on content."""
        query_lower = query.lower().strip()

        # Check for search indicators
        if "search" in query_lower or any(ind in query_lower for ind in ["who won", "weather", "news", "latest", "time", "score", "price", "stock"]):
            # Return a complexity that maps to Search model?
            # For now, let's just piggyback on logic in route()
            pass

        # Check for simple indicators
        for indicator in SIMPLE_INDICATORS:
            if query_lower.startswith(indicator) or len(query_lower.split()) < 5:
                return QueryComplexity.SIMPLE

        # Check for complex indicators
        complex_score = sum(1 for ind in COMPLEX_INDICATORS if ind in query_lower)

        if complex_score >= 2 or len(query_lower.split()) > 50:
            return QueryComplexity.COMPLEX
        elif complex_score >= 1 or len(query_lower.split()) > 20:
            return QueryComplexity.MODERATE

        return QueryComplexity.SIMPLE

    def route(self, query: str, force_deep: bool = False) -> RoutingDecision:
        """
        Route query to optimal model/thinking level.

        Args:
            query: User query text
            force_deep: Force Pro with high thinking
        """
        self._lazy_load()  # Ensure models property is available
        complexity = self.classify_query(query)
        models = self.models

        # For Gemini 2.5 fallback, use thinking_budget instead of thinking_level
        # use_budget = not self._use_gemini3

        if force_deep:
            return RoutingDecision(
                model=models["pro"],
                thinking_level=ThinkingLevel.HIGH,
                complexity=complexity,
                parallel_deep_think=False,
            )

        # Check for search intent
        query_lower = query.lower()
        search_triggers = ["who won", "weather", "news", "latest", "time in", "score", "price", "stock", "search"]
        needs_search = any(t in query_lower for t in search_triggers)

        if needs_search and self._use_gemini3:
             # Route to Search Model (Gemini 2.5) on Regional Endpoint
            return RoutingDecision(
                model=models["search"],
                thinking_level=ThinkingLevel.MINIMAL, # 2.5 doesn't use thinking config usually
                complexity=complexity,
                parallel_deep_think=False,
            )

        if complexity == QueryComplexity.SIMPLE:
            return RoutingDecision(
                model=models["flash"],
                thinking_level=ThinkingLevel.MINIMAL if self._use_gemini3 else ThinkingLevel.LOW,
                complexity=complexity,
                parallel_deep_think=False,
            )

        elif complexity == QueryComplexity.MODERATE:
            return RoutingDecision(
                model=models["flash"],
                thinking_level=ThinkingLevel.LOW,
                complexity=complexity,
                parallel_deep_think=False,
            )

        else:  # COMPLEX
            # Use Flash for quick response, Pro for deep thinking in parallel
            return RoutingDecision(
                model=models["flash"],
                thinking_level=ThinkingLevel.LOW,
                complexity=complexity,

                parallel_deep_think=True,  # Run Pro in background
            )

    def generate(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        routing: Optional[RoutingDecision] = None,
    ) -> Dict[str, Any]:
        """
        Generate response using routed model.

        Returns:
            {
                "text": str,
                "model": str,
                "thinking_level": str,
                "complexity": str,
            }
        """
        self._lazy_load()

        if routing is None:
            routing = self.route(query)

        # Gemini 3: use thinking_level
        config = self._types.GenerateContentConfig(
            thinking_config=self._types.ThinkingConfig(
                thinking_level=routing.thinking_level.value
            ),
            tools=[self._grounding_tool] # Add tools to config
        )

        # Build contents
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I'm ready."}]})
        contents.append({"role": "user", "parts": [{"text": query}]})

        client = self._get_client_for_model(routing.model)

        response = client.models.generate_content(
            model=routing.model,
            contents=contents,
            config=config,
        )

        return {
            "text": response.text,
            "model": routing.model,
            "thinking_level": routing.thinking_level.value,
            "complexity": routing.complexity.value,
        }
    def generate_stream(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        routing: Optional[RoutingDecision] = None,
    ) -> Iterator[Union[str, Dict[str, Any]]]:
        """
        Generate streaming response using routed model.
        Yields text chunks (str) and optionally grounding metadata (dict).
        """
        self._lazy_load()

        if routing is None:
            routing = self.route(query)

        # Gemini 3: use thinking_level
        config = self._types.GenerateContentConfig(
            thinking_config=self._types.ThinkingConfig(
                thinking_level=routing.thinking_level.value
            ),
            tools=[self._grounding_tool] # Add tools to config
        )

        # Build contents
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I'm ready."}]})
        contents.append({"role": "user", "parts": [{"text": query}]})

        client = self._get_client_for_model(routing.model)

        responses = client.models.generate_content_stream(
            model=routing.model,
            contents=contents,
            config=config,
        )

        for response in responses:
            # Yield Metadata if present
            # Note: with genai library, candidates might be empty in some chunks?
            # We check response.candidates
            if response.candidates:
                cand = response.candidates[0]
                if hasattr(cand, 'grounding_metadata') and cand.grounding_metadata:
                    # Grounding Metadata object needs to be converted to dict or passed as is?
                    # Let's pass a wrapper dict
                    yield {"type": "citation", "data": cand.grounding_metadata}

            if response.text:
                yield response.text


    async def generate_parallel(
        self,
        query: str,
        system_prompt: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Generate with parallel deep thinking.

        Returns:
            (fast_response, deep_response or None)

        Fast response comes from Flash (low thinking).
        Deep response comes from Pro (high thinking) - may take longer.
        """
        self._lazy_load()
        routing = self.route(query)

        # Get fast response
        fast_result = self.generate(query, system_prompt, routing)

        if not routing.parallel_deep_think:
            return fast_result, None

        # Run deep thinking in background
        deep_routing = RoutingDecision(
            model=self.models["pro"],
            thinking_level=ThinkingLevel.HIGH,
            complexity=routing.complexity,
        )

        loop = asyncio.get_event_loop()
        deep_future = loop.run_in_executor(
            self._executor,
            lambda: self.generate(query, system_prompt, deep_routing)
        )

        # Return fast response immediately, deep response as future
        return fast_result, deep_future



def get_router() -> Gemini3Router:
    """Get the router instance (legacy accessor)."""
    return Gemini3Router.get_instance()
