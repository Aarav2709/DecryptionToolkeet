"""
Base64 encoding/decoding module.
"""

import base64
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class Base64Decoder(BaseDecoder):
    """Decoder for Base64 encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Base64 encoded strings."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like Base64."""
        if not data:
            return 0.0
        
        # Remove whitespace
        cleaned = re.sub(r'\s+', '', data)
        
        # Base64 uses A-Z, a-z, 0-9, +, / and = for padding
        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', cleaned):
            return 0.0
        
        # Length should be multiple of 4 (after padding)
        if len(cleaned) % 4 != 0:
            return 0.0
        
        # Should have at most 2 padding characters at the end
        padding_count = cleaned.count('=')
        if padding_count > 2:
            return 0.0
        
        # Padding should only be at the end
        if '=' in cleaned and not cleaned.endswith('=' * padding_count):
            return 0.0
        
        # Boost confidence for typical Base64 characteristics
        confidence = 0.7
        
        # Higher confidence for longer strings
        if len(cleaned) > 20:
            confidence = 0.9
        
        # Extra boost if it has padding (very Base64-like)
        if padding_count > 0:
            confidence += 0.2
        
        # Extra boost if it has mixed case (common in Base64)
        has_upper = any(c.isupper() for c in cleaned if c.isalpha())
        has_lower = any(c.islower() for c in cleaned if c.isalpha())
        if has_upper and has_lower:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Base64 string."""
        try:
            # Remove whitespace
            cleaned = re.sub(r'\s+', '', data)
            
            # Try standard Base64
            decoded_bytes = base64.b64decode(cleaned)
            
            # Try to decode as UTF-8
            try:
                decoded_str = decoded_bytes.decode('utf-8')
                if self.is_printable(decoded_str):
                    return decoded_str
            except UnicodeDecodeError:
                pass
            
            # Try other common encodings
            for encoding in ['latin-1', 'ascii', 'cp1252']:
                try:
                    decoded_str = decoded_bytes.decode(encoding)
                    if self.is_printable(decoded_str):
                        return decoded_str
                except UnicodeDecodeError:
                    continue
            
            # If all else fails, return the hex representation
            return decoded_bytes.hex()
            
        except Exception as e:
            raise ValueError(f"Failed to decode Base64: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to Base64."""
        return base64.b64encode(data.encode('utf-8')).decode('ascii')
