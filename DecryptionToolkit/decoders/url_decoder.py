"""
URL encoding/decoding module.
"""

import urllib.parse
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class URLDecoder(BaseDecoder):
    """Decoder for URL encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes URL encoded strings (percent encoding)."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like URL encoded."""
        if not data:
            return 0.0
        
        # Look for percent encoding pattern
        percent_count = len(re.findall(r'%[0-9a-fA-F]{2}', data))
        
        if percent_count == 0:
            return 0.0
        
        # Higher confidence with more percent encodings
        total_chars = len(data)
        percent_ratio = (percent_count * 3) / total_chars  # Each %XX is 3 chars
        
        if percent_ratio > 0.3:
            return 0.95
        elif percent_ratio > 0.1:
            return 0.8
        else:
            return 0.6
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode URL encoded string."""
        try:
            # URL decode
            decoded = urllib.parse.unquote(data)
            
            # Also try unquote_plus for + as space
            decoded_plus = urllib.parse.unquote_plus(data)
            
            # Return the one that looks most readable
            if decoded != decoded_plus:
                if self.is_printable(decoded_plus) and ' ' in decoded_plus:
                    return decoded_plus
            
            return decoded
            
        except Exception as e:
            raise ValueError(f"Failed to decode URL encoding: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to URL encoding."""
        return urllib.parse.quote(data)
