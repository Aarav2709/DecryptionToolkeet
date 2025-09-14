"""
Base85 encoding/decoding module.
"""

import base64
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class Base85Decoder(BaseDecoder):
    """Decoder for Base85 (ASCII85) encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Base85/ASCII85 encoded strings."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like Base85."""
        if not data:
            return 0.0
        
        # Remove whitespace
        cleaned = re.sub(r'\s+', '', data)
        
        # ASCII85 often wrapped in <~ and ~>
        if cleaned.startswith('<~') and cleaned.endswith('~>'):
            cleaned = cleaned[2:-2]
            confidence_boost = 0.3
        else:
            confidence_boost = 0.0
        
        # Base85 uses ASCII 33-117 (! to u)
        valid_chars = set(chr(i) for i in range(33, 118))
        if not all(c in valid_chars for c in cleaned):
            return 0.0
        
        # Length should be multiple of 5 for most cases
        base_confidence = 0.6 + confidence_boost
        if len(cleaned) % 5 == 0:
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Base85 string."""
        try:
            # Remove whitespace
            cleaned = re.sub(r'\s+', '', data)
            
            # Handle ASCII85 wrapper
            if cleaned.startswith('<~') and cleaned.endswith('~>'):
                cleaned = cleaned[2:-2]
            
            # Try standard Base85
            decoded_bytes = base64.a85decode(cleaned)
            
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
            raise ValueError(f"Failed to decode Base85: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to Base85."""
        encoded = base64.a85encode(data.encode('utf-8')).decode('ascii')
        return f"<~{encoded}~>"  # Wrap in ASCII85 format
