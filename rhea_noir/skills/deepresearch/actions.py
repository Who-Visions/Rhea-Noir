"""
Gemini Deep Research Agent Skill for Rhea-Noir
Autonomous multi-step research with web + file search
"""
import time
from typing import Optional, Dict, Any, List


class DeepResearchSkill:
    """Skill for Gemini Deep Research Agent."""

    name = "deepresearch"
    version = "1.0.0"
    description = "Gemini Deep Research - Autonomous research agent"

    AGENT = "deep-research-pro-preview-12-2025"

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

    def research(
        self,
        query: str,
        format_instructions: Optional[str] = None,
        poll_interval: int = 10,
        timeout: int = 1800  # 30 minutes max
    ) -> Dict:
        """
        Run a deep research task.

        Args:
            query: Research question or task
            format_instructions: Optional formatting (e.g., "Include tables")
            poll_interval: Seconds between status checks
            timeout: Maximum wait time in seconds

        Returns:
            Dict with report and sources
        """
        try:
            client = self._get_client()

            prompt = query
            if format_instructions:
                prompt = f"{query}\n\nFormat: {format_instructions}"

            # Start background research
            interaction = client.interactions.create(
                input=prompt,
                agent=self.AGENT,
                background=True
            )

            interaction_id = interaction.id
            start_time = time.time()

            # Poll for completion
            while True:
                if time.time() - start_time > timeout:
                    return self._error(f"Research timed out after {timeout}s")

                interaction = client.interactions.get(interaction_id)

                if interaction.status == "completed":
                    report = interaction.outputs[-1].text if interaction.outputs else ""
                    return self._success({
                        "report": report,
                        "interaction_id": interaction_id,
                        "status": "completed"
                    })
                elif interaction.status == "failed":
                    return self._error(f"Research failed: {interaction.error}")

                time.sleep(poll_interval)

        except Exception as e:
            return self._error(str(e))

    def research_with_files(
        self,
        query: str,
        file_store: str,
        format_instructions: Optional[str] = None,
        poll_interval: int = 10,
        timeout: int = 1800
    ) -> Dict:
        """
        Run research with access to your file search store.

        Args:
            query: Research question
            file_store: File search store name
            format_instructions: Optional formatting
            poll_interval: Seconds between status checks
            timeout: Maximum wait time

        Returns:
            Dict with report
        """
        try:
            client = self._get_client()

            prompt = query
            if format_instructions:
                prompt = f"{query}\n\nFormat: {format_instructions}"

            interaction = client.interactions.create(
                input=prompt,
                agent=self.AGENT,
                background=True,
                tools=[{
                    "type": "file_search",
                    "file_search_store_names": [file_store]
                }]
            )

            interaction_id = interaction.id
            start_time = time.time()

            while True:
                if time.time() - start_time > timeout:
                    return self._error(f"Research timed out")

                interaction = client.interactions.get(interaction_id)

                if interaction.status == "completed":
                    return self._success({
                        "report": interaction.outputs[-1].text if interaction.outputs else "",
                        "interaction_id": interaction_id,
                        "file_store": file_store
                    })
                elif interaction.status == "failed":
                    return self._error(f"Research failed: {interaction.error}")

                time.sleep(poll_interval)

        except Exception as e:
            return self._error(str(e))

    def followup(
        self,
        question: str,
        previous_interaction_id: str
    ) -> Dict:
        """
        Ask a follow-up question about a completed research.

        Args:
            question: Follow-up question
            previous_interaction_id: ID from previous research

        Returns:
            Dict with answer
        """
        try:
            client = self._get_client()

            interaction = client.interactions.create(
                input=question,
                agent=self.AGENT,
                previous_interaction_id=previous_interaction_id
            )

            return self._success({
                "answer": interaction.outputs[-1].text if interaction.outputs else "",
                "interaction_id": interaction.id
            })
        except Exception as e:
            return self._error(str(e))


skill = DeepResearchSkill()
