from .base_decoder import BaseDecoder
import re


class RailFenceDecoder(BaseDecoder):
    name = "railfence"
    description = "Decodes Rail Fence cipher with different rail counts (zigzag transposition)."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        # Rail fence typically has alphabetic characters
        if not re.match(r'^[A-Za-z\s]+$', data.strip()):
            return 0.2
        
        # Check for patterns that suggest rail fence
        char_positions = {}
        for i, char in enumerate(data):
            if char.isalpha():
                if char.upper() not in char_positions:
                    char_positions[char.upper()] = []
                char_positions[char.upper()].append(i)
        
        # Look for regular spacing patterns
        regular_patterns = 0
        for positions in char_positions.values():
            if len(positions) > 2:
                diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                if len(set(diffs)) <= 2:  # Regular pattern
                    regular_patterns += 1
        
        confidence = min(0.7, 0.3 + (regular_patterns * 0.1))
        return confidence
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        
        if len(clean_data) < 3:
            return ["Input too short for rail fence"]
        
        # Try different numbers of rails (2 to 8)
        for rails in range(2, min(9, len(clean_data))):
            try:
                decoded = self._decode_railfence(clean_data, rails)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Rails {rails}: {decoded}")
            except:
                continue
        
        return results if results else ["No valid rail fence decoding found"]
    
    def _decode_railfence(self, text: str, rails: int) -> str:
        if rails == 1:
            return text
        
        # Create rail pattern
        rail = [[] for _ in range(rails)]
        direction = 1
        row = 0
        
        # Mark positions
        for i in range(len(text)):
            rail[row].append(i)
            row += direction
            if row == rails - 1 or row == 0:
                direction *= -1
        
        # Read characters in rail order
        result = [''] * len(text)
        char_index = 0
        
        for r in range(rails):
            for pos in rail[r]:
                if char_index < len(text):
                    result[pos] = text[char_index]
                    char_index += 1
        
        return ''.join(result)
    
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
