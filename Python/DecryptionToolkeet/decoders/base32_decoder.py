"""
Base32 encoding/decoding module.
"""

import base64
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class Base32Decoder(BaseDecoder):
    """Decoder for Base32 encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Base32 encoded strings."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like Base32."""
        if not data:
            return 0.0
        
        # Remove whitespace
        cleaned = re.sub(r'\s+', '', data).upper()
        
        # Base32 uses A-Z and 2-7, with = for padding
        if not re.match(r'^[A-Z2-7]*={0,6}$', cleaned):
            return 0.0
        
        # Length should be multiple of 8 (after padding)
        if len(cleaned) % 8 != 0:
            return 0.0
        
        # Should have at most 6 padding characters at the end
        padding_count = cleaned.count('=')
        if padding_count > 6:
            return 0.0
        
        # Padding should only be at the end
        if '=' in cleaned and not cleaned.endswith('=' * padding_count):
            return 0.0
        
        # Higher confidence for longer strings
        confidence = 0.7
        if len(cleaned) > 16:
            confidence = 0.9
        
        return confidence
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Base32 string."""
        try:
            # Remove whitespace and convert to uppercase
            cleaned = re.sub(r'\s+', '', data).upper()
            
            # Try standard Base32
            decoded_bytes = base64.b32decode(cleaned)
            
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
            raise ValueError(f"Failed to decode Base32: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to Base32."""
        return base64.b32encode(data.encode('utf-8')).decode('ascii')
