"""
Deploy Rhea Noir to Agent Engine via Python SDK (Python 3.12)
"""

import vertexai
from vertexai.agent_engines import AgentEngine
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Vertex AI
PROJECT_ID = "rhea-noir"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://rhea-noir-vertex-staging"

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

# Import the agent
from rhea_noir.agent import root_agent

print("=" * 60)
print("🌙 Rhea Noir Agent Engine Deployment")
print("=" * 60)
print(f"Project: {PROJECT_ID}")
print(f"Location: {LOCATION}")
print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")
print()

try:
    print("📦 Starting deployment to Agent Engine...")
    print("   (This may take 5-10 minutes)")
    print()
    
    # Deploy to Agent Engine
    remote_agent = AgentEngine.create(
        agent_engine=root_agent,
        display_name="Rhea Noir",
        description="Rhea Noir - Advanced AI Agent with elegant intelligence",
        requirements=[
            "google-adk>=1.0.0",
            "google-cloud-aiplatform>=1.71.0",
        ],
    )
    
    print()
    print("=" * 60)
    print("✅ DEPLOYMENT SUCCESSFUL!")
    print("=" * 60)
    print(f"Agent Engine ID: {remote_agent.resource_name}")
    print()
    print("To query the agent:")
    print('  from vertexai.agent_engines import AgentEngine')
    print(f'  agent = AgentEngine("{remote_agent.resource_name}")')
    print('  response = agent.query(input="Hello Rhea Noir!")')
    print()
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ DEPLOYMENT FAILED")
    print("=" * 60)
    print(f"Error: {e}")
    raise
