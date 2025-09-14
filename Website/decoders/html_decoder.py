"""
HTML entity decoding module.
"""

import html
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class HTMLDecoder(BaseDecoder):
    """Decoder for HTML entity encoded strings."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes HTML entity encoded strings."
    
    def can_decode(self, data: str) -> float:
        """Check if data contains HTML entities."""
        if not data:
            return 0.0
        
        # Look for named entities
        named_entities = len(re.findall(r'&[a-zA-Z][a-zA-Z0-9]*;', data))
        
        # Look for numeric entities
        numeric_entities = len(re.findall(r'&#\d+;', data))
        
        # Look for hex entities
        hex_entities = len(re.findall(r'&#x[0-9a-fA-F]+;', data))
        
        total_entities = named_entities + numeric_entities + hex_entities
        
        if total_entities == 0:
            return 0.0
        
        # Higher confidence with more entities
        if total_entities >= 5:
            return 0.95
        elif total_entities >= 2:
            return 0.8
        else:
            return 0.6
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode HTML entity encoded string."""
        try:
            # Use html.unescape to decode all HTML entities
            decoded = html.unescape(data)
            return decoded
            
        except Exception as e:
            raise ValueError(f"Failed to decode HTML entities: {str(e)}")
    
    def encode(self, data: str) -> str:
        """Encode string to HTML entities."""
        return html.escape(data)
