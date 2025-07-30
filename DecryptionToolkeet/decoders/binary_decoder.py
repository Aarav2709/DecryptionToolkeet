"""
Binary encoding/decoding module.
"""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class BinaryDecoder(BaseDecoder):
    """Decoder for binary encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes binary encoded strings."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like binary."""
        if not data:
            return 0.0
        
        # Remove whitespace
        cleaned = re.sub(r'\s+', '', data)
        
        # Should only contain 0s and 1s
        if not re.match(r'^[01]+$', cleaned):
            return 0.0
        
        # Should be multiple of 8 for byte representation
        if len(cleaned) % 8 != 0:
            return 0.6  # Still could be binary, but lower confidence
        
        # Higher confidence for longer strings
        confidence = 0.8
        if len(cleaned) > 32:
            confidence = 0.95
        
        return confidence
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode binary string."""
        try:
            # Remove whitespace
            cleaned = re.sub(r'\s+', '', data)
            
            # Split into 8-bit chunks
            byte_chunks = [cleaned[i:i+8] for i in range(0, len(cleaned), 8)]
            
            # Convert each chunk to a byte
            decoded_bytes = bytearray()
            for chunk in byte_chunks:
                if len(chunk) == 8:  # Only process complete bytes
                    decoded_bytes.append(int(chunk, 2))
            
            if not decoded_bytes:
                raise ValueError("No complete bytes found")
            
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
            
            # If all else fails, return hex representation
            return decoded_bytes.hex()
            
        except Exception as e:
            raise ValueError(f"Failed to decode binary: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to binary."""
        binary_str = ''
        for char in data:
            binary_str += format(ord(char), '08b')
        return binary_str
