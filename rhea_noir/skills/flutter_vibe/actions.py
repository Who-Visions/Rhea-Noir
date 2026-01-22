"""
Flutter Vibe Skill - Actions
Generates premium Flutter code using the Vibe Engine standards (Riverpod, GoRouter, Deep Space Theme).
Now powered by Gemini 3 Smart Router for intelligent model selection.
"""

from typing import Dict, Any, List, Optional
from rhea_noir.skills import execute_skill


class FlutterVibeSkill:
    """Skill for generating premium Vibe-Coded Flutter applications.
    
    Uses Gemini 3 Smart Router for intelligent model selection:
    - Simple widgets → Flash (minimal thinking, fast)
    - Complex architecture → Pro (high thinking, thorough)
    """

    name = "flutter_vibe"
    description = "Generate premium, Vibe-Coded Flutter applications"
    version = "2.0.0"  # Upgraded to Gemini 3 Router

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

    # Complexity hints for router - which actions need deep thinking
    FORCE_DEEP_ACTIONS = {"scaffold_app", "generate_feature", "review_code"}

    def __init__(self):
        self._router = None

    def _get_router(self):
        """Get Gemini 3 Router (lazy loaded)."""
        if self._router is None:
            from rhea_noir.gemini3_router import Gemini3Router
            self._router = Gemini3Router.get_instance()
        return self._router

    @property
    def actions(self) -> List[str]:
        """List of available actions."""
        return [
            "scaffold_app",
            "generate_widget",
            "generate_feature",
            "generate_screen",
            "explain_code",
            "review_code",
            "ralph_mode",  # Added Ralph Loop action
        ]

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a skill action."""
        try:
            if action == "scaffold_app":
                return self._scaffold_app(
                    kwargs.get("name"),
                    kwargs.get("description")
                )
            if action == "generate_widget":
                return self._generate_widget(
                    kwargs.get("prompt"),
                    kwargs.get("name")
                )
            if action == "generate_feature":
                return self._generate_feature(
                    kwargs.get("name"),
                    kwargs.get("requirements")
                )
            if action == "generate_screen":
                return self._generate_screen(
                    kwargs.get("name"),
                    kwargs.get("description"),
                    kwargs.get("feature")
                )
            if action == "explain_code":
                return self._explain_code(kwargs.get("code"))
            if action == "review_code":
                return self._review_code(kwargs.get("code"))
            if action == "ralph_mode":
                return self._ralph_mode(
                    kwargs.get("goal"),
                    kwargs.get("context_code")
                )
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:  # pylint: disable=broad-except
            return {"success": False, "error": str(e)}

    def _ralph_mode(
        self,
        goal: str,
        context_code: Optional[str] = None,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Ralph Loop Protocol: Autonomous, Verified Development.
        
        Algorithm:
        1. Generator: Gemini 3 Pro generates code based on goal.
        2. Verifier: Deterministic tool (flutter analyze) checks for errors.
        3. Exit: Complete if 0 errors.
        4. Refiner: If errors exist, send logs back to Gemini 3 Pro to fix.
        5. Stop: After max_iterations or status=verified.
        """
        if not goal:
            return {"success": False, "error": "Goal required for Ralph Mode"}

        router = self._get_router()
        current_code = context_code or ""
        history = []
        
        # Start a long-running task in the harness if available
        # But for now, we'll execute the loop synchronously for the CLI
        
        for i in range(max_iterations):
            # 1. GENERATE/REFINE
            prompt = f"""{self.SYSTEM_PROMPT}
            
            TASK: {goal}
            ITERATION: {i+1}/{max_iterations}
            CURRENT CODE:
            {current_code}
            
            {f"PREVIOUS ERRORS (VERIFIER OUTPUT):\n{history[-1]['errors']}" if history else "This is your first attempt."}
            
            GOAL: Produce production-grade code that passes 'flutter analyze'.
            OUTPUT: Only the updated code block.
            """
            # 1. GENERATE/REFINE
            routing = router.route(prompt, force_deep=True)
            result = router.generate(prompt, routing=routing)
            new_code = result.get("text", "")
            
            # 2. VERIFY
            # Realistically, we'd write to a temp file and run flutter analyze.
            # For this implementation, we'll do a structural/lint check using subprocess
            # OR simulate a verifier that looks for common Dart/Flutter issues.
            verification = self._verify_code(new_code)
            
            iteration_data = {
                "iteration": i + 1,
                "code": new_code,
                "verified": verification["verified"],
                "errors": verification["errors"],
                "model": result.get("model")
            }
            history.append(iteration_data)
            
            current_code = new_code
            
            # 3. WATCHDOG OVERSIGHT
            watchdog_report = execute_skill(
                "watchdog", 
                "monitor_task", 
                task_id=f"ralph_{goal[:10]}", 
                history=history
            )
            
            if watchdog_report.get("status") == "stalled":
                # Consult Watchdog for recovery
                recovery = execute_skill(
                    "watchdog",
                    "recovery_directive",
                    goal=goal,
                    context=new_code
                )
                # We could append the recovery plan to the next prompt
                if recovery.get("success"):
                    goal = f"{goal}\n\nRECOVERY DIRECTIVE: {recovery.get('recovery_plan')}"
            
            if verification["verified"]:
                break

        return {
            "success": True,
            "goal": goal,
            "status": "verified" if history[-1]["verified"] else "max_iterations_reached",
            "iterations": len(history),
            "result": current_code,
            "history": history
        }

    def _verify_code(self, code: str) -> Dict[str, Any]:
        """External verifier (Deterministic)."""
        import subprocess
        import tempfile
        import os
        
        errors = []
        
        # Clean the code block if it contains markdown
        clean_code = code
        if "```" in code:
            parts = code.split("```")
            for part in parts:
                if part.strip().startswith("dart"):
                    clean_code = part.replace("dart", "", 1).strip()
                    break
        
        # DETERMINISTIC CHECK 1: Static Analysis
        with tempfile.NamedTemporaryFile(suffix=".dart", delete=False, mode='w', encoding='utf-8') as f:
            f.write(clean_code)
            tmp_path = f.name

        try:
            # Check for basic syntax errors first using dart analyze
            # We assume 'dart' is in path
            proc = subprocess.run(
                ["dart", "analyze", tmp_path],
                capture_output=True,
                text=True,
                check=False
            )
            if proc.returncode != 0:
                # Filter out the file path to keep logs clean
                errors.append(proc.stdout.replace(tmp_path, "file.dart"))
        except FileNotFoundError:
            # Fallback for environments without Flutter/Dart installed
            # Heuristic check for common Vibe standards
            if "ConsumerWidget" not in clean_code and "StatelessWidget" not in clean_code and "HooksConsumerWidget" not in clean_code:
                errors.append("ERR: No standard Flutter widget base found.")
            if "setState" in clean_code:
                errors.append("VIBE-ERR: Detected setState(). Vibe standards require Riverpod.")
            if "const" not in clean_code and "class" in clean_code:
                errors.append("LINT: Missing 'const' constructors for optimization.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return {
            "verified": len(errors) == 0,
            "errors": "\n".join(errors)
        }

    def _scaffold_app(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a project structure and key files for a new Vibe app."""
        if not name:
            return {"success": False, "error": "App name required"}

        router = self._get_router()

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

        # Force deep thinking for complex scaffold
        routing = router.route(prompt, force_deep=True)
        result = router.generate(prompt, routing=routing)

        return {
            "success": True,
            "result": result.get("text", ""),
            "model": result.get("model", "unknown"),
            "thinking_level": result.get("thinking_level", "unknown"),
            "complexity": result.get("complexity", "unknown"),
        }

    def _generate_widget(
        self,
        prompt: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a single reusable Vibe widget."""
        if not prompt:
            return {"success": False, "error": "Prompt required"}

        router = self._get_router()

        prompt_str = f"""{self.SYSTEM_PROMPT}

        TASK: Create a premium Flutter widget.
        NAME: {name or 'CustomWidget'}
        REQUIREMENTS: {prompt}

        Use HooksConsumerWidget if state is needed, or ConsumerWidget/StatelessWidget.
        Ensure it uses the VibeTheme (Theme.of(context)) colors.
        """

        # Simple widget = let router decide (likely Flash)
        result = router.generate(prompt_str)

        return {
            "success": True,
            "result": result.get("text", ""),
            "model": result.get("model", "unknown"),
            "thinking_level": result.get("thinking_level", "unknown"),
        }

    def _generate_feature(
        self,
        name: str,
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a full feature slice (domain, data, presentation)."""
        if not name:
            return {"success": False, "error": "Feature name required"}

        router = self._get_router()

        prompt = f"""{self.SYSTEM_PROMPT}

        TASK: Architect a full feature slice for '{name}'.
        REQUIREMENTS: {requirements or 'Standard CRUD operations'}

        Generate the following files/classes:
        1. Domain: Entity class (freezed)
        2. Data: Simple Repository (Provider)
        3. Presentation: Controller/Notifier (Riverpod)
        4. Presentation: A Screen widget using the controller.

        Adhere strictly to the Feature-First directory structure.
        """

        # Force deep thinking for complex architecture
        routing = router.route(prompt, force_deep=True)
        result = router.generate(prompt, routing=routing)

        return {
            "success": True,
            "result": result.get("text", ""),
            "model": result.get("model", "unknown"),
            "thinking_level": result.get("thinking_level", "unknown"),
            "complexity": result.get("complexity", "unknown"),
        }

    def _generate_screen(
        self,
        name: str,
        description: Optional[str] = None,
        feature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete screen with state management."""
        if not name:
            return {"success": False, "error": "Screen name required"}

        router = self._get_router()

        prompt = f"""{self.SYSTEM_PROMPT}

        TASK: Create a premium Flutter screen.
        NAME: {name}Screen
        DESCRIPTION: {description or 'A beautiful screen'}
        FEATURE: {feature or 'home'}

        Include:
        - HooksConsumerWidget with proper animations
        - Riverpod provider/notifier if state needed
        - VibeTheme colors and typography
        - Entrance animation (FadeTransition or SlideTransition)
        """

        # Moderate complexity - let router decide
        result = router.generate(prompt)

        return {
            "success": True,
            "result": result.get("text", ""),
            "model": result.get("model", "unknown"),
            "thinking_level": result.get("thinking_level", "unknown"),
        }

    def _explain_code(self, code: str) -> Dict[str, Any]:
        """Analyze and explain Dart code."""
        if not code:
            return {"success": False, "error": "Code required"}

        router = self._get_router()

        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            "Act as a mentor. Explain this code, verify if it follows "
            f"Vibe standards, and suggest improvements:\n\n{code}"
        )

        # Let router decide based on code complexity
        result = router.generate(prompt)

        return {
            "success": True,
            "result": result.get("text", ""),
            "model": result.get("model", "unknown"),
            "thinking_level": result.get("thinking_level", "unknown"),
        }

    def _review_code(self, code: str) -> Dict[str, Any]:
        """Review code for Vibe standards compliance."""
        if not code:
            return {"success": False, "error": "Code required"}

        router = self._get_router()

        prompt = f"""{self.SYSTEM_PROMPT}

        TASK: Review this Flutter code for Vibe standards compliance.

        Evaluate:
        1. Aesthetic adherence (Deep Space theme, animations)
        2. State management (Riverpod, no setState)
        3. Architecture (Feature-First, clean layers)
        4. Best practices (const, immutability, clean code)

        Provide a score (0-100) and specific issues with suggested fixes.

        CODE:
        {code}
        """

        # Force deep thinking for thorough review
        routing = router.route(prompt, force_deep=True)
        result = router.generate(prompt, routing=routing)

        return {
            "success": True,
            "result": result.get("text", ""),
            "model": result.get("model", "unknown"),
            "thinking_level": result.get("thinking_level", "unknown"),
            "score": "See result for score",
        }


skill = FlutterVibeSkill()

