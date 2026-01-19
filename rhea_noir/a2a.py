"""
Rhea Noir A2A (Agent-to-Agent) Discovery Module
Who Visions Fleet Standard - Dynamic agent discovery via /.well-known/agent.json
"""

import requests
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading


@dataclass
class AgentCard:
    """Agent identity card from /.well-known/agent.json"""
    name: str
    version: str
    description: str
    capabilities: List[str]
    endpoints: Dict[str, str]
    extensions: Dict[str, str] = field(default_factory=dict)
    base_url: str = ""
    discovered_at: datetime = field(default_factory=datetime.now)
    
    @property
    def chat_endpoint(self) -> str:
        """Get full chat endpoint URL"""
        chat_path = self.endpoints.get("chat", "/v1/chat/completions")
        return f"{self.base_url.rstrip('/')}{chat_path}"
    
    @property
    def color(self) -> str:
        return self.extensions.get("color", "cyan")
    
    @property
    def emoji(self) -> str:
        return self.extensions.get("emoji", "🤖")
    
    @property
    def role(self) -> str:
        return self.extensions.get("role", "Agent")


# Default agent registry (fallback when discovery fails)
DEFAULT_AGENTS = {
    "dav1d": {
        "base_url": "https://dav1d-322812104986.us-central1.run.app",
        "fallback": {
            "name": "Dav1d",
            "emoji": "🤖",
            "color": "cyan",
            "chat_endpoint": "/v1/chat/completions"
        }
    },
    "yuki": {
        "base_url": "https://yuki-ai-914641083224.us-central1.run.app",
        "fallback": {
            "name": "Yuki",
            "emoji": "❄️",
            "color": "bright_blue",
            "chat_endpoint": "/v1/chat/completions"
        }
    },
}


class FleetRegistry:
    """
    Dynamic agent registry with A2A discovery.
    Discovers agents via /.well-known/agent.json on first contact.
    """
    
    CACHE_TTL = timedelta(hours=1)  # Re-discover after 1 hour
    DISCOVERY_TIMEOUT = 5  # seconds
    
    def __init__(self):
        self._agents: Dict[str, AgentCard] = {}
        self._lock = threading.Lock()
    
    def discover(self, agent_key: str, base_url: Optional[str] = None) -> Optional[AgentCard]:
        """
        Discover an agent's capabilities via A2A protocol.
        
        Args:
            agent_key: Short name like "dav1d" or "yuki"
            base_url: Optional base URL, uses DEFAULT_AGENTS if not provided
        
        Returns:
            AgentCard if discovery succeeds, None otherwise
        """
        # Check cache first
        with self._lock:
            if agent_key in self._agents:
                card = self._agents[agent_key]
                if datetime.now() - card.discovered_at < self.CACHE_TTL:
                    return card
        
        # Get base URL from defaults if not provided
        if not base_url:
            if agent_key not in DEFAULT_AGENTS:
                return None
            base_url = DEFAULT_AGENTS[agent_key]["base_url"]
        
        # Try to fetch agent card
        try:
            url = f"{base_url.rstrip('/')}/.well-known/agent.json"
            response = requests.get(url, timeout=self.DISCOVERY_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            card = AgentCard(
                name=data.get("name", agent_key.title()),
                version=data.get("version", "unknown"),
                description=data.get("description", ""),
                capabilities=data.get("capabilities", []),
                endpoints=data.get("endpoints", {"chat": "/v1/chat/completions"}),
                extensions=data.get("extensions", {}),
                base_url=base_url,
            )
            
            with self._lock:
                self._agents[agent_key] = card
            
            return card
            
        except Exception:
            # Fall back to default config
            return self._create_fallback(agent_key, base_url)
    
    def _create_fallback(self, agent_key: str, base_url: str) -> Optional[AgentCard]:
        """Create a fallback AgentCard from DEFAULT_AGENTS"""
        if agent_key not in DEFAULT_AGENTS:
            return None
        
        fallback = DEFAULT_AGENTS[agent_key]["fallback"]
        card = AgentCard(
            name=fallback.get("name", agent_key.title()),
            version="fallback",
            description="Agent discovery unavailable - using fallback config",
            capabilities=["text-generation"],
            endpoints={"chat": fallback.get("chat_endpoint", "/v1/chat/completions")},
            extensions={
                "color": fallback.get("color", "cyan"),
                "emoji": fallback.get("emoji", "🤖"),
            },
            base_url=base_url,
        )
        
        with self._lock:
            self._agents[agent_key] = card
        
        return card
    
    def get(self, agent_key: str) -> Optional[AgentCard]:
        """Get an agent, discovering if necessary"""
        return self.discover(agent_key)
    
    def list_agents(self) -> Dict[str, AgentCard]:
        """List all known agents (discovered + defaults)"""
        # Discover all default agents
        for key in DEFAULT_AGENTS:
            if key not in self._agents:
                self.discover(key)
        
        return dict(self._agents)
    
    def add_agent(self, agent_key: str, base_url: str) -> Optional[AgentCard]:
        """Add a new agent to the registry and discover its capabilities"""
        return self.discover(agent_key, base_url)
    
    def clear_cache(self):
        """Clear the agent cache to force re-discovery"""
        with self._lock:
            self._agents.clear()


# Global fleet registry instance
fleet = FleetRegistry()


def discover_agent(base_url: str) -> Optional[AgentCard]:
    """
    Discover an agent at the given base URL.
    
    Example:
        card = discover_agent("https://dav1d-322812104986.us-central1.run.app")
        print(card.name, card.capabilities)
    """
    try:
        url = f"{base_url.rstrip('/')}/.well-known/agent.json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return AgentCard(
            name=data.get("name", "Unknown"),
            version=data.get("version", "unknown"),
            description=data.get("description", ""),
            capabilities=data.get("capabilities", []),
            endpoints=data.get("endpoints", {}),
            extensions=data.get("extensions", {}),
            base_url=base_url,
        )
    except Exception:
        return None
