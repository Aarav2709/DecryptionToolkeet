"""
Caesar cipher decoding module with brute force capability.
"""

import string
from typing import Union, List
from .base_decoder import BaseDecoder


class CaesarDecoder(BaseDecoder):
    """Decoder for Caesar cipher with brute force support."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Caesar cipher (brute force all shifts)."
    
    def can_decode(self, data: str) -> float:
        """Check if data could be Caesar cipher."""
        if not data:
            return 0.0
        
        # Should contain mostly letters
        letters = sum(1 for c in data if c.isalpha())
        if letters / len(data) < 0.5:
            return 0.0
        
        # Caesar cipher is always possible for text with letters
        return 0.5
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Caesar cipher by trying all possible shifts."""
        results = []
        
        for shift in range(1, 26):  # Try shifts 1-25
            decoded = self._caesar_shift(data, shift)
            if self._looks_like_english(decoded):
                results.append(f"Shift {shift}: {decoded}")
        
        if not results:
            # If no results look like English, return all possibilities
            for shift in range(1, 26):
                decoded = self._caesar_shift(data, shift)
                results.append(f"Shift {shift}: {decoded}")
        
        return results
    
    def _caesar_shift(self, text: str, shift: int) -> str:
        """Apply Caesar cipher shift to text."""
        result = ""
        for char in text:
            if char.isalpha():
                # Determine if uppercase or lowercase
                start = ord('A') if char.isupper() else ord('a')
                # Shift character
                shifted = (ord(char) - start - shift) % 26
                result += chr(start + shifted)
            else:
                result += char
        return result
    
    def _looks_like_english(self, text: str) -> bool:
        """Simple heuristic to check if text looks like English."""
        # Common English words and patterns
        common_words = ['the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they', 
                       'hello', 'world', 'this', 'have', 'from', 'they', 'know', 'want', 'been',
                       'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'your']
        text_lower = text.lower()
        
        # Check for common words
        word_count = sum(1 for word in common_words if word in text_lower)
        if word_count >= 1:  # Lower threshold
            return True
        
        # Check for reasonable letter frequency (e is most common)
        if len(text) > 5:  # Lower length requirement
            e_count = text_lower.count('e')
            if e_count / len(text) > 0.08:
                return True
        
        # Check for common letter combinations
        common_bigrams = ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'on', 'en', 'at', 'ou', 'it', 'is', 'or', 'ti', 'hi', 'st', 'ar', 'ng']
        bigram_count = sum(1 for bigram in common_bigrams if bigram in text_lower)
        if bigram_count >= 2:
            return True
        
        return False
    
    def encode(self, data: str, shift: int = 3) -> str:
        """Encode string with Caesar cipher."""
        result = ""
        for char in data:
            if char.isalpha():
                start = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - start + shift) % 26
                result += chr(start + shifted)
            else:
                result += char
        return result
