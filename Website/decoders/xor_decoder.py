"""
XOR cipher decoding module with key brute force.
"""

from typing import Union, List
from .base_decoder import BaseDecoder


class XORDecoder(BaseDecoder):
    """Decoder for XOR cipher with key brute force."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes XOR cipher (brute force keys 0-255)."
    
    def can_decode(self, data: str) -> float:
        """Check if data could be XOR cipher."""
        if not data:
            return 0.0
        
        # XOR can be applied to any data
        # Try a few common XOR keys to see if we get readable results
        for key in [1, 2, 3, 32, 42, 69, 123, 255]:
            try:
                decoded = self._xor_with_key(data.encode('utf-8'), key)
                if self.is_printable(decoded.decode('utf-8', errors='ignore')):
                    return 0.8
            except:
                continue
        
        return 0.3  # Could still be XOR
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode XOR cipher by trying all single-byte keys."""
        results = []
        
        try:
            # Convert input to bytes
            data_bytes = data.encode('utf-8')
            
            for key in range(1, 256):  # Try keys 1-255 (0 would be unchanged)
                try:
                    decoded_bytes = self._xor_with_key(data_bytes, key)
                    decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                    
                    if self.is_printable(decoded_str) and self._looks_like_text(decoded_str):
                        results.append(f"Key {key}: {decoded_str}")
                except:
                    continue
            
            # Also try multi-character keys if no single-byte key worked
            if not results:
                common_keys = ['key', 'secret', 'password', 'xor', '123', 'abc']
                for key_str in common_keys:
                    try:
                        decoded_bytes = self._xor_with_string_key(data_bytes, key_str)
                        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                        
                        if self.is_printable(decoded_str) and self._looks_like_text(decoded_str):
                            results.append(f"Key '{key_str}': {decoded_str}")
                    except:
                        continue
            
        except Exception as e:
            raise ValueError(f"Failed to decode XOR: {str(e)}")
        
        return results if results else ["No readable XOR decryption found"]
    
    def _xor_with_key(self, data: bytes, key: int) -> bytes:
        """XOR data with single-byte key."""
        return bytes(b ^ key for b in data)
    
    def _xor_with_string_key(self, data: bytes, key: str) -> bytes:
        """XOR data with multi-character key."""
        key_bytes = key.encode('utf-8')
        result = bytearray()
        
        for i, byte in enumerate(data):
            key_byte = key_bytes[i % len(key_bytes)]
            result.append(byte ^ key_byte)
        
        return bytes(result)
    
    def _looks_like_text(self, text: str) -> bool:
        """Check if text looks like readable content."""
        if len(text) < 3:
            return False
        
        # Check for common English patterns
        common_words = ['the', 'and', 'you', 'that', 'was', 'for', 'are', 'with']
        text_lower = text.lower()
        
        for word in common_words:
            if word in text_lower:
                return True
        
        # Check for reasonable character distribution
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count > 0:
            space_count = text.count(' ')
            # Reasonable ratio of spaces to letters
            if space_count / alpha_count > 0.1 and space_count / alpha_count < 0.5:
                return True
        
        return False
    
    def encode(self, data: str, key: int = 42) -> str:
        """Encode string with XOR cipher."""
        data_bytes = data.encode('utf-8')
        encoded_bytes = self._xor_with_key(data_bytes, key)
        return encoded_bytes.decode('utf-8', errors='ignore')
