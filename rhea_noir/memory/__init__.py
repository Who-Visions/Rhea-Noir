"""
Rhea Noir Memory System
SQLite (short-term) + BigQuery (long-term) with lazy sync
"""

from .short_term import ShortTermMemory
try:
    from .long_term import BigQueryMemory
except ImportError:
    BigQueryMemory = None
from .keywords import KeywordExtractor
from .sync import MemorySync
from .chunker import SmartChunker

# Import expressions for emoji data
from ..expressions import (
    RheaExpressions,
    RHEA_IDENTITY,
    get_expression,
    get_hand,
    get_reaction,
    get_signature,
    get_identity,
    get_all_for_memory,
)

__all__ = [
    "ShortTermMemory",
    "LongTermMemory",
    "KeywordExtractor",
    "MemorySync",
    "SmartChunker",
    "RheaExpressions",
    "RHEA_IDENTITY",
    "get_expression",
    "get_hand",
    "get_reaction",
    "get_signature",
    "get_identity",
    "get_all_for_memory",
]
