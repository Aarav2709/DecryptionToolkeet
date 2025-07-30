"""
Hexadecimal encoding/decoding module.
"""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class HexDecoder(BaseDecoder):
    """Decoder for hexadecimal encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes hexadecimal encoded strings."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like hexadecimal."""
        if not data:
            return 0.0
        
        # Remove whitespace and common prefixes
        cleaned = re.sub(r'\s+', '', data)
        cleaned = re.sub(r'^(0x|\\x)', '', cleaned, flags=re.IGNORECASE)
        
        # Should only contain hex characters
        if not re.match(r'^[0-9a-fA-F]+$', cleaned):
            return 0.0
        
        # Should have even length (pairs of hex digits)
        if len(cleaned) % 2 != 0:
            return 0.0
        
        # Higher confidence for longer strings
        confidence = 0.8
        if len(cleaned) > 20:
            confidence = 0.95
        
        return confidence
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode hexadecimal string."""
        try:
            # Remove whitespace and common prefixes
            cleaned = re.sub(r'\s+', '', data)
            cleaned = re.sub(r'^(0x|\\x)', '', cleaned, flags=re.IGNORECASE)
            
            # Convert hex to bytes
            decoded_bytes = bytes.fromhex(cleaned)
            
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
            
            # If all else fails, return raw bytes representation
            return str(decoded_bytes)
            
        except Exception as e:
            raise ValueError(f"Failed to decode hexadecimal: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to hexadecimal."""
        return data.encode('utf-8').hex()
