"""
Gemini Computer Use Skill for Rhea-Noir
Browser automation using AI vision and control
"""
import time
from typing import Optional, Dict, Any, List


# Screen dimensions (recommended for Computer Use)
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900


def denormalize_x(x: int, screen_width: int = SCREEN_WIDTH) -> int:
    """Convert normalized x coordinate (0-1000) to actual pixel coordinate."""
    return int(x / 1000 * screen_width)


def denormalize_y(y: int, screen_height: int = SCREEN_HEIGHT) -> int:
    """Convert normalized y coordinate (0-1000) to actual pixel coordinate."""
    return int(y / 1000 * screen_height)


class ComputerUseSkill:
    """Skill for Gemini Computer Use browser automation."""

    name = "computeruse"
    version = "1.0.0"
    description = "Gemini Computer Use - AI-powered browser automation"

    MODEL = "gemini-2.5-computer-use-preview-10-2025"

    def __init__(self):
        self._client = None
        self._playwright = None
        self._browser = None
        self._page = None

    def _get_client(self):
        """Get Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client()
            except ImportError as e:
                raise ImportError("google-genai not installed. Run: pip install google-genai") from e
        return self._client

    def _success(self, data: Any) -> Dict:
        """Return success response."""
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        """Return error response."""
        return {"success": False, "error": message}

    def _init_browser(self, headless: bool = False):
        """Initialize Playwright browser."""
        if self._browser is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as e:
            raise ImportError("playwright not installed. Run: pip install playwright && playwright install chromium") from e

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=headless)
        context = self._browser.new_context(
            viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
        )
        self._page = context.new_page()

    def _close_browser(self):
        """Close browser and cleanup."""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        self._page = None

    def _take_screenshot(self) -> bytes:
        """Capture current page screenshot."""
        if not self._page:
            raise RuntimeError("Browser not initialized")
        return self._page.screenshot(type="png")

    def _execute_action(self, function_call) -> Dict:
        """Execute a single Computer Use action."""
        fname = function_call.name
        args = function_call.args
        result = {}

        try:
            if fname == "open_web_browser":
                pass  # Already open

            elif fname == "navigate":
                self._page.goto(args["url"])

            elif fname == "click_at":
                x = denormalize_x(args["x"])
                y = denormalize_y(args["y"])
                self._page.mouse.click(x, y)

            elif fname == "type_text_at":
                x = denormalize_x(args["x"])
                y = denormalize_y(args["y"])
                text = args["text"]
                press_enter = args.get("press_enter", True)
                clear_first = args.get("clear_before_typing", True)

                self._page.mouse.click(x, y)
                if clear_first:
                    self._page.keyboard.press("Control+A")
                    self._page.keyboard.press("Backspace")
                self._page.keyboard.type(text)
                if press_enter:
                    self._page.keyboard.press("Enter")

            elif fname == "scroll_document":
                direction = args["direction"]
                if direction == "down":
                    self._page.keyboard.press("PageDown")
                elif direction == "up":
                    self._page.keyboard.press("PageUp")
                elif direction == "left":
                    self._page.keyboard.press("Home")
                elif direction == "right":
                    self._page.keyboard.press("End")

            elif fname == "scroll_at":
                x = denormalize_x(args["x"])
                y = denormalize_y(args["y"])
                direction = args["direction"]
                magnitude = args.get("magnitude", 800)

                self._page.mouse.move(x, y)
                if direction == "down":
                    self._page.mouse.wheel(0, magnitude)
                elif direction == "up":
                    self._page.mouse.wheel(0, -magnitude)
                elif direction == "right":
                    self._page.mouse.wheel(magnitude, 0)
                elif direction == "left":
                    self._page.mouse.wheel(-magnitude, 0)

            elif fname == "hover_at":
                x = denormalize_x(args["x"])
                y = denormalize_y(args["y"])
                self._page.mouse.move(x, y)

            elif fname == "key_combination":
                keys = args["keys"]
                self._page.keyboard.press(keys)

            elif fname == "go_back":
                self._page.go_back()

            elif fname == "go_forward":
                self._page.go_forward()

            elif fname == "search":
                self._page.goto("https://www.google.com")

            elif fname == "wait_5_seconds":
                time.sleep(5)

            elif fname == "drag_and_drop":
                x = denormalize_x(args["x"])
                y = denormalize_y(args["y"])
                dest_x = denormalize_x(args["destination_x"])
                dest_y = denormalize_y(args["destination_y"])
                self._page.mouse.move(x, y)
                self._page.mouse.down()
                self._page.mouse.move(dest_x, dest_y)
                self._page.mouse.up()

            else:
                result["warning"] = f"Unknown action: {fname}"

            # Wait for page to settle
            try:
                self._page.wait_for_load_state(timeout=5000)
            except:
                pass
            time.sleep(0.5)

        except Exception as e:
            result["error"] = str(e)

        return result

    def run_task(
        self,
        goal: str,
        start_url: str = "https://www.google.com",
        max_steps: int = 10,
        headless: bool = False,
        excluded_actions: Optional[List[str]] = None,
        require_human_confirmation: bool = False
    ) -> Dict:
        """
        Run a multi-step browser automation task.

        Args:
            goal: Natural language description of the task
            start_url: Starting URL for the browser
            max_steps: Maximum number of action steps
            headless: Run browser in headless mode
            excluded_actions: List of actions to exclude
            require_human_confirmation: Require user confirmation for risky actions

        Returns:
            Dict with task results, screenshots, and final answer
        """
        try:
            from google.genai import types
            from google.genai.types import Content, Part

            client = self._get_client()

            # Initialize browser
            self._init_browser(headless=headless)
            self._page.goto(start_url)

            # Build tool config
            computer_use_config = {
                'environment': types.Environment.ENVIRONMENT_BROWSER
            }
            if excluded_actions:
                computer_use_config['excluded_predefined_functions'] = excluded_actions

            config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        computer_use=types.ComputerUse(**computer_use_config)
                    )
                ]
            )

            # Initial screenshot
            screenshot = self._take_screenshot()

            # Build conversation
            contents = [
                Content(
                    role="user",
                    parts=[
                        Part(text=goal),
                        Part.from_bytes(data=screenshot, mime_type='image/png')
                    ]
                )
            ]

            steps_taken = []
            final_answer = None

            # Agent loop
            for step in range(max_steps):
                response = client.models.generate_content(
                    model=self.MODEL,
                    contents=contents,
                    config=config
                )

                candidate = response.candidates[0]
                contents.append(candidate.content)

                # Check for function calls
                function_calls = [
                    part.function_call for part in candidate.content.parts
                    if part.function_call
                ]

                if not function_calls:
                    # No more actions - extract final text
                    text_parts = [
                        part.text for part in candidate.content.parts if part.text
                    ]
                    final_answer = " ".join(text_parts)
                    break

                # Execute actions
                function_responses = []
                for fc in function_calls:
                    # Check for safety decision
                    if require_human_confirmation and 'safety_decision' in fc.args:
                        decision = fc.args['safety_decision']
                        if decision.get('decision') == 'require_confirmation':
                            # In production, prompt user here
                            steps_taken.append({
                                "action": fc.name,
                                "status": "requires_confirmation",
                                "explanation": decision.get('explanation')
                            })
                            continue

                    # Execute the action
                    result = self._execute_action(fc)
                    steps_taken.append({
                        "step": step + 1,
                        "action": fc.name,
                        "args": dict(fc.args) if fc.args else {},
                        "result": result
                    })

                    # Capture new state
                    screenshot = self._take_screenshot()
                    current_url = self._page.url

                    function_responses.append(
                        types.FunctionResponse(
                            name=fc.name,
                            response={"url": current_url, **result},
                            parts=[
                                types.FunctionResponsePart(
                                    inline_data=types.FunctionResponseBlob(
                                        mime_type="image/png",
                                        data=screenshot
                                    )
                                )
                            ]
                        )
                    )

                # Add function responses to conversation
                if function_responses:
                    contents.append(
                        Content(
                            role="user",
                            parts=[Part(function_response=fr) for fr in function_responses]
                        )
                    )

            return self._success({
                "goal": goal,
                "steps_taken": steps_taken,
                "total_steps": len(steps_taken),
                "final_answer": final_answer,
                "final_url": self._page.url if self._page else None
            })

        except Exception as e:
            return self._error(str(e))
        finally:
            self._close_browser()

    def navigate(self, url: str) -> Dict:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to

        Returns:
            Dict with navigation result
        """
        try:
            self._init_browser()
            self._page.goto(url)
            return self._success({
                "url": url,
                "title": self._page.title()
            })
        except Exception as e:
            return self._error(str(e))

    def take_screenshot(self, output_path: Optional[str] = None) -> Dict:
        """
        Take a screenshot of the current page.

        Args:
            output_path: Optional path to save screenshot

        Returns:
            Dict with screenshot data or path
        """
        try:
            if not self._page:
                return self._error("Browser not initialized. Call navigate() first.")

            screenshot = self._take_screenshot()

            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(screenshot)
                return self._success({"saved_to": output_path})

            return self._success({
                "screenshot_bytes": len(screenshot),
                "format": "png"
            })
        except Exception as e:
            return self._error(str(e))


# Singleton instance
skill = ComputerUseSkill()
