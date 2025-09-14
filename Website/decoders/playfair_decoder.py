from .base_decoder import BaseDecoder
import re


class PlayfairDecoder(BaseDecoder):
    name = "playfair"
    description = "Decodes Playfair cipher using 5x5 grid with common keywords."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 6:
            return 0.0
        
        # Remove spaces and check if it's alphabetic
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        
        if not clean_data:
            return 0.0
        
        # Playfair typically has even length (digrams)
        if len(clean_data) % 2 != 0:
            return 0.2
        
        # Check for patterns typical of Playfair
        confidence = 0.4
        
        # Look for repeated digrams (less common in Playfair)
        digrams = [clean_data[i:i+2] for i in range(0, len(clean_data), 2)]
        unique_digrams = len(set(digrams))
        
        if unique_digrams / len(digrams) > 0.8:  # Many unique digrams
            confidence += 0.2
        
        # Check for absence of double letters (Playfair splits them)
        has_doubles = any(clean_data[i] == clean_data[i+1] for i in range(0, len(clean_data)-1, 2))
        if not has_doubles:
            confidence += 0.2
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper().replace('J', 'I')
        
        if len(clean_data) < 6 or len(clean_data) % 2 != 0:
            return ["Input must be even length for Playfair"]
        
        # Try common keys
        common_keys = ['MONARCHY', 'KEYWORD', 'PLAYFAIR', 'CIPHER', 'SECRET', 'HIDDEN', 'CODE']
        
        for key in common_keys:
            try:
                decoded = self._decode_playfair(clean_data, key)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Key '{key}': {decoded}")
            except:
                continue
        
        return results if results else ["No valid Playfair decoding found"]
    
    def _decode_playfair(self, text: str, key: str) -> str:
        # Create Playfair square
        square = self._create_playfair_square(key)
        
        # Create position lookup
        pos = {}
        for i in range(5):
            for j in range(5):
                pos[square[i][j]] = (i, j)
        
        # Decode digrams
        result = []
        for i in range(0, len(text), 2):
            if i + 1 < len(text):
                char1, char2 = text[i], text[i+1]
                if char1 in pos and char2 in pos:
                    row1, col1 = pos[char1]
                    row2, col2 = pos[char2]
                    
                    if row1 == row2:  # Same row
                        new_col1 = (col1 - 1) % 5
                        new_col2 = (col2 - 1) % 5
                        result.append(square[row1][new_col1])
                        result.append(square[row2][new_col2])
                    elif col1 == col2:  # Same column
                        new_row1 = (row1 - 1) % 5
                        new_row2 = (row2 - 1) % 5
                        result.append(square[new_row1][col1])
                        result.append(square[new_row2][col2])
                    else:  # Rectangle
                        result.append(square[row1][col2])
                        result.append(square[row2][col1])
        
        decoded = ''.join(result)
        # Remove padding X's at the end
        return decoded.rstrip('X')
    
    def _create_playfair_square(self, key: str) -> list:
        # Remove duplicates and J from key
        key = key.upper().replace('J', 'I')
        seen = set()
        key_chars = []
        for char in key:
            if char.isalpha() and char not in seen:
                key_chars.append(char)
                seen.add(char)
        
        # Add remaining alphabet
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # No J
        for char in alphabet:
            if char not in seen:
                key_chars.append(char)
        
        # Create 5x5 square
        square = []
        for i in range(5):
            row = []
            for j in range(5):
                row.append(key_chars[i * 5 + j])
            square.append(row)
        
        return square
    
    def _looks_like_text(self, text: str) -> bool:
        if len(text) < 3:
            return False
        
        # Check for common English patterns
        common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'DAY']
        text_upper = text.upper()
        
        for word in common_words:
            if word in text_upper:
                return True
        
        # Check for reasonable letter frequency
        vowels = sum(1 for c in text_upper if c in 'AEIOU')
        consonants = sum(1 for c in text_upper if c.isalpha() and c not in 'AEIOU')
        
        if consonants > 0:
            vowel_ratio = vowels / (vowels + consonants)
            return 0.2 <= vowel_ratio <= 0.6
        
        return False
