from .base_decoder import BaseDecoder
import re


class BifidDecoder(BaseDecoder):
    name = "bifid"
    description = "Decodes Bifid cipher using 5x5 grid coordinates with periods."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        if not clean_data:
            return 0.0
        
        confidence = 0.4
        
        # Bifid works with alphabetic characters
        if re.match(r'^[A-Z]+$', clean_data):
            confidence += 0.3
        
        # Check for reasonable length
        if 4 <= len(clean_data) <= 100:
            confidence += 0.2
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper().replace('J', 'I')
        
        if len(clean_data) < 4:
            return ["Input too short for Bifid cipher"]
        
        # Try different period lengths
        for period in range(3, min(16, len(clean_data))):
            try:
                decoded = self._decode_bifid(clean_data, period)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Period {period}: {decoded}")
            except:
                continue
        
        return results if results else ["No valid Bifid decoding found"]
    
    def _decode_bifid(self, text: str, period: int) -> str:
        # Standard Polybius square
        square = [
            ['A', 'B', 'C', 'D', 'E'],
            ['F', 'G', 'H', 'I', 'K'],
            ['L', 'M', 'N', 'O', 'P'],
            ['Q', 'R', 'S', 'T', 'U'],
            ['V', 'W', 'X', 'Y', 'Z']
        ]
        
        # Create position lookup
        pos_lookup = {}
        for i in range(5):
            for j in range(5):
                pos_lookup[square[i][j]] = (i+1, j+1)
        
        # Convert text to coordinates
        coords = []
        for char in text:
            if char in pos_lookup:
                coords.append(pos_lookup[char])
        
        # Group by period and rearrange
        result_chars = []
        for start in range(0, len(coords), period):
            group = coords[start:start + period]
            
            # Extract row and column coordinates
            rows = [coord[0] for coord in group]
            cols = [coord[1] for coord in group]
            
            # Combine: all rows first, then all columns
            combined = rows + cols
            
            # Convert back to characters using pairs
            for i in range(0, len(combined), 2):
                if i + 1 < len(combined):
                    row, col = combined[i], combined[i+1]
                    if 1 <= row <= 5 and 1 <= col <= 5:
                        result_chars.append(square[row-1][col-1])
        
        return ''.join(result_chars)
    
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
