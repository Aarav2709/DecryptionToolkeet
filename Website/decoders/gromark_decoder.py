from .base_decoder import BaseDecoder
import re


class GromarkDecoder(BaseDecoder):
    name = "gromark"
    description = "Decodes Gromark cipher (Gronsfeld variant) using numeric key patterns."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        if not clean_data:
            return 0.0
        
        confidence = 0.3
        
        # Gromark typically produces mixed case or all caps
        if re.match(r'^[A-Z]+$', clean_data):
            confidence += 0.2
        
        # Check character distribution
        char_counts = {}
        for char in clean_data:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Gromark tends to have more even distribution
        max_freq = max(char_counts.values()) if char_counts else 0
        min_freq = min(char_counts.values()) if char_counts else 0
        
        if max_freq > 0 and (max_freq - min_freq) / max_freq < 0.6:
            confidence += 0.3
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isalpha()).upper()
        
        if len(clean_data) < 4:
            return ["Input too short for Gromark cipher"]
        
        # Try common numeric keys
        common_keys = ['123', '1234', '12345', '987', '9876', '54321', '135', '246', '159']
        
        for key in common_keys:
            try:
                decoded = self._decode_gromark(clean_data, key)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Key '{key}': {decoded}")
            except:
                continue
        
        return results if results else ["No valid Gromark decoding found"]
    
    def _decode_gromark(self, text: str, key: str) -> str:
        # Convert key to numbers
        key_nums = [int(d) for d in key if d.isdigit()]
        if not key_nums:
            return ""
        
        result = []
        key_index = 0
        
        for char in text:
            if char.isalpha():
                # Get the key number for this position
                shift = key_nums[key_index % len(key_nums)]
                
                # Decode using Caesar shift
                if char.isupper():
                    decoded_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                else:
                    decoded_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                
                result.append(decoded_char)
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
