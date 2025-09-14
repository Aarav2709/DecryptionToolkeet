"""
ROT13 cipher decoding module.
"""

import string
from typing import Union, List
from .base_decoder import BaseDecoder


class ROT13Decoder(BaseDecoder):
    """Decoder for ROT13 cipher."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes ROT13 cipher."
    
    def can_decode(self, data: str) -> float:
        """Check if data could be ROT13."""
        if not data:
            return 0.0
        
        # Should contain mostly letters
        letters = sum(1 for c in data if c.isalpha())
        if letters / len(data) < 0.5:
            return 0.0
        
        # Try ROT13 and see if result looks more like English
        decoded = self._rot13(data)
        if self._looks_like_english(decoded):
            return 0.9
        
        return 0.3  # Could still be ROT13
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode ROT13 cipher."""
        return self._rot13(data)
    
    def _rot13(self, text: str) -> str:
        """Apply ROT13 transformation."""
        result = ""
        for char in text:
            if char.isalpha():
                # Determine if uppercase or lowercase
                start = ord('A') if char.isupper() else ord('a')
                # ROT13 is shift by 13
                shifted = (ord(char) - start + 13) % 26
                result += chr(start + shifted)
            else:
                result += char
        return result
    
    def _looks_like_english(self, text: str) -> bool:
        """Simple heuristic to check if text looks like English."""
        # Common English words
        common_words = ['the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they']
        text_lower = text.lower()
        
        # Check for common words
        word_count = sum(1 for word in common_words if word in text_lower)
        if word_count >= 2:
            return True
        
        # Check for reasonable letter frequency
        if len(text) > 10:
            e_count = text_lower.count('e')
            if e_count / len(text) > 0.08:
                return True
        
        return False
    
    def encode(self, data: str) -> str:
        """Encode string with ROT13 (same as decode since ROT13 is symmetric)."""
        return self._rot13(data)
