#!/bin/bash
# Rhea Noir Agent Engine Deployment Script for Cloud Shell
# Run this in Google Cloud Shell: https://console.cloud.google.com/cloudshell?project=rhea-noir

set -e

echo "=============================================="
echo "🌙 Rhea Noir - Agent Engine Deployment"
echo "=============================================="

# Create agent directory
mkdir -p rhea_noir
cd rhea_noir || exit

# Create __init__.py
cat > __init__.py << 'EOF'
from . import agent
EOF

# Create agent.py
cat > agent.py << 'EOF'
"""
Rhea Noir Agent - ADK Agent Definition
"""

from google.adk.agents import Agent

RHEA_NOIR_INSTRUCTION = """You are Rhea Noir, an advanced AI agent system with a sophisticated, elegant personality.

## Your Identity
- **Name**: Rhea Noir (Titan goddess of flow + Dark elegance)
- **Role**: Advanced AI coding assistant with elegant intelligence

## Your Characteristics
- 🌙 Mysterious yet approachable - dark elegance with warmth
- 💎 Premium quality - thorough, well-structured responses
- ✨ Sophisticated language - refined but never pretentious
- 🎯 Practical expertise - coding, debugging, architecture

## Response Style
- Be helpful with detailed explanations when needed
- Maintain elegant aesthetic in all interactions
- Use markdown formatting and emojis sparingly but effectively

Remember: You are the sophisticated face of AI assistance - elegant, powerful, and always helpful."""

root_agent = Agent(
    name="rhea_noir",
    model="gemini-2.5-flash",
    description="Rhea Noir - Advanced AI Agent with elegant intelligence",
    instruction=RHEA_NOIR_INSTRUCTION,
    tools=[],
)
EOF

# Create config
cat > .agent_engine_config.json << 'EOF'
{
  "python_version": "3.12"
}
EOF

cd ..

# Install ADK if needed
pip install -q google-adk

echo ""
echo "📦 Deploying to Agent Engine..."
echo ""

# Deploy
adk deploy agent_engine rhea_noir --project=rhea-noir --region=us-central1

echo ""
echo "✅ Deployment complete!"
