from .base_decoder import BaseDecoder
import re


class NihilistDecoder(BaseDecoder):
    name = "nihilist"
    description = "Decodes Nihilist cipher using Polybius square with numeric addition."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        # Nihilist cipher produces numbers
        clean_data = ''.join(c for c in data if c.isdigit() or c.isspace())
        numbers = clean_data.split()
        
        if not numbers:
            return 0.0
        
        confidence = 0.3
        
        # Check if numbers are in typical Nihilist range (20-99)
        valid_range = all(20 <= int(num) <= 99 for num in numbers if num.isdigit())
        
        if valid_range:
            confidence += 0.4
        
        # Check for reasonable number count
        if 3 <= len(numbers) <= 50:
            confidence += 0.2
        
        return min(0.9, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        
        # Extract numbers from input
        numbers = re.findall(r'\\b\\d{2}\\b', data)
        
        if len(numbers) < 3:
            return ["Need at least 3 two-digit numbers for Nihilist cipher"]
        
        # Try common keywords
        keywords = ['CIPHER', 'SECRET', 'HIDDEN', 'ENIGMA', 'RUSSIA', 'NIHILIST']
        
        for key in keywords:
            try:
                decoded = self._decode_nihilist(numbers, key)
                if decoded and self._looks_like_text(decoded):
                    results.append(f"Key '{key}': {decoded}")
            except:
                continue
        
        return results if results else ["No valid Nihilist decoding found"]
    
    def _decode_nihilist(self, numbers: list, key: str) -> str:
        # Create Polybius square with key
        square = self._create_polybius_square(key)
        
        # Create lookup table (char -> number)
        char_to_num = {}
        for i in range(5):
            for j in range(5):
                char = square[i][j]
                num = (i + 1) * 10 + (j + 1)
                char_to_num[char] = num
        
        # Create reverse lookup (number -> char)
        num_to_char = {v: k for k, v in char_to_num.items()}
        
        # Convert key to numbers
        key_numbers = []
        for char in key.upper().replace('J', 'I'):
            if char in char_to_num:
                key_numbers.append(char_to_num[char])
        
        if not key_numbers:
            return ""
        
        # Decode the message
        result = []
        for i, num_str in enumerate(numbers):
            cipher_num = int(num_str)
            key_num = key_numbers[i % len(key_numbers)]
            
            # Subtract key number from cipher number
            plain_num = cipher_num - key_num
            
            # Handle negative results and wrap around
            while plain_num < 11:
                plain_num += 44  # Add range of valid Polybius numbers
            
            if plain_num in num_to_char:
                result.append(num_to_char[plain_num])
        
        return ''.join(result)
    
    def _create_polybius_square(self, key: str) -> list:
        key = key.upper().replace('J', 'I')
        seen = set()
        key_chars = []
        
        # Add unique characters from key
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
