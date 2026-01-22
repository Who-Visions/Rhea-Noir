"""
Rhea Noir Intent Detection - Automatic action selection
Rhea thinks for the user - detects what they need from context
"""

import re
from typing import List, Dict, Any, Optional
from enum import Enum, auto


class Intent(Enum):
    """Detected user intents"""
    CHAT = auto()              # Regular conversation
    SEARCH_WEB = auto()        # Needs web search/grounding
    SEARCH_KNOWLEDGE = auto()  # Needs knowledge base search
    SEARCH_MEMORY = auto()     # Needs memory recall
    CODE_GENERATE = auto()     # Generate code
    CODE_DEBUG = auto()        # Debug/fix code
    CODE_EXPLAIN = auto()      # Explain code
    ANALYZE_IMAGE = auto()     # Image analysis
    LONG_TASK = auto()         # Long-running task needed
    RESEARCH = auto()          # Deep research needed


class IntentDetector:
    """
    Detects user intent from query context.
    Rhea uses this to automatically decide what actions to take.
    Uses intelligent contextual clues:
    - Conversation history
    - Code blocks presence
    - Time patterns
    - User's evolution data
    """

    # Intent patterns - Rhea looks for these signals
    PATTERNS = {
        Intent.SEARCH_WEB: [
            r'\b(search|google|find|look up|what is|who is|latest|news|current)\b',
            r'\b(2024|2025|today|yesterday|recently|this week)\b',
            r'\b(how do i|how to|tutorial|guide)\b',
        ],
        Intent.SEARCH_KNOWLEDGE: [
            r'\b(in (my|the|our) (docs|documents|files|notes|knowledge))\b',
            r'\b(from (my|the|our) (docs|documents|files|notes))\b',
            r'\b(according to|based on|reference|documentation)\b',
        ],
        Intent.SEARCH_MEMORY: [
            r'\b(remember|recalled|we (talked|discussed|said)|earlier|before)\b',
            r'\b(last (time|session|conversation))\b',
            r'\b(you (told|said|mentioned))\b',
        ],
        Intent.CODE_GENERATE: [
            r'\b(write|create|generate|build|make|implement) (a |an |the |some )?(code|function|class|script|program|app)\b',
            r'\b(code (for|to)|write me|create a)\b',
        ],
        Intent.CODE_DEBUG: [
            r'\b(debug|fix|error|bug|issue|problem|broken|not working|fails)\b',
            r'\b(why (is|does|doesn\'t)|what\'s wrong)\b',
            r'\btraceback\b',
        ],
        Intent.CODE_EXPLAIN: [
            r'\b(explain|what does|how does|understand|walk me through)\b.*(code|function|class|this)\b',
            r'\b(can you explain|tell me about|describe)\b',
        ],
        Intent.ANALYZE_IMAGE: [
            r'\b(image|picture|photo|screenshot|diagram|chart|graph)\b',
            r'\b(look at|see|analyze|describe|what\'s in)\b.*(this|the|my)\b',
            r'\b(attached|uploaded|shared)\b',
        ],
        Intent.LONG_TASK: [
            r'\b(build|create|develop|implement) (a |an |the )?(full|complete|entire|whole)\b',
            r'\b(project|application|system|platform)\b',
            r'\b(step by step|end to end|from scratch)\b',
        ],
        Intent.RESEARCH: [
            r'\b(research|analyze|investigate|deep dive|comprehensive|thorough)\b',
            r'\b(compare|evaluate|assess|review)\b.*(options|alternatives|approaches)\b',
        ],
    }

    # Keywords that boost confidence for each intent
    BOOSTERS = {
        Intent.SEARCH_WEB: ['latest', 'current', 'news', '2025', '2024', 'now'],
        Intent.SEARCH_MEMORY: ['we', 'you said', 'remember', 'earlier'],
        Intent.CODE_GENERATE: ['python', 'javascript', 'function', 'class', 'api'],
        Intent.CODE_DEBUG: ['error', 'exception', 'traceback', 'failed'],
        Intent.ANALYZE_IMAGE: ['image', 'picture', 'screenshot', 'photo'],
    }

    # Contextual clues - what came before affects interpretation
    CONTEXT_CLUES = {
        # If previous message was about code, current is likely code-related
        "code_block": [Intent.CODE_DEBUG, Intent.CODE_EXPLAIN],
        # If discussing a project, likely long task
        "project_mention": [Intent.LONG_TASK],
        # If URLs were shared, might need web info
        "url_present": [Intent.SEARCH_WEB],
        # If files were mentioned, might need knowledge search
        "file_mention": [Intent.SEARCH_KNOWLEDGE],
    }

    def __init__(self):
        self.recent_intents: List[Intent] = []
        self.conversation_context: List[Dict] = []

    def detect(  # pylint: disable=too-many-branches
        self,
        query: str,
        has_image: bool = False,
        context: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Detect intent from user query with intelligent contextual clues.

        Args:
            query: User's message
            has_image: Whether an image is attached
            context: Recent conversation context

        Returns:
            Dict with:
                - primary_intent: Main detected intent
                - intents: All detected intents with confidence
                - actions: Recommended actions for Rhea
                - context_clues: What context influenced the decision
        """
        query_lower = query.lower()
        detected: Dict[Intent, float] = {}
        context_clues_found: List[str] = []

        # Update conversation context
        if context:
            self.conversation_context = context[-10:]

        # ===== CONTEXTUAL CLUES ANALYSIS =====

        # 1. Check for code blocks in query or recent context
        has_code = bool(re.search(r'```|def |class |function |import ', query))
        if has_code:
            context_clues_found.append("code_block_present")
            detected[Intent.CODE_DEBUG] = detected.get(Intent.CODE_DEBUG, 0) + 0.2
            detected[Intent.CODE_EXPLAIN] = detected.get(Intent.CODE_EXPLAIN, 0) + 0.2

        # 2. Check for URLs
        has_url = bool(re.search(r'https?://|www\.', query))
        if has_url:
            context_clues_found.append("url_present")
            detected[Intent.SEARCH_WEB] = detected.get(Intent.SEARCH_WEB, 0) + 0.2

        # 3. Check for file references
        has_file = bool(re.search(r'\.(py|js|ts|json|md|txt|csv|yaml|yml|html|css)\b', query_lower))
        if has_file:
            context_clues_found.append("file_reference")
            detected[Intent.SEARCH_KNOWLEDGE] = detected.get(Intent.SEARCH_KNOWLEDGE, 0) + 0.2

        # 4. Check recent conversation for code/project context
        if self.conversation_context:
            recent_text = " ".join([m.get("content", "") for m in self.conversation_context[-3:]])
            if "```" in recent_text or "def " in recent_text:
                context_clues_found.append("recent_code_discussion")
                detected[Intent.CODE_DEBUG] = detected.get(Intent.CODE_DEBUG, 0) + 0.15
            if any(w in recent_text.lower() for w in ["project", "build", "implement", "feature"]):
                context_clues_found.append("project_context")
                detected[Intent.LONG_TASK] = detected.get(Intent.LONG_TASK, 0) + 0.15

        # 5. Check for continuation patterns ("this", "that", "it")
        if re.search(r'^(this|that|it|the same|again)\b', query_lower):
            context_clues_found.append("continuation_pattern")
            # Boost based on previous intent
            if self.recent_intents:
                last_intent = self.recent_intents[-1]
                detected[last_intent] = detected.get(last_intent, 0) + 0.3

        # 6. Check for image attachment
        if has_image:
            context_clues_found.append("image_attached")
            detected[Intent.ANALYZE_IMAGE] = 1.0

        # ===== PATTERN MATCHING =====

        # Match explicit patterns
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    detected[intent] = detected.get(intent, 0) + 0.3

        # Apply keyword boosters
        for intent, keywords in self.BOOSTERS.items():
            for kw in keywords:
                if kw in query_lower:
                    detected[intent] = detected.get(intent, 0) + 0.2

        # Cap at 1.0
        detected = {k: min(v, 1.0) for k, v in detected.items()}

        # Determine primary intent
        if detected:
            primary = max(detected, key=detected.get)
        else:
            primary = Intent.CHAT
            detected[Intent.CHAT] = 1.0

        # Build recommended actions
        actions = self._build_actions(detected, query)

        # Track for future context
        self.recent_intents.append(primary)
        self.recent_intents = self.recent_intents[-10:]

        return {
            "primary_intent": primary,
            "intents": {k.name: v for k, v in detected.items()},
            "actions": actions,
            "context_clues": context_clues_found,
        }

    def _build_actions(
        self,
        intents: Dict[Intent, float],
        query: str,
    ) -> List[Dict[str, Any]]:
        """Build action list based on detected intents"""
        actions = []

        for intent, confidence in sorted(intents.items(), key=lambda x: -x[1]):
            if confidence < 0.3:
                continue

            if intent == Intent.SEARCH_WEB:
                actions.append({
                    "action": "search_web",
                    "confidence": confidence,
                    "params": {"query": query},
                })
            elif intent == Intent.SEARCH_KNOWLEDGE:
                actions.append({
                    "action": "search_knowledge",
                    "confidence": confidence,
                    "params": {"query": query},
                })
            elif intent == Intent.SEARCH_MEMORY:
                actions.append({
                    "action": "search_memory",
                    "confidence": confidence,
                    "params": {"query": query},
                })
            elif intent == Intent.ANALYZE_IMAGE:
                actions.append({
                    "action": "use_image_model",
                    "confidence": confidence,
                    "params": {"model": "gemini-3-pro-image-preview"},
                })
            elif intent == Intent.RESEARCH:
                actions.append({
                    "action": "use_elite_model",
                    "confidence": confidence,
                    "params": {"model": "gemini-3-pro-preview"},
                })
            elif intent == Intent.LONG_TASK:
                actions.append({
                    "action": "create_task",
                    "confidence": confidence,
                    "params": {"description": query},
                })

        return actions

    def should_search_web(self, query: str) -> bool:
        """Quick check if web search is needed"""
        result = self.detect(query)
        return Intent.SEARCH_WEB in [
            Intent[k] for k, v in result["intents"].items() if v >= 0.5
        ]

    def should_search_memory(self, query: str) -> bool:
        """Quick check if memory search is needed"""
        result = self.detect(query)
        return Intent.SEARCH_MEMORY in [
            Intent[k] for k, v in result["intents"].items() if v >= 0.5
        ]

    def get_model_recommendation(self, query: str, has_image: bool = False) -> str:
        """Get recommended model based on intent"""
        result = self.detect(query, has_image=has_image)

        actions = result["actions"]
        for action in actions:
            if action["action"] == "use_image_model":
                return "gemini-3-pro-image-preview"
            elif action["action"] == "use_elite_model":
                return "gemini-3-pro-preview"

        # Default based on complexity
        if any(k in result["intents"] for k in ["CODE_DEBUG", "CODE_EXPLAIN"]):
            return "gemini-2.5-pro"

        return "gemini-2.5-flash"


# Global detector instance
detector = IntentDetector()
