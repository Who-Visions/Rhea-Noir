"""
A2A Skill - Agent-to-Agent communication.
"""

from typing import Dict, List, Any
from ..base import Skill


class A2ASkill(Skill):
    """
    Fleet discovery and inter-agent communication.
    """

    name = "a2a"
    description = "Agent-to-Agent fleet discovery and communication"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._fleet = None

    @property
    def actions(self) -> List[str]:
        return ["discover", "list", "chat"]

    def _lazy_load(self):
        if self._fleet is None:
            try:
                from rhea_noir.a2a import fleet, discover_agent
                self._fleet = fleet
                self._discover_fn = discover_agent
            except ImportError:
                pass

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()

        if not self._fleet:
            return self._error("A2A system not available")

        if action == "discover":
            url = kwargs.get("url", "")
            if not url:
                return self._error("URL is required")
            card = self._discover_fn(url)
            if card:
                return self._success(card.to_dict())
            return self._error("Discovery failed")

        elif action == "list":
            agents = self._fleet.list_agents()
            return self._success({
                "agents": [card.to_dict() for card in agents.values()]
            })

        elif action == "chat":
            agent = kwargs.get("agent", "")
            message = kwargs.get("message", "")
            if not agent or not message:
                return self._error("Agent and message required")

            card = self._fleet.get(agent)
            if not card:
                return self._error(f"Agent '{agent}' not found")

            # Use requests to send message
            import requests
            try:
                response = requests.post(
                    card.chat_endpoint,
                    json={"model": agent, "messages": [{"role": "user", "content": message}]},
                    timeout=60
                )
                data = response.json()
                return self._success({
                    "agent": card.name,
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content", "")
                })
            except Exception as e:
                return self._error(str(e))

        else:
            return self._action_not_found(action)


skill = A2ASkill()
