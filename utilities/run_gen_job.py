import asyncio
import os
import sys

# Add current dir to path to find utilities
sys.path.append(os.getcwd())

from utilities.rhea_asset_gen import ImageGenCortex

async def main():
    print("🚀 Starting Batch Generation...")
    cortex = ImageGenCortex()
    
    prompt = "Cinematic 3D render of a futuristic infinite void tunnel, neon cyan laser beams, dark mist, hyperrealistic, 8k"
    filename = await cortex.generate_asset(prompt)
    
    if filename:
        print(f"SUCCESS: {filename}")
    else:
        print("FAILURE: No file generated")

if __name__ == "__main__":
    asyncio.run(main())
