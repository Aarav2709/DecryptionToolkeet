from .base_decoder import BaseDecoder
import re


class BeaufortDecoder(BaseDecoder):
    name = "beaufort"
    description = "Decodes Beaufort cipher (reciprocal Vigenère variant) with keywords."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        if not clean_data:
            return 0.0
        
        confidence = 0.4
        
        # Beaufort produces alphabetic text
        if re.match(r'^[A-Z]+$', clean_data):
            confidence += 0.2
        
        # Check for patterns that might indicate Beaufort
        if len(clean_data) >= 10:
            confidence += 0.2
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        
        if len(clean_data) < 4:
            return ["Input too short for Beaufort cipher"]
        
        # Try common keywords
        keywords = ['CIPHER', 'SECRET', 'HIDDEN', 'ENIGMA', 'DECODE', 'CRYPTO', 'BEAUFORT']
        
        for key in keywords:
            try:
                decoded = self._decode_beaufort(clean_data, key)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Key '{key}': {decoded}")
            except:
                continue
        
        return results if results else ["No valid Beaufort decoding found"]
    
    def _decode_beaufort(self, text: str, key: str) -> str:
        key = key.upper()
        result = []
        key_index = 0
        
        for char in text:
            if char.isalpha():
                # Beaufort formula: plaintext = key - ciphertext (mod 26)
                key_char = key[key_index % len(key)]
                key_val = ord(key_char) - ord('A')
                cipher_val = ord(char) - ord('A')
                
                # Beaufort decryption
                plain_val = (key_val - cipher_val) % 26
                result.append(chr(plain_val + ord('A')))
                
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _looks_like_text(self, text: str) -> bool:
        if len(text) < 3:
            return False
        
        common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER']
        text_upper = text.upper()
        
        for word in common_words:
            if word in text_upper:
                return True
        
        vowels = sum(1 for c in text_upper if c in 'AEIOU')
        consonants = sum(1 for c in text_upper if c.isalpha() and c not in 'AEIOU')
        
        if consonants > 0:
            vowel_ratio = vowels / (vowels + consonants)
            return 0.2 <= vowel_ratio <= 0.6
        
        return False
