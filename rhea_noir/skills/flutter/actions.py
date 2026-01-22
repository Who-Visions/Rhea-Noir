"""
Flutter Vibe Skill - Actions
Generates premium Flutter code using the Vibe Engine standards (Riverpod, GoRouter, Deep Space Theme).
"""

from typing import Dict, Any, List, Optional
import os
from pathlib import Path

class FlutterSkill:
    name = "flutter"
    description = "Generate premium, Vibe-Coded Flutter applications"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a Senior Flutter Engineer specializing in the "Vibe-Coded" aesthetic.

    CORE STANDARDS:
    1. **Aesthetic**: Deep Space Theme (Bg: #050505, Primary: #6C63FF, Secondary: #00E5FF).
    2. **State Management**: flutter_riverpod (HooksConsumerWidget, Notifiers) - NO setState!
    3. **Navigation**: go_router (Typed routes preferred).
    4. **Architecture**: Feature-First (features/auth, features/home).
    5. **UI**: Material 3, Outfit/Inter fonts, smooth Curves.fastOutSlowIn animations.
    6. **Best Practices**: const constructors, immutability (freezed preferred), strict clean code.

    Your goal is to produce copy-paste ready, production-grade code that looks expensive and runs smooth.
    """

    @property
    def actions(self) -> List[str]:
        return [
            "scaffold_app",
            "generate_widget",
            "generate_feature",
            "explain_code"
        ]

    def _get_client(self):
        """Get Gemini 3 client"""
        try:
            from google import genai
            return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except ImportError:
            raise ImportError("google-genai package required")

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        try:
            if action == "scaffold_app":
                return self._scaffold_app(kwargs.get("name"), kwargs.get("description"))
            elif action == "generate_widget":
                return self._generate_widget(kwargs.get("prompt"), kwargs.get("name"))
            elif action == "generate_feature":
                return self._generate_feature(kwargs.get("name"), kwargs.get("requirements"))
            elif action == "explain_code":
                return self._explain_code(kwargs.get("code"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _scaffold_app(self, name: str, description: str) -> Dict[str, Any]:
        """Generate a project structure and key files for a new Vibe app."""
        if not name: return {"success": False, "error": "App name required"}

        client = self._get_client()
        from google.genai import types

        prompt = f"""{self.SYSTEM_PROMPT}

        TASK: Scaffold a new Flutter app named '{name}'.
        DESCRIPTION: {description or 'A premium Flutter app'}

        OUTPUT: Generate the folder structure and content for these key files:
        1. lib/main.dart (ProviderScope, App entry)
        2. lib/core/theme/app_theme.dart (The Vibe Theme definition)
        3. lib/core/router/app_router.dart (GoRouter setup)
        4. lib/features/home/presentation/home_screen.dart (A beautiful landing screen)

        Use standard markdown code blocks for each file, labeled with the filename.
        """

        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high")
            )
        )

        return {
            "success": True,
            "result": response.text,
            "model": "gemini-3-pro-preview"
        }

    def _generate_widget(self, prompt: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Generate a single reusable Vibe widget."""
        if not prompt: return {"success": False, "error": "Prompt required"}

        client = self._get_client()

        prompt_str = f"""{self.SYSTEM_PROMPT}

        TASK: Create a premium Flutter widget.
        NAME: {name or 'CustomWidget'}
        REQUIREMENTS: {prompt}

        Use HooksConsumerWidget if state is needed, or ConsumerWidget/StatelessWidget.
        Ensure it uses the VibeTheme (Theme.of(context)) colors.
        """

        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt_str
        )

        return {
            "success": True,
            "result": response.text
        }

    def _generate_feature(self, name: str, requirements: str) -> Dict[str, Any]:
        """Generate a full feature slice (domain, data, presentation)."""
        if not name: return {"success": False, "error": "Feature name required"}

        client = self._get_client()

        prompt = f"""{self.SYSTEM_PROMPT}

        TASK: architect a full feature slice for '{name}'.
        REQUIREMENTS: {requirements}

        Generate the following files/classes:
        1. Domain: Entity class (freezed)
        2. Data: Simple Repository (Provider)
        3. Presentation: Controller/Notifier (Riverpod)
        4. Presentation: a Screen widget using the controller.

        Adhere stricly to the Feature-First directory structure.
        """

        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="high")
            )
        )

        return {
            "success": True,
            "result": response.text
        }

    def _explain_code(self, code: str) -> Dict[str, Any]:
        """Analyze and explain Dart text."""
        if not code: return {"success": False, "error": "Code required"}

        client = self._get_client()

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"{self.SYSTEM_PROMPT}\n\nAct as a mentor. Explain this code, verify if it follows Vibe standards, and suggest improvements:\n\n{code}"
        )

        return {
            "success": True,
            "result": response.text
        }

skill = FlutterSkill()
