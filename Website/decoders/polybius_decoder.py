from .base_decoder import BaseDecoder
import re


class PolybusDecoder(BaseDecoder):
    name = "polybius"
    description = "Decodes Polybius Square cipher (5x5 grid using coordinate pairs)."
    
    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0
        
        # Remove spaces and check if it's all digits
        clean_data = ''.join(c for c in data if c.isdigit())
        
        if not clean_data:
            return 0.0
        
        # Must be even length for Polybius (pairs of digits)
        if len(clean_data) % 2 != 0:
            return 0.2
        
        # Check if all digits are valid Polybius coordinates (1-5)
        valid_digits = all(d in '12345' for d in clean_data)
        
        if not valid_digits:
            return 0.1
        
        # High confidence if looks like Polybius
        confidence = 0.8
        
        # Check for patterns
        pairs = [clean_data[i:i+2] for i in range(0, len(clean_data), 2)]
        unique_pairs = len(set(pairs))
        
        # Good variety of pairs suggests real encoding
        if unique_pairs / len(pairs) > 0.6:
            confidence += 0.1
        
        return min(0.9, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isdigit())
        
        if len(clean_data) % 2 != 0:
            return ["Input must be even length for Polybius Square"]
        
        # Standard Polybius square
        polybius_square = {
            '11': 'A', '12': 'B', '13': 'C', '14': 'D', '15': 'E',
            '21': 'F', '22': 'G', '23': 'H', '24': 'I', '25': 'J',
            '31': 'K', '32': 'L', '33': 'M', '34': 'N', '35': 'O',
            '41': 'P', '42': 'Q', '43': 'R', '44': 'S', '45': 'T',
            '51': 'U', '52': 'V', '53': 'W', '54': 'X', '55': 'Y'
        }
        
        try:
            decoded_chars = []
            for i in range(0, len(clean_data), 2):
                pair = clean_data[i:i+2]
                if pair in polybius_square:
                    decoded_chars.append(polybius_square[pair])
                else:
                    decoded_chars.append('?')
            
            decoded = ''.join(decoded_chars)
            if decoded and not '?' in decoded:
                results.append(f"Standard: {decoded}")
            
            # Try alternative mapping (I/J combined)
            polybius_alt = polybius_square.copy()
            polybius_alt['24'] = 'I/J'
            polybius_alt['25'] = 'K'
            # Shift everything after J
            shifts = {'25': 'K', '31': 'L', '32': 'M', '33': 'N', '34': 'O', '35': 'P',
                     '41': 'Q', '42': 'R', '43': 'S', '44': 'T', '45': 'U',
                     '51': 'V', '52': 'W', '53': 'X', '54': 'Y', '55': 'Z'}
            
            for key, value in shifts.items():
                polybius_alt[key] = value
            
            decoded_chars_alt = []
            for i in range(0, len(clean_data), 2):
                pair = clean_data[i:i+2]
                if pair in polybius_alt:
                    decoded_chars_alt.append(polybius_alt[pair])
                else:
                    decoded_chars_alt.append('?')
            
            decoded_alt = ''.join(decoded_chars_alt)
            if decoded_alt and not '?' in decoded_alt and decoded_alt != decoded:
                results.append(f"I/J variant: {decoded_alt}")
            
        except:
            pass
        
        return results if results else ["Invalid Polybius coordinates"]
    
    def _looks_like_text(self, text: str) -> bool:
        if len(text) < 3:
            return False
        
        # Check for reasonable letter frequency
        vowels = sum(1 for c in text.upper() if c in 'AEIOU')
        consonants = sum(1 for c in text.upper() if c.isalpha() and c not in 'AEIOU')
        
        if consonants > 0:
            vowel_ratio = vowels / (vowels + consonants)
            return 0.2 <= vowel_ratio <= 0.6
        
        return False
