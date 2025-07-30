from .base_decoder import BaseDecoder
import re


class ColumnarDecoder(BaseDecoder):
    name = "columnar"
    description = "Decodes Columnar Transposition cipher with common key patterns."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 6:
            return 0.0
        
        # Columnar typically has alphabetic characters
        if not re.match(r'^[A-Za-z\s]+$', data.strip()):
            return 0.2
        
        # Check if length suggests columnar (divisible by common key lengths)
        clean_data = ''.join(c for c in data if c.isalpha())
        length = len(clean_data)
        
        confidence = 0.3
        
        # Common key lengths
        for key_len in [3, 4, 5, 6, 7, 8]:
            if length % key_len == 0:
                confidence += 0.1
                break
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        
        if len(clean_data) < 6:
            return ["Input too short for columnar transposition"]
        
        # Try different key lengths
        for key_length in range(3, min(9, len(clean_data) // 2)):
            if len(clean_data) % key_length == 0:
                try:
                    # Try different key permutations for common keys
                    common_keys = self._generate_common_keys(key_length)
                    
                    for key in common_keys:
                        decoded = self._decode_columnar(clean_data, key)
                        if decoded and self._looks_like_text(decoded):
                            key_str = ''.join(str(x) for x in key)
                            results.append(f"Key {key_str}: {decoded}")
                except:
                    continue
        
        return results if results else ["No valid columnar decoding found"]
    
    def _generate_common_keys(self, length: int) -> list:
        """Generate common key patterns for given length."""
        keys = []
        
        if length == 3:
            keys = [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
        elif length == 4:
            keys = [[1,2,3,4], [4,3,2,1], [1,3,2,4], [2,4,1,3], [3,1,4,2]]
        elif length == 5:
            keys = [[1,2,3,4,5], [5,4,3,2,1], [1,3,5,2,4], [2,4,1,5,3]]
        else:
            # Generate a few basic patterns
            keys = [list(range(1, length + 1))]  # Sequential
            keys.append(list(range(length, 0, -1)))  # Reverse
            
            # Alternating pattern
            if length % 2 == 0:
                alt = []
                for i in range(length // 2):
                    alt.extend([i + 1, length - i])
                keys.append(alt)
        
        return keys[:10]  # Limit to first 10 patterns
    
    def _decode_columnar(self, text: str, key: list) -> str:
        key_length = len(key)
        rows = len(text) // key_length
        
        if rows * key_length != len(text):
            return ""
        
        # Create matrix
        matrix = []
        for i in range(rows):
            row = []
            for j in range(key_length):
                row.append(text[i * key_length + j])
            matrix.append(row)
        
        # Rearrange columns according to key
        sorted_indices = sorted(range(key_length), key=lambda x: key[x])
        
        result = []
        for i in range(rows):
            for j in sorted_indices:
                result.append(matrix[i][j])
        
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
