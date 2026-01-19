import asyncio
import os
from google import genai
from google.genai import types
from datetime import datetime

# Configure Client (Uses 'gcloud auth' / Application Default Credentials)
# Ensure you have run: gcloud auth application-default login
client = genai.Client(vertexai=True, project="rhea-noir", location="us-central1")

class ImageGenCortex:
    """
    Rhea's Visual Cortex (Nano Banana).
    Powered by Gemini 3 Pro (Generation) and Gemini 2.5 Flash (Editing).
    """
    
    async def generate_asset(self, prompt: str, aspect_ratio: str = "16:9", thinking_mode: bool = True):
        """
        Generates high-fidelity assets using 'Nano Banana Pro' (Gemini 3 Pro Image).
        Enable 'thinking_mode' for enhanced prompt adherence.
        """
        print(f"🎨 Rhea Generating Asset: '{prompt}' (Mode: Nano Banana Pro)...")
        
        try:
            response = await client.aio.models.generate_images(
                model="imagen-3.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    # include_thoughts=thinking_mode,  # Removed: Not supported in SDK 1.59 config
                    aspect_ratio=aspect_ratio,
                    output_mime_type="image/jpeg"
                )
            )
            
            # Handle Thoughts (if returned) - Disabled for Imagen 3
            # if thinking_mode and response.predictions and response.predictions[0].thoughts:
            #     print(f"🧠 Rhea's Thoughts: {response.predictions[0].thoughts}")

            # Save Image
            generated_image = response.generated_images[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rhea_asset_{timestamp}.jpg"
            
            with open(filename, "wb") as f:
                f.write(generated_image.image.image_bytes)
                
            print(f"✅ Asset Saved: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Generation Failed: {e}")
            return None

    async def edit_asset(self, base_image_path: str, prompt: str):
        """
        Edits an existing asset using 'Nano Banana Flash' (Gemini 2.5).
        """
        print(f"🎨 Rhea Editing Asset: {base_image_path} with prompt '{prompt}'...")
        
        try:
            base_img = types.Image.load_from_file(base_image_path)
            
            response = await client.aio.models.edit_image(
                model="gemini-2.5-flash-image",
                prompt=prompt,
                base_image=base_img,
                config=types.EditImageConfig(
                    number_of_images=1
                )
            )
            
            generated_image = response.generated_images[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rhea_edit_{timestamp}.jpg"
            
            with open(filename, "wb") as f:
                f.write(generated_image.image.image_bytes)
                
            print(f"✅ Edit Saved: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Edit Failed: {e}")
            return None

# CLI Entry Point
async def main():
    cortex = ImageGenCortex()
    
    print("\n--- Rhea Asset Generator (Nano Banana Pro) ---")
    print("1. Generate New Asset")
    print("2. Edit Existing Asset")
    choice = input("Select Mode (1/2): ")
    
    if choice == "1":
        prompt = input("Enter Asset Description: ")
        await cortex.generate_asset(prompt)
    elif choice == "2":
        path = input("Enter Base Image Path: ")
        prompt = input("Enter Edit Instruction: ")
        await cortex.edit_asset(path, prompt)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    asyncio.run(main())
