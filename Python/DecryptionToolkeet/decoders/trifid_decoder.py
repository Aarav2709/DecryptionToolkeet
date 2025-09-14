from .base_decoder import BaseDecoder
import re


class TrifidDecoder(BaseDecoder):
    name = "trifid"
    description = "Decodes Trifid cipher using 3x3x3 cube coordinates with periods."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 6:
            return 0.0
        
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        if not clean_data:
            return 0.0
        
        confidence = 0.3
        
        # Trifid works with all letters
        if re.match(r'^[A-Z]+$', clean_data):
            confidence += 0.3
        
        # Check for reasonable length
        if 6 <= len(clean_data) <= 100:
            confidence += 0.2
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        
        if len(clean_data) < 6:
            return ["Input too short for Trifid cipher"]
        
        # Try different period lengths
        for period in range(3, min(21, len(clean_data) // 2)):
            try:
                decoded = self._decode_trifid(clean_data, period)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Period {period}: {decoded}")
            except:
                continue
        
        return results if results else ["No valid Trifid decoding found"]
    
    def _decode_trifid(self, text: str, period: int) -> str:
        # Trifid square (3x3x3 = 27 positions for 26 letters + space)
        square = [
            [['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', 'I']],
            [['J', 'K', 'L'], ['M', 'N', 'O'], ['P', 'Q', 'R']],
            [['S', 'T', 'U'], ['V', 'W', 'X'], ['Y', 'Z', ' ']]
        ]
        
        # Create position lookup
        pos_lookup = {}
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    char = square[i][j][k]
                    if char != ' ':
                        pos_lookup[char] = (i+1, j+1, k+1)
        
        # Convert text to coordinates
        coords = []
        for char in text:
            if char in pos_lookup:
                coords.append(pos_lookup[char])
        
        if not coords:
            return ""
        
        # Group by period and rearrange
        result_chars = []
        for start in range(0, len(coords), period):
            group = coords[start:start + period]
            
            # Extract coordinates
            layer1 = [coord[0] for coord in group]
            layer2 = [coord[1] for coord in group]
            layer3 = [coord[2] for coord in group]
            
            # Combine coordinates
            combined = layer1 + layer2 + layer3
            
            # Convert back to characters
            for i in range(0, len(combined), 3):
                if i + 2 < len(combined):
                    x, y, z = combined[i], combined[i+1], combined[i+2]
                    if 1 <= x <= 3 and 1 <= y <= 3 and 1 <= z <= 3:
                        char = square[x-1][y-1][z-1]
                        if char != ' ':
                            result_chars.append(char)
        
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
