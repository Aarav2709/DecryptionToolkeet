"""
Vigenère cipher decoding module with dictionary brute force.
"""

import string
from typing import Union, List
from .base_decoder import BaseDecoder


class VigenereDecoder(BaseDecoder):
    """Decoder for Vigenère cipher with key guessing."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Vigenère cipher (tries common keys)."
        self.common_keys = [
            'KEY', 'SECRET', 'PASSWORD', 'CIPHER', 'CODE', 'CRYPTO',
            'ENCRYPT', 'DECODE', 'HIDDEN', 'MESSAGE', 'TEXT', 'DATA',
            'WORD', 'LETTER', 'ALPHABET', 'SECURITY', 'PRIVATE',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'
        ]
    
    def can_decode(self, data: str) -> float:
        """Check if data could be Vigenère cipher."""
        if not data:
            return 0.0
        
        # Should contain mostly letters
        letters = sum(1 for c in data if c.isalpha())
        if letters / len(data) < 0.5:
            return 0.0
        
        # Try some common keys and see if any result looks like English
        for key in self.common_keys[:5]:  # Quick check with first 5 keys
            decoded = self._vigenere_decode(data, key)
            if self._looks_like_english(decoded):
                return 0.9
        
        return 0.2  # Could still be Vigenère
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Vigenère cipher by trying common keys."""
        results = []
        
        for key in self.common_keys:
            try:
                decoded = self._vigenere_decode(data, key)
                if self._looks_like_english(decoded):
                    results.append(f"Key '{key}': {decoded}")
            except:
                continue
        
        if not results:
            # If no good results, try a few keys anyway
            for key in self.common_keys[:10]:
                try:
                    decoded = self._vigenere_decode(data, key)
                    results.append(f"Key '{key}': {decoded}")
                except:
                    continue
        
        return results if results else ["No valid decryption found with common keys"]
    
    def _vigenere_decode(self, text: str, key: str) -> str:
        """Decode text using Vigenère cipher with given key."""
        if not key:
            return text
        
        key = key.upper()
        result = ""
        key_index = 0
        
        for char in text:
            if char.isalpha():
                # Get the key character for this position
                key_char = key[key_index % len(key)]
                key_shift = ord(key_char) - ord('A')
                
                # Determine if uppercase or lowercase
                if char.isupper():
                    shifted = (ord(char) - ord('A') - key_shift) % 26
                    result += chr(ord('A') + shifted)
                else:
                    shifted = (ord(char) - ord('a') - key_shift) % 26
                    result += chr(ord('a') + shifted)
                
                key_index += 1
            else:
                result += char
        
        return result
    
    def _looks_like_english(self, text: str) -> bool:
        """Simple heuristic to check if text looks like English."""
        # Common English words
        common_words = ['the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they', 'have', 'this']
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
    
    def encode(self, data: str, key: str = "KEY") -> str:
        """Encode string with Vigenère cipher."""
        if not key:
            return data
        
        key = key.upper()
        result = ""
        key_index = 0
        
        for char in data:
            if char.isalpha():
                # Get the key character for this position
                key_char = key[key_index % len(key)]
                key_shift = ord(key_char) - ord('A')
                
                # Determine if uppercase or lowercase
                if char.isupper():
                    shifted = (ord(char) - ord('A') + key_shift) % 26
                    result += chr(ord('A') + shifted)
                else:
                    shifted = (ord(char) - ord('a') + key_shift) % 26
                    result += chr(ord('a') + shifted)
                
                key_index += 1
            else:
                result += char
        
        return result
