"""
Unicode and Zalgo text cleanup module.
"""

import unicodedata
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class UnicodeDecoder(BaseDecoder):
    """Decoder for Unicode normalization and Zalgo cleanup."""
    
    def __init__(self):
        super().__init__()
        self.description = "Cleans up Unicode text and removes Zalgo/diacritical marks."
    
    def can_decode(self, data: str) -> float:
        """Check if data contains special Unicode characters."""
        if not data:
            return 0.0
        
        # Check for combining characters (diacritical marks)
        combining_chars = sum(1 for c in data if unicodedata.combining(c))
        
        # Check for various Unicode categories that might need cleaning
        special_chars = sum(1 for c in data if unicodedata.category(c) in ['Mn', 'Mc', 'Me'])
        
        if combining_chars > 0 or special_chars > 0:
            return 0.9
        
        # Check for non-ASCII characters
        non_ascii = sum(1 for c in data if ord(c) > 127)
        if non_ascii > 0:
            return 0.6
        
        return 0.0
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Clean up Unicode text and normalize it."""
        results = []
        
        # 1. Remove combining characters (Zalgo cleanup)
        zalgo_cleaned = self._remove_combining_chars(data)
        if zalgo_cleaned != data:
            results.append(f"Zalgo removed: {zalgo_cleaned}")
        
        # 2. Unicode normalization forms
        nfc = unicodedata.normalize('NFC', data)
        if nfc != data:
            results.append(f"NFC normalized: {nfc}")
        
        nfd = unicodedata.normalize('NFD', data)
        if nfd != data:
            results.append(f"NFD normalized: {nfd}")
        
        nfkc = unicodedata.normalize('NFKC', data)
        if nfkc != data:
            results.append(f"NFKC normalized: {nfkc}")
        
        nfkd = unicodedata.normalize('NFKD', data)
        if nfkd != data:
            results.append(f"NFKD normalized: {nfkd}")
        
        # 3. Convert Unicode escapes
        unicode_escaped = self._decode_unicode_escapes(data)
        if unicode_escaped != data:
            results.append(f"Unicode escapes decoded: {unicode_escaped}")
        
        # 4. Remove all non-printable characters
        printable_only = self._keep_printable_only(data)
        if printable_only != data:
            results.append(f"Printable only: {printable_only}")
        
        # 5. Transliterate to ASCII
        ascii_transliterated = self._transliterate_to_ascii(data)
        if ascii_transliterated != data:
            results.append(f"ASCII transliterated: {ascii_transliterated}")
        
        return results if results else [data]  # Return original if no changes
    
    def _remove_combining_chars(self, text: str) -> str:
        """Remove combining characters (diacritical marks)."""
        return ''.join(c for c in text if not unicodedata.combining(c))
    
    def _decode_unicode_escapes(self, text: str) -> str:
        """Decode Unicode escape sequences like \\uXXXX."""
        try:
            # Handle \\uXXXX escapes
            result = re.sub(r'\\u([0-9a-fA-F]{4})', 
                          lambda m: chr(int(m.group(1), 16)), text)
            
            # Handle \\UXXXXXXXX escapes
            result = re.sub(r'\\U([0-9a-fA-F]{8})', 
                          lambda m: chr(int(m.group(1), 16)), result)
            
            # Handle \\xXX escapes
            result = re.sub(r'\\x([0-9a-fA-F]{2})', 
                          lambda m: chr(int(m.group(1), 16)), result)
            
            return result
        except:
            return text
    
    def _keep_printable_only(self, text: str) -> str:
        """Keep only printable characters."""
        return ''.join(c for c in text if c.isprintable() or c in '\\n\\r\\t')
    
    def _transliterate_to_ascii(self, text: str) -> str:
        """Transliterate Unicode text to ASCII equivalents."""
        try:
            # First normalize to NFD to separate base characters from diacritics
            nfd = unicodedata.normalize('NFD', text)
            
            # Remove combining characters
            ascii_text = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
            
            # Try to encode as ASCII, replacing non-ASCII characters
            return ascii_text.encode('ascii', errors='replace').decode('ascii')
        except:
            return text
    
    def get_unicode_info(self, text: str) -> List[str]:
        """Get detailed Unicode information about the text."""
        info = []
        
        for i, char in enumerate(text):
            if ord(char) > 127 or unicodedata.combining(char):
                name = unicodedata.name(char, 'UNKNOWN')
                category = unicodedata.category(char)
                combining = unicodedata.combining(char)
                
                info.append(f"Pos {i}: '{char}' U+{ord(char):04X} {name} [{category}]" + 
                          (f" combining={combining}" if combining else ""))
        
        return info
