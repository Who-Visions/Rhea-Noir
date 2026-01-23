"""
Rhea Noir Agent - ADK Agent Definition
Deployed to Vertex AI Reasoning Engine for persistent memory and tool calling
"""

from google.adk.agents import Agent

# System instruction for Rhea Noir personality (Dynamic from Persona System)
from rhea_noir.persona import get_system_prompt
from rhea_noir.gemini3_router import MODELS

# Default to "Chill Bestie" mode for the root agent unless overridden
RHEA_NOIR_INSTRUCTION = get_system_prompt("chill_bestie") # Base instruction

# Define the Rhea Noir root agent
root_agent = Agent(
    name="rhea_noir",
    model=MODELS["flash"],  # Use centralized model constant
    description=(
        "Rhea Noir - A cybernetic creative partner and intelligent agent system. "
        "Expert in coding, streaming strategy, and cultural intelligence."
    ),
    instruction=RHEA_NOIR_INSTRUCTION,
    tools=[],  # Tools will be added as capabilities expand
)
