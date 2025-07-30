"""
Baconian cipher decoding module.
"""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class BaconianDecoder(BaseDecoder):
    """Decoder for Baconian cipher."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Baconian cipher (A/B or 0/1 patterns)."
        
        # Baconian cipher mapping (5-bit groups)
        self.bacon_to_letter = {
            'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D', 'AABAA': 'E',
            'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H', 'ABAAA': 'I', 'ABAAB': 'J',
            'ABABA': 'K', 'ABABB': 'L', 'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O',
            'ABBBB': 'P', 'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',
            'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X', 'BBAAA': 'Y',
            'BBAAB': 'Z'
        }
        
        # Alternative mapping where I=J and U=V (original Bacon cipher)
        self.bacon_to_letter_alt = {
            'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D', 'AABAA': 'E',
            'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H', 'ABAAA': 'I/J', 'ABAAB': 'K',
            'ABABA': 'L', 'ABABB': 'M', 'ABBAA': 'N', 'ABBAB': 'O', 'ABBBA': 'P',
            'ABBBB': 'Q', 'BAAAA': 'R', 'BAAAB': 'S', 'BAABA': 'T', 'BAABB': 'U/V',
            'BABAA': 'W', 'BABAB': 'X', 'BABBA': 'Y', 'BABBB': 'Z'
        }
        
        # Create reverse mapping for encoding
        self.letter_to_bacon = {v: k for k, v in self.bacon_to_letter.items()}
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like Baconian cipher."""
        if not data:
            return 0.0
        
        # Remove whitespace
        cleaned = re.sub(r'\s+', '', data)
        
        # Check for A/B pattern
        if re.match(r'^[AB]+$', cleaned.upper()):
            if len(cleaned) % 5 == 0 and len(cleaned) >= 5:
                return 0.9
            else:
                return 0.7
        
        # Check for 0/1 pattern
        if re.match(r'^[01]+$', cleaned):
            if len(cleaned) % 5 == 0 and len(cleaned) >= 5:
                return 0.8
            else:
                return 0.6
        
        # Check for binary-like patterns with other characters
        unique_chars = set(cleaned.upper())
        if len(unique_chars) == 2:
            if len(cleaned) % 5 == 0 and len(cleaned) >= 5:
                return 0.7
            else:
                return 0.5
        
        return 0.0
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Baconian cipher."""
        try:
            results = []
            
            # Remove whitespace
            cleaned = re.sub(r'\s+', '', data).upper()
            
            # Try different interpretations
            
            # 1. Direct A/B interpretation
            if re.match(r'^[AB]+$', cleaned):
                result = self._decode_ab(cleaned)
                if result:
                    results.append(f"A/B standard: {result}")
                
                result_alt = self._decode_ab_alt(cleaned)
                if result_alt and result_alt != result:
                    results.append(f"A/B alternative: {result_alt}")
            
            # 2. 0/1 to A/B interpretation
            elif re.match(r'^[01]+$', cleaned):
                ab_data = cleaned.replace('0', 'A').replace('1', 'B')
                result = self._decode_ab(ab_data)
                if result:
                    results.append(f"0/1 as A/B: {result}")
            
            # 3. Two-character pattern
            else:
                unique_chars = list(set(cleaned))
                if len(unique_chars) == 2:
                    # Map first unique char to A, second to B
                    ab_data = cleaned.replace(unique_chars[0], 'A').replace(unique_chars[1], 'B')
                    result = self._decode_ab(ab_data)
                    if result:
                        results.append(f"{unique_chars[0]}/{unique_chars[1]} as A/B: {result}")
            
            return results if results else ["Could not decode as Baconian cipher"]
            
        except Exception as e:
            raise ValueError(f"Failed to decode Baconian cipher: {str(e)}")
    
    def _decode_ab(self, data: str) -> str:
        """Decode A/B pattern using standard mapping."""
        if len(data) % 5 != 0:
            return None
        
        result = ""
        for i in range(0, len(data), 5):
            group = data[i:i+5]
            if group in self.bacon_to_letter:
                result += self.bacon_to_letter[group]
            else:
                result += "?"
        
        return result if result else None
    
    def _decode_ab_alt(self, data: str) -> str:
        """Decode A/B pattern using alternative mapping."""
        if len(data) % 5 != 0:
            return None
        
        result = ""
        for i in range(0, len(data), 5):
            group = data[i:i+5]
            if group in self.bacon_to_letter_alt:
                result += self.bacon_to_letter_alt[group]
            else:
                result += "?"
        
        return result if result else None
    
    def encode(self, data: str) -> str:
        """Encode string to Baconian cipher."""
        result = ""
        
        for char in data.upper():
            if char in self.letter_to_bacon:
                result += self.letter_to_bacon[char]
            elif char == ' ':
                result += " "
            else:
                result += "?????"  # Unknown character
        
        return result
