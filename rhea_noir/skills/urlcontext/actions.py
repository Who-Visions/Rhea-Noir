"""
Gemini URL Context Skill for Rhea-Noir
Analyze and compare web pages using Gemini
"""
from typing import Optional, Dict, Any, List


class URLContextSkill:
    """Skill for Gemini URL Context operations."""
    
    name = "urlcontext"
    version = "1.0.0"
    description = "Gemini URL Context - Analyze and compare web pages"
    
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
    
    def analyze_url(
        self,
        url: str,
        question: str,
        model: str = "gemini-3-flash-preview"
    ) -> Dict:
        """
        Analyze content from a single URL.
        
        Args:
            url: URL to analyze
            question: Question about the content
            model: Gemini model to use
            
        Returns:
            Dict with analysis and URL metadata
        """
        try:
            from google.genai.types import GenerateContentConfig
            client = self._get_client()
            
            response = client.models.generate_content(
                model=model,
                contents=f"{question}\n\nURL: {url}",
                config=GenerateContentConfig(
                    tools=[{"url_context": {}}]
                )
            )
            
            # Extract URL metadata
            url_metadata = None
            if response.candidates and response.candidates[0].url_context_metadata:
                url_metadata = response.candidates[0].url_context_metadata
            
            return self._success({
                "answer": response.text,
                "url": url,
                "url_metadata": url_metadata
            })
        except Exception as e:
            return self._error(str(e))
    
    def compare_urls(
        self,
        urls: List[str],
        question: str,
        model: str = "gemini-3-flash-preview"
    ) -> Dict:
        """
        Compare content from multiple URLs.
        
        Args:
            urls: List of URLs to compare (max 20)
            question: Comparison question
            model: Gemini model to use
            
        Returns:
            Dict with comparison and sources
        """
        try:
            from google.genai.types import GenerateContentConfig
            client = self._get_client()
            
            if len(urls) > 20:
                return self._error("Maximum 20 URLs allowed per request")
            
            # Build prompt with URLs
            url_list = "\n".join([f"- {url}" for url in urls])
            prompt = f"{question}\n\nURLs to compare:\n{url_list}"
            
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[{"url_context": {}}]
                )
            )
            
            url_metadata = None
            if response.candidates and response.candidates[0].url_context_metadata:
                url_metadata = response.candidates[0].url_context_metadata
            
            return self._success({
                "answer": response.text,
                "urls": urls,
                "url_metadata": url_metadata
            })
        except Exception as e:
            return self._error(str(e))
    
    def synthesize(
        self,
        urls: List[str],
        question: str,
        use_google_search: bool = False,
        model: str = "gemini-3-flash-preview"
    ) -> Dict:
        """
        Synthesize content from multiple URLs, optionally with search.
        
        Args:
            urls: Source URLs
            question: What to create/synthesize
            use_google_search: Also use Google Search grounding
            model: Gemini model to use
            
        Returns:
            Dict with synthesized content
        """
        try:
            from google.genai.types import GenerateContentConfig
            client = self._get_client()
            
            tools = [{"url_context": {}}]
            if use_google_search:
                tools.append({"google_search": {}})
            
            url_list = "\n".join([f"- {url}" for url in urls])
            prompt = f"{question}\n\nSource URLs:\n{url_list}"
            
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=GenerateContentConfig(tools=tools)
            )
            
            return self._success({
                "content": response.text,
                "sources": urls,
                "used_search": use_google_search
            })
        except Exception as e:
            return self._error(str(e))
    
    def extract_data(
        self,
        url: str,
        data_fields: List[str],
        model: str = "gemini-3-flash-preview"
    ) -> Dict:
        """
        Extract specific data fields from a URL.
        
        Args:
            url: URL to extract from
            data_fields: List of fields to extract (e.g., ["price", "title"])
            model: Gemini model to use
            
        Returns:
            Dict with extracted data
        """
        try:
            from google.genai.types import GenerateContentConfig
            client = self._get_client()
            
            fields_str = ", ".join(data_fields)
            prompt = f"Extract the following data from {url}: {fields_str}. Return as JSON."
            
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[{"url_context": {}}],
                    response_mime_type="application/json"
                )
            )
            
            return self._success({
                "extracted_data": response.text,
                "url": url,
                "fields": data_fields
            })
        except Exception as e:
            return self._error(str(e))


# Singleton instance
skill = URLContextSkill()
