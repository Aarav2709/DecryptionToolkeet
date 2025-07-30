from .base_decoder import BaseDecoder
import re


class TwoSquareDecoder(BaseDecoder):
    name = "twosquare"
    description = "Decodes Two Square cipher (Wheatstone) using horizontal 5x5 grids."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        if not clean_data or len(clean_data) % 2 != 0:
            return 0.1
        
        confidence = 0.4
        
        # Check for patterns typical of Two-square
        if re.match(r'^[A-Z]+$', clean_data):
            confidence += 0.2
        
        return min(0.7, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper().replace('J', 'I')
        
        if len(clean_data) % 2 != 0:
            return ["Input must be even length for Two-square"]
        
        keywords = ['EXAMPLE', 'KEYWORD', 'SECRET', 'CIPHER', 'ATTACK', 'DEFEND']
        
        for key1 in keywords:
            for key2 in keywords:
                if key1 != key2:
                    try:
                        decoded = self._decode_twosquare(clean_data, key1, key2)
                        if decoded and self._looks_like_text(decoded):
                            results.append(f"Keys '{key1}', '{key2}': {decoded}")
                    except:
                        continue
        
        return results if results else ["No valid Two-square decoding found"]
    
    def _decode_twosquare(self, text: str, key1: str, key2: str) -> str:
        square1 = self._create_keyed_square(key1)
        square2 = self._create_keyed_square(key2)
        
        # Create position lookups
        pos1 = {}
        pos2 = {}
        for i in range(5):
            for j in range(5):
                pos1[square1[i][j]] = (i, j)
                pos2[square2[i][j]] = (i, j)
        
        # Decode digrams
        result = []
        for i in range(0, len(text), 2):
            if i + 1 < len(text):
                char1, char2 = text[i], text[i+1]
                
                # Find positions in both squares
                if char1 in pos1 and char2 in pos2:
                    row1, col1 = pos1[char1]
                    row2, col2 = pos2[char2]
                    
                    # Decode using horizontal adjacency
                    new_col1 = (col1 - 1) % 5
                    new_col2 = (col2 - 1) % 5
                    
                    result.append(square1[row1][new_col1])
                    result.append(square2[row2][new_col2])
        
        return ''.join(result)
    
    def _create_keyed_square(self, key: str) -> list:
        key = key.upper().replace('J', 'I')
        seen = set()
        key_chars = []
        
        for char in key:
            if char.isalpha() and char not in seen:
                key_chars.append(char)
                seen.add(char)
        
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        for char in alphabet:
            if char not in seen:
                key_chars.append(char)
        
        return [key_chars[i:i+5] for i in range(0, 25, 5)]
    
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
