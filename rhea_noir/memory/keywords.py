"""
Keyword Extractor - Extract and evolve keywords from conversations
"""

import re
from typing import List, Set
from collections import Counter


class KeywordExtractor:
    """Extract meaningful keywords from text for memory indexing"""

    # Common stop words to filter out
    STOP_WORDS: Set[str] = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
        "your", "yours", "yourself", "yourselves", "he", "him", "his",
        "himself", "she", "her", "hers", "herself", "it", "its", "itself",
        "they", "them", "their", "theirs", "themselves", "what", "which",
        "who", "whom", "this", "that", "these", "those", "am", "been",
        "being", "having", "doing", "just", "now", "here", "there", "when",
        "where", "why", "how", "all", "each", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "also", "then", "once", "both",
        "into", "through", "during", "before", "after", "above", "below",
        "up", "down", "out", "off", "over", "under", "again", "further",
        "about", "if", "because", "until", "while", "any", "between",
    }

    # Tech keywords to prioritize
    TECH_KEYWORDS: Set[str] = {
        "python", "javascript", "typescript", "java", "golang", "rust",
        "api", "database", "sql", "nosql", "mongodb", "postgresql", "mysql",
        "react", "vue", "angular", "node", "django", "flask", "fastapi",
        "docker", "kubernetes", "aws", "gcp", "azure", "cloud",
        "git", "github", "gitlab", "cicd", "devops", "terraform",
        "machine learning", "ml", "ai", "neural", "model", "training",
        "frontend", "backend", "fullstack", "microservices", "serverless",
        "authentication", "oauth", "jwt", "security", "encryption",
        "testing", "unit test", "integration", "debugging", "error",
        "performance", "optimization", "caching", "redis", "memory",
        "bigquery", "vertex", "gemini", "agent", "reasoning",
    }

    def __init__(self):
        """Initialize keyword extractor"""
        self.keyword_history: Counter = Counter()

    def extract(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []

        # Normalize text
        text_lower = text.lower()

        # Extract words (including compound words with hyphens/underscores)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]\b|\b[a-zA-Z]\b', text_lower)

        # Filter and score words
        scored_words: Counter = Counter()

        for word in words:
            # Skip stop words
            if word in self.STOP_WORDS:
                continue

            # Skip very short words (except known tech terms)
            if len(word) < 3 and word not in self.TECH_KEYWORDS:
                continue

            # Score the word
            score = 1

            # Boost tech keywords
            if word in self.TECH_KEYWORDS:
                score += 2

            # Boost longer words (likely more meaningful)
            if len(word) > 6:
                score += 1

            scored_words[word] += score

        # Get top keywords
        top_keywords = [kw for kw, _ in scored_words.most_common(max_keywords)]

        # Update history
        self.keyword_history.update(top_keywords)

        return top_keywords

    def extract_phrases(self, text: str, max_phrases: int = 5) -> List[str]:
        """Extract multi-word phrases (bigrams)"""
        if not text:
            return []

        words = text.lower().split()
        phrases = []

        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]

            # Skip if either is a stop word
            if w1 in self.STOP_WORDS or w2 in self.STOP_WORDS:
                continue

            phrase = f"{w1} {w2}"

            # Prioritize known tech phrases
            if phrase in self.TECH_KEYWORDS:
                phrases.insert(0, phrase)
            else:
                phrases.append(phrase)

        return phrases[:max_phrases]

    def get_top_keywords(self, n: int = 20) -> List[tuple]:
        """Get most common keywords from history"""
        return self.keyword_history.most_common(n)

    def get_related(self, keyword: str, text_corpus: List[str]) -> List[str]:
        """Find keywords that often appear with the given keyword"""
        related: Counter = Counter()

        for text in text_corpus:
            if keyword.lower() in text.lower():
                # Extract other keywords from this text
                other_keywords = self.extract(text)
                for kw in other_keywords:
                    if kw != keyword.lower():
                        related[kw] += 1

        return [kw for kw, _ in related.most_common(10)]
