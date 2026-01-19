"""
Rhea Noir Smart Chunking - Semantic memory segmentation
Breaks content into coherent, searchable chunks
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """A semantic memory chunk"""
    content: str
    chunk_type: str  # 'text', 'code', 'header', 'list', 'paragraph'
    keywords: List[str]
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]


class SmartChunker:
    """
    Breaks content into semantically coherent chunks.
    Better for retrieval than raw full messages.
    """
    
    # Target chunk size (characters)
    MIN_CHUNK_SIZE = 100
    MAX_CHUNK_SIZE = 1000
    OVERLAP_SIZE = 50  # Overlap between chunks for context
    
    def __init__(self):
        pass
    
    def chunk(self, content: str) -> List[Chunk]:
        """
        Break content into smart chunks.
        
        Strategies:
        1. Code blocks → separate chunks
        2. Headers → start new chunks
        3. Paragraphs → natural boundaries
        4. Lists → keep together
        5. Sentences → fallback splitting
        """
        if not content or len(content) < self.MIN_CHUNK_SIZE:
            return [self._create_chunk(content, "text", 0, len(content))]
        
        chunks = []
        
        # Extract code blocks first (they're special)
        code_pattern = r'```[\w]*\n?(.*?)```'
        code_matches = list(re.finditer(code_pattern, content, re.DOTALL))
        
        # Track positions we've chunked
        pos = 0
        
        for match in code_matches:
            # Chunk text before code block
            if match.start() > pos:
                text_before = content[pos:match.start()]
                chunks.extend(self._chunk_text(text_before, pos))
            
            # Code block as its own chunk
            code_content = match.group(1).strip()
            if code_content:
                chunks.append(self._create_chunk(
                    code_content, 
                    "code", 
                    match.start(), 
                    match.end()
                ))
            
            pos = match.end()
        
        # Chunk remaining text after last code block
        if pos < len(content):
            remaining = content[pos:]
            chunks.extend(self._chunk_text(remaining, pos))
        
        return chunks
    
    def _chunk_text(self, text: str, base_pos: int) -> List[Chunk]:
        """Chunk regular text content"""
        chunks = []
        
        # Split by headers first
        header_pattern = r'^(#{1,6}\s+.+)$'
        sections = re.split(header_pattern, text, flags=re.MULTILINE)
        
        current_pos = base_pos
        for section in sections:
            if not section.strip():
                continue
            
            # Check if this is a header
            if re.match(r'^#{1,6}\s+', section):
                chunks.append(self._create_chunk(
                    section.strip(),
                    "header",
                    current_pos,
                    current_pos + len(section)
                ))
            else:
                # Split by paragraphs
                paragraphs = re.split(r'\n\s*\n', section)
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    
                    # Check if it's a list
                    if re.match(r'^[\-\*\d+\.]\s', para):
                        chunks.append(self._create_chunk(
                            para, "list", current_pos, current_pos + len(para)
                        ))
                    elif len(para) > self.MAX_CHUNK_SIZE:
                        # Split long paragraphs by sentences
                        chunks.extend(self._split_by_sentences(para, current_pos))
                    else:
                        chunks.append(self._create_chunk(
                            para, "paragraph", current_pos, current_pos + len(para)
                        ))
                    
                    current_pos += len(para) + 2  # Account for paragraph break
            
            current_pos += len(section)
        
        return chunks
    
    def _split_by_sentences(self, text: str, base_pos: int) -> List[Chunk]:
        """Split long text by sentences"""
        chunks = []
        
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunk_start = base_pos
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.MAX_CHUNK_SIZE:
                # Save current chunk
                if current_chunk:
                    chunks.append(self._create_chunk(
                        current_chunk.strip(),
                        "text",
                        chunk_start,
                        chunk_start + len(current_chunk)
                    ))
                current_chunk = sentence
                chunk_start = base_pos + len(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk.strip(),
                "text",
                chunk_start,
                chunk_start + len(current_chunk)
            ))
        
        return chunks
    
    def _create_chunk(
        self, 
        content: str, 
        chunk_type: str, 
        start: int, 
        end: int
    ) -> Chunk:
        """Create a chunk with extracted keywords"""
        keywords = self._extract_keywords(content)
        
        return Chunk(
            content=content,
            chunk_type=chunk_type,
            keywords=keywords,
            start_pos=start,
            end_pos=end,
            metadata={"type": chunk_type}
        )
    
    def _extract_keywords(self, content: str, max_keywords: int = 5) -> List[str]:
        """Quick keyword extraction for a chunk"""
        # Simple extraction - get significant words
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]{2,}\b', content.lower())
        
        # Filter common words
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
                    'can', 'her', 'was', 'one', 'our', 'out', 'has', 'have',
                    'this', 'that', 'with', 'from', 'they', 'will', 'would',
                    'there', 'their', 'what', 'about', 'which', 'when', 'been'}
        
        filtered = [w for w in words if w not in stopwords]
        
        # Get most common
        from collections import Counter
        counts = Counter(filtered)
        return [w for w, _ in counts.most_common(max_keywords)]
    
    def chunk_conversation(
        self, 
        messages: List[Dict[str, str]]
    ) -> List[Chunk]:
        """Chunk a conversation into retrievable pieces"""
        all_chunks = []
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            msg_chunks = self.chunk(content)
            
            # Add role to metadata
            for chunk in msg_chunks:
                chunk.metadata["role"] = role
                chunk.metadata["message_index"] = i
            
            all_chunks.extend(msg_chunks)
        
        return all_chunks


# Global chunker instance
chunker = SmartChunker()
