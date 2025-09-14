from .base_decoder import BaseDecoder
import re


class XXDecoder(BaseDecoder):
    name = "xxencode"
    description = "Decodes XXencoded data (UUencode variant with different charset)."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 10:
            return 0.0
        
        lines = data.strip().split('\\n')
        confidence = 0.0
        
        # Check for XXencode header pattern
        if lines and lines[0].startswith('begin '):
            confidence += 0.4
        
        # Check for XXencode charset (+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz)
        xx_chars = set('+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
        
        for line in lines[1:-1]:
            if line and len(line) > 1:
                # Check if line uses XXencode charset
                line_chars = set(line[1:])  # Skip length byte
                if line_chars.issubset(xx_chars):
                    confidence += 0.3
                    break
        
        return min(0.8, confidence)
    
    def decode(self, data: str) -> list:
        try:
            lines = data.strip().split('\\n')
            
            # Find begin line
            start_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('begin '):
                    start_idx = i + 1
                    break
            
            # Find end line
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if line in ['end', '++']:
                    end_idx = i
                    break
            
            # Decode XXencoded lines
            result = []
            for line in lines[start_idx:end_idx]:
                if line:
                    decoded_line = self._decode_xx_line(line)
                    if decoded_line is not None:
                        result.extend(decoded_line)
            
            if result:
                decoded_text = bytes(result).decode('ascii', errors='ignore')
                return [f"XXdecoded: {decoded_text}"]
            
        except Exception:
            pass
        
        return ["Invalid XXencoded data"]
    
    def _decode_xx_line(self, line: str) -> list:
        if not line:
            return []
        
        # XXencode character set
        xx_charset = '+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        
        # First character indicates length
        length = xx_charset.index(line[0]) if line[0] in xx_charset else 0
        line = line[1:]  # Remove length character
        
        # Decode the rest of the line
        result = []
        for i in range(0, len(line), 4):
            if i + 3 < len(line):
                # Get 4 characters and convert to indices
                try:
                    chars = [xx_charset.index(c) for c in line[i:i+4]]
                    
                    # Convert to 3 bytes
                    b1 = (chars[0] << 2) | (chars[1] >> 4)
                    b2 = ((chars[1] & 15) << 4) | (chars[2] >> 2)
                    b3 = ((chars[2] & 3) << 6) | chars[3]
                    
                    result.extend([b1 & 255, b2 & 255, b3 & 255])
                except ValueError:
                    continue
        
        # Trim to actual length
        return result[:length]
