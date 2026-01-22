"""
Rhea Noir Evolution System - Learning and adaptation
Tracks success, preferences, and evolves over time
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class EvolutionTracker:
    """Tracks Rhea's learning and evolution over time"""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize evolution tracker"""
        if data_dir is None:
            data_dir = Path.home() / ".rhea_noir" / "harness"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.evolution_file = self.data_dir / "evolution.json"
        self._load()

    def _load(self):
        """Load evolution state from disk"""
        if self.evolution_file.exists():
            with open(self.evolution_file, encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        # Initialize with defaults
        self.keyword_weights: Dict[str, float] = data.get("keyword_weights", {})
        self.preferences: Dict[str, Any] = data.get("preferences", {
            "response_length": "balanced",  # brief, balanced, detailed
            "code_style": "modern",         # modern, classic, minimal
            "explanation_depth": "medium",  # shallow, medium, deep
        })
        self.feedback_history: List[Dict] = data.get("feedback_history", [])
        self.success_rate: Dict[str, Dict] = data.get("success_rate", {})
        self.session_count = data.get("session_count", 0)

    def _save(self):
        """Save evolution state to disk"""
        data = {
            "keyword_weights": self.keyword_weights,
            "preferences": self.preferences,
            "feedback_history": self.feedback_history[-100:],  # Keep last 100
            "success_rate": self.success_rate,
            "session_count": self.session_count,
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.evolution_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def record_feedback(self, is_positive: bool, context: Optional[str] = None):
        """Record user feedback on last response"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "positive": is_positive,
            "context": context,
        }
        self.feedback_history.append(entry)

        # Update success rate
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.success_rate:
            self.success_rate[today] = {"positive": 0, "negative": 0}

        if is_positive:
            self.success_rate[today]["positive"] += 1
        else:
            self.success_rate[today]["negative"] += 1

        self._save()

    def boost_keywords(self, keywords: List[str], boost: float = 0.1):
        """Increase importance of keywords based on usage"""
        for kw in keywords:
            current = self.keyword_weights.get(kw, 1.0)
            self.keyword_weights[kw] = min(current + boost, 5.0)  # Cap at 5x

        self._save()

    def decay_keywords(self, decay_rate: float = 0.01):
        """Slowly decay unused keyword weights"""
        for kw in list(self.keyword_weights.keys()):
            self.keyword_weights[kw] = max(
                self.keyword_weights[kw] - decay_rate,
                0.5  # Min weight
            )
            if self.keyword_weights[kw] <= 0.5:
                del self.keyword_weights[kw]

        self._save()

    def get_top_keywords(self, n: int = 10) -> List[tuple]:
        """Get most important keywords"""
        sorted_kw = sorted(
            self.keyword_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_kw[:n]

    def update_preference(self, key: str, value: Any):
        """Update a preference setting"""
        self.preferences[key] = value
        self._save()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value"""
        return self.preferences.get(key, default)

    def get_success_stats(self) -> Dict[str, Any]:
        """Get overall success statistics"""
        total_positive = sum(d["positive"] for d in self.success_rate.values())
        total_negative = sum(d["negative"] for d in self.success_rate.values())
        total = total_positive + total_negative

        return {
            "total_feedback": total,
            "positive": total_positive,
            "negative": total_negative,
            "success_rate": total_positive / total if total > 0 else 0,
            "sessions": self.session_count,
        }

    def start_session(self):
        """Record a new session start"""
        self.session_count += 1
        self._save()

    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get a summary of Rhea's evolution"""
        stats = self.get_success_stats()
        top_keywords = self.get_top_keywords(5)

        return {
            "sessions": stats["sessions"],
            "success_rate": f"{stats['success_rate']:.1%}",
            "total_feedback": stats["total_feedback"],
            "top_interests": [kw for kw, _ in top_keywords],
            "preferences": self.preferences,
        }


# Global tracker instance
evolution = EvolutionTracker()
