"""
Atbash cipher decoding module.
"""

import string
from typing import Union, List
from .base_decoder import BaseDecoder


class AtbashDecoder(BaseDecoder):
    """Decoder for Atbash cipher."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Atbash cipher (A=Z, B=Y, etc.)."
    
    def can_decode(self, data: str) -> float:
        """Check if data could be Atbash."""
        if not data:
            return 0.0
        
        # Should contain mostly letters
        letters = sum(1 for c in data if c.isalpha())
        if letters / len(data) < 0.5:
            return 0.0
        
        # If it contains non-letter characters like numbers, = signs, etc.
        # it's less likely to be a simple cipher like Atbash
        non_letters = sum(1 for c in data if not c.isalpha() and not c.isspace())
        if non_letters > 0:
            # Reduce confidence significantly for mixed content
            base_confidence = 0.3
        else:
            base_confidence = 0.5
        
        # Try Atbash and see if result looks more like English
        decoded = self._atbash(data)
        if self._looks_like_english(decoded):
            return min(base_confidence + 0.4, 1.0)
        
        return base_confidence
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Atbash cipher."""
        return self._atbash(data)
    
    def _atbash(self, text: str) -> str:
        """Apply Atbash transformation."""
        result = ""
        for char in text:
            if char.isalpha():
                if char.isupper():
                    # A=Z, B=Y, C=X, etc.
                    result += chr(ord('Z') - (ord(char) - ord('A')))
                else:
                    # a=z, b=y, c=x, etc.
                    result += chr(ord('z') - (ord(char) - ord('a')))
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
        """Encode string with Atbash (same as decode since Atbash is symmetric)."""
        return self._atbash(data)
