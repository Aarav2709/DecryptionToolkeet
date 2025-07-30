from .base_decoder import BaseDecoder
import re


class FourSquareDecoder(BaseDecoder):
    name = "foursquare"
    description = "Decodes Four Square cipher using two 5x5 key grids with digrams."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        if not clean_data or len(clean_data) % 2 != 0:
            return 0.1
        
        # Four-square typically has even length pairs
        confidence = 0.4
        
        # Check for no doubled letters (rare in Four-square)
        has_doubles = any(clean_data[i] == clean_data[i+1] for i in range(0, len(clean_data)-1, 2))
        if not has_doubles:
            confidence += 0.2
        
        return min(0.7, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper().replace('J', 'I')
        
        if len(clean_data) % 2 != 0:
            return ["Input must be even length for Four-square"]
        
        # Try common keyword combinations
        keywords = ['EXAMPLE', 'KEYWORD', 'SECRET', 'CIPHER', 'ATTACK']
        
        for key1 in keywords:
            for key2 in keywords:
                if key1 != key2:
                    try:
                        decoded = self._decode_foursquare(clean_data, key1, key2)
                        if decoded and self._looks_like_text(decoded):
                            results.append(f"Keys '{key1}', '{key2}': {decoded}")
                    except:
                        continue
        
        return results if results else ["No valid Four-square decoding found"]
    
    def _decode_foursquare(self, text: str, key1: str, key2: str) -> str:
        # Create the four squares
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # No J
        
        # Upper left and lower right are plain alphabet
        square1 = [list(alphabet[i:i+5]) for i in range(0, 25, 5)]
        square4 = [list(alphabet[i:i+5]) for i in range(0, 25, 5)]
        
        # Upper right and lower left use keywords
        square2 = self._create_keyed_square(key1)
        square3 = self._create_keyed_square(key2)
        
        # Create position lookup for plain squares
        pos1 = {}
        for i in range(5):
            for j in range(5):
                pos1[square1[i][j]] = (i, j)
        
        # Decode digrams
        result = []
        for i in range(0, len(text), 2):
            if i + 1 < len(text):
                char1, char2 = text[i], text[i+1]
                if char1 in pos1 and char2 in pos1:
                    row1, col1 = pos1[char1]
                    row2, col2 = pos1[char2]
                    
                    # Use keyed squares for decoding
                    result.append(square2[row1][col2])
                    result.append(square3[row2][col1])
        
        return ''.join(result)
    
    def _create_keyed_square(self, key: str) -> list:
        key = key.upper().replace('J', 'I')
        seen = set()
        key_chars = []
        
        # Add unique characters from key
        for char in key:
            if char.isalpha() and char not in seen:
                key_chars.append(char)
                seen.add(char)
        
        # Add remaining alphabet
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        for char in alphabet:
            if char not in seen:
                key_chars.append(char)
        
        # Create 5x5 square
        return [key_chars[i:i+5] for i in range(0, 25, 5)]
    
    def _looks_like_text(self, text: str) -> bool:
        if len(text) < 3:
            return False
        
        common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE']
        text_upper = text.upper()
        
        for word in common_words:
            if word in text_upper:
                return True
        
        # Check vowel ratio
        vowels = sum(1 for c in text_upper if c in 'AEIOU')
        consonants = sum(1 for c in text_upper if c.isalpha() and c not in 'AEIOU')
        
        if consonants > 0:
            vowel_ratio = vowels / (vowels + consonants)
            return 0.2 <= vowel_ratio <= 0.6
        
        return False
