"""
Stitch Skill - AI-powered UI and Image generation using Google's Gemini 3 API.
Generates UI layouts, components, production-ready code, and images from natural language.
"""


import base64
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class StitchSkill:
    """
    Generate AI-powered UIs and images with text prompts using Google Gemini 3.

    Supported models:
    - gemini-3-pro-preview: Text/code generation with advanced reasoning
    - gemini-3-pro-image-preview: Image generation (Nano Banana Pro)
    - gemini-2.5-flash-image: Fast image generation (Nano Banana)
    """

    name = "stitch"
    description = "AI-powered UI and image generation from natural language"
    version = "2.0.0"

    # UI Generation system prompt
    SYSTEM_PROMPT = """You are an expert UI/UX designer and front-end developer.
When given a description of a UI, you generate clean, production-ready code.
Always output complete, valid code that can be used immediately.
Use modern best practices, semantic HTML, and clean CSS.
For React components, use functional components with hooks.
Make UIs visually appealing with good spacing, colors, and typography."""

    @property
    def actions(self) -> List[str]:
        return [
            "generate_ui", "generate_component", "generate_react", "generate_html",
            "generate_image", "edit_image", "generate_logo", "generate_infographic"
        ]

    def _success(self, result):
        return {"success": True, "result": result}

    def _error(self, msg):
        return {"success": False, "error": msg}

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "generate_ui":
                return self._generate_ui(kwargs.get("prompt"), kwargs.get("format", "html"))
            elif action == "generate_component":
                return self._generate_component(kwargs.get("prompt"), kwargs.get("framework", "react"))
            elif action == "generate_react":
                return self._generate_ui(kwargs.get("prompt"), format="react")
            elif action == "generate_html":
                return self._generate_ui(kwargs.get("prompt"), format="html")
            elif action == "generate_image":
                return self._generate_image(
                    kwargs.get("prompt"),
                    kwargs.get("aspect_ratio", "16:9"),
                    kwargs.get("resolution", "1K"),
                    kwargs.get("output_path")
                )
            elif action == "edit_image":
                return self._edit_image(
                    kwargs.get("prompt"),
                    kwargs.get("image_path"),
                    kwargs.get("output_path")
                )
            elif action == "generate_logo":
                return self._generate_logo(kwargs.get("prompt"), kwargs.get("output_path"))
            elif action == "generate_infographic":
                return self._generate_infographic(kwargs.get("prompt"), kwargs.get("output_path"))
            else:
                return self._error(f"Unknown action: {action}")
        except Exception as e:
            return self._error(f"Stitch error: {str(e)}")

    def _get_client(self):
        """Get Gemini 3 client"""
        try:
            from google import genai
            # Client automatically uses GEMINI_API_KEY from environment
            return genai.Client()
        except ImportError:
            raise ImportError("google-genai package required: pip install google-genai")

    def _generate_ui(self, prompt: str, format: str = "html") -> Dict[str, Any]:
        """Generate a complete UI from a text prompt using Gemini 3"""
        if not prompt:
            return self._error("Prompt is required")

        client = self._get_client()
        from google.genai import types

        format_instructions = {
            "html": "Generate a complete HTML page with inline CSS. Make it modern and responsive.",
            "react": "Generate a React functional component with styled-components or Tailwind classes.",
            "css": "Generate CSS-only with class names that can be applied to semantic HTML.",
        }

        full_prompt = f"""{self.SYSTEM_PROMPT}

User Request: {prompt}

Output Format: {format_instructions.get(format, format_instructions['html'])}

Generate the complete code now:"""

        # Use Gemini 3 Pro with high thinking for better reasoning
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high")
            )
        )

        # Extract code from response
        code = response.text

        # Try to extract code block if wrapped in markdown
        if "```" in code:
            import re
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', code, re.DOTALL)
            if code_blocks:
                code = code_blocks[0]

        return self._success({
            "prompt": prompt,
            "format": format,
            "code": code,
            "model": "gemini-3-pro-preview"
        })

    def _generate_component(self, prompt: str, framework: str = "react") -> Dict[str, Any]:
        """Generate a reusable UI component"""
        if not prompt:
            return self._error("Prompt is required")

        client = self._get_client()

        framework_prompts = {
            "react": "Create a reusable React functional component with TypeScript types. Include props interface.",
            "vue": "Create a Vue 3 component with Composition API and TypeScript.",
            "svelte": "Create a Svelte component with TypeScript.",
            "html": "Create a reusable HTML/CSS component with CSS custom properties for theming."
        }

        full_prompt = f"""{self.SYSTEM_PROMPT}

User Request: {prompt}

Framework: {framework}
{framework_prompts.get(framework, framework_prompts['react'])}

Requirements:
- Self-contained component
- Accepts customization via props/attributes
- Includes basic styling
- Production-ready code

Generate the component code:"""

        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high")
            )
        )

        code = response.text

        # Extract code block
        if "```" in code:
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', code, re.DOTALL)
            if code_blocks:
                code = code_blocks[0]

        return self._success({
            "prompt": prompt,
            "framework": framework,
            "code": code,
            "model": "gemini-3-pro-preview"
        })

    def _generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "1K",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an image from a text prompt using Gemini 3 Pro Image"""
        if not prompt:
            return self._error("Prompt is required")

        client = self._get_client()

        # Use Gemini 3 Pro Image for best quality
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=resolution
                )
            )
        )

        # Extract image from response
        image_data = None
        text_response = None

        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                text_response = part.text
            elif hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data

        if not image_data:
            return self._error("No image generated")

        # Save image if output path provided
        saved_path = None
        if output_path:
            saved_path = Path(output_path)
            saved_path.parent.mkdir(parents=True, exist_ok=True)
            with open(saved_path, 'wb') as f:
                f.write(base64.b64decode(image_data) if isinstance(image_data, str) else image_data)

        return self._success({
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "saved_path": str(saved_path) if saved_path else None,
            "text_response": text_response,
            "image_base64": image_data[:100] + "..." if image_data else None,  # Truncated for display
            "model": "gemini-3-pro-image-preview"
        })

    def _edit_image(
        self,
        prompt: str,
        image_path: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Edit an existing image using Gemini image models"""
        if not prompt:
            return self._error("Prompt is required")
        if not image_path or not Path(image_path).exists():
            return self._error(f"Image path not found: {image_path}")

        client = self._get_client()

        # Read image as base64
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Determine mime type
        ext = Path(image_path).suffix.lower()
        mime_types = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif'}
        mime_type = mime_types.get(ext, 'image/png')

        # Build multimodal content
        contents = [
            {"text": prompt},
            {"inline_data": {"mime_type": mime_type, "data": image_base64}}
        ]

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",  # Use Flash for faster editing
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        # Extract edited image
        image_data = None
        text_response = None

        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                text_response = part.text
            elif hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data

        if not image_data:
            return self._error("No edited image generated")

        # Save edited image
        saved_path = None
        if output_path:
            saved_path = Path(output_path)
            saved_path.parent.mkdir(parents=True, exist_ok=True)
            with open(saved_path, 'wb') as f:
                f.write(base64.b64decode(image_data) if isinstance(image_data, str) else image_data)

        return self._success({
            "prompt": prompt,
            "original_image": image_path,
            "saved_path": str(saved_path) if saved_path else None,
            "text_response": text_response,
            "model": "gemini-2.5-flash-image"
        })

    def _generate_logo(self, prompt: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate a professional logo using Gemini 3 Pro Image"""
        if not prompt:
            return self._error("Prompt is required")

        # Enhance prompt for logo generation
        enhanced_prompt = f"""Create a modern, minimalist logo: {prompt}.
The design should be clean, professional, with bold typography.
The logo should work well in both light and dark backgrounds.
Make the text legible and well-placed."""

        return self._generate_image(enhanced_prompt, aspect_ratio="1:1", resolution="2K", output_path=output_path)

    def _generate_infographic(self, prompt: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate an infographic using Gemini 3 Pro Image"""
        if not prompt:
            return self._error("Prompt is required")

        client = self._get_client()

        # Use Google Search grounding for real-time data
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                    image_size="2K"
                ),
                tools=[{"google_search": {}}]  # Enable search grounding
            )
        )

        # Extract image
        image_data = None
        text_response = None

        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                text_response = part.text
            elif hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data

        if not image_data:
            return self._error("No infographic generated")

        # Save infographic
        saved_path = None
        if output_path:
            saved_path = Path(output_path)
            saved_path.parent.mkdir(parents=True, exist_ok=True)
            with open(saved_path, 'wb') as f:
                f.write(base64.b64decode(image_data) if isinstance(image_data, str) else image_data)

        return self._success({
            "prompt": prompt,
            "saved_path": str(saved_path) if saved_path else None,
            "text_response": text_response,
            "grounded": True,
            "model": "gemini-3-pro-image-preview"
        })


skill = StitchSkill()
