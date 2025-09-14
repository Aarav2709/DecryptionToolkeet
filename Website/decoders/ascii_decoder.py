"""
ASCII code decoding module.
"""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class AsciiDecoder(BaseDecoder):
    """Decoder for ASCII code sequences."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes ASCII code sequences (space or comma separated)."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like ASCII codes."""
        if not data:
            return 0.0
        
        # Try space-separated format
        space_parts = data.strip().split()
        if len(space_parts) > 1 and all(self._is_ascii_code(part) for part in space_parts):
            return 0.9
        
        # Try comma-separated format
        comma_parts = [part.strip() for part in data.split(',')]
        if len(comma_parts) > 1 and all(self._is_ascii_code(part) for part in comma_parts):
            return 0.9
        
        # Try single ASCII code
        if self._is_ascii_code(data.strip()):
            return 0.6
        
        return 0.0
    
    def _is_ascii_code(self, s: str) -> bool:
        """Check if string represents a valid ASCII code."""
        try:
            num = int(s)
            return 0 <= num <= 127
        except ValueError:
            return False
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode ASCII code sequence."""
        try:
            # Try space-separated format first
            parts = data.strip().split()
            if len(parts) > 1 and all(self._is_ascii_code(part) for part in parts):
                return self._decode_parts(parts)
            
            # Try comma-separated format
            parts = [part.strip() for part in data.split(',')]
            if len(parts) > 1 and all(self._is_ascii_code(part) for part in parts):
                return self._decode_parts(parts)
            
            # Try single code
            if self._is_ascii_code(data.strip()):
                return chr(int(data.strip()))
            
            raise ValueError("No valid ASCII codes found")
            
        except Exception as e:
            raise ValueError(f"Failed to decode ASCII codes: {str(e)}")
    
    def _decode_parts(self, parts: List[str]) -> str:
        """Decode list of ASCII code strings."""
        result = ''
        for part in parts:
            if self._is_ascii_code(part):
                result += chr(int(part))
        return result
    
    def encode(self, data: str) -> str:
        """Encode string to ASCII codes."""
        return ' '.join(str(ord(char)) for char in data)
