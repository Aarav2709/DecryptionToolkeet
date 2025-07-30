"""
Affine cipher decoding module.
"""

import math
from typing import Union, List
from .base_decoder import BaseDecoder


class AffineDecoder(BaseDecoder):
    """Decoder for Affine cipher with brute force."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Affine cipher (brute force a,b parameters)."
        
        # Valid 'a' values (must be coprime with 26)
        self.valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    
    def can_decode(self, data: str) -> float:
        """Check if data could be Affine cipher."""
        if not data:
            return 0.0
        
        # Should contain mostly letters
        letters = sum(1 for c in data if c.isalpha())
        if letters / len(data) < 0.5:
            return 0.0
        
        # Try a few common Affine parameters
        for a in [3, 5, 7]:
            for b in [1, 2, 3]:
                decoded = self._affine_decode(data, a, b)
                if self._looks_like_english(decoded):
                    return 0.9
        
        return 0.3  # Could still be Affine
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Affine cipher by trying all valid parameters."""
        results = []
        
        for a in self.valid_a:
            for b in range(26):
                try:
                    decoded = self._affine_decode(data, a, b)
                    if self._looks_like_english(decoded):
                        results.append(f"a={a}, b={b}: {decoded}")
                except:
                    continue
        
        if not results:
            # If no good results, show a few attempts anyway
            for a in self.valid_a[:3]:
                for b in range(0, 26, 5):
                    try:
                        decoded = self._affine_decode(data, a, b)
                        results.append(f"a={a}, b={b}: {decoded}")
                    except:
                        continue
                    if len(results) >= 5:
                        break
                if len(results) >= 5:
                    break
        
        return results if results else ["No valid Affine decryption found"]
    
    def _affine_decode(self, text: str, a: int, b: int) -> str:
        """Decode text using Affine cipher with parameters a and b."""
        # Find modular inverse of a
        a_inv = self._mod_inverse(a, 26)
        if a_inv is None:
            raise ValueError(f"No modular inverse for a={a}")
        
        result = ""
        for char in text:
            if char.isalpha():
                # Determine if uppercase or lowercase
                is_upper = char.isupper()
                char = char.upper()
                
                # Apply inverse affine transformation: x = a^(-1) * (y - b) mod 26
                y = ord(char) - ord('A')
                x = (a_inv * (y - b)) % 26
                
                decoded_char = chr(x + ord('A'))
                result += decoded_char if is_upper else decoded_char.lower()
            else:
                result += char
        
        return result
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """Find modular inverse of a modulo m using extended Euclidean algorithm."""
        if math.gcd(a, m) != 1:
            return None  # No inverse exists
        
        # Extended Euclidean Algorithm
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        _, x, _ = extended_gcd(a, m)
        return (x % m + m) % m
    
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
    
    def encode(self, data: str, a: int = 5, b: int = 8) -> str:
        """Encode string with Affine cipher."""
        if a not in self.valid_a:
            raise ValueError(f"Invalid 'a' value: {a}. Must be coprime with 26.")
        
        result = ""
        for char in data:
            if char.isalpha():
                is_upper = char.isupper()
                char = char.upper()
                
                # Apply affine transformation: y = (a * x + b) mod 26
                x = ord(char) - ord('A')
                y = (a * x + b) % 26
                
                encoded_char = chr(y + ord('A'))
                result += encoded_char if is_upper else encoded_char.lower()
            else:
                result += char
        
        return result
