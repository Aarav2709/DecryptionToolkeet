from .base_decoder import BaseDecoder
import re


class UUDecoder(BaseDecoder):
    name = "uuencode"
    description = "Decodes UUencoded data (Unix-to-Unix encoding) with begin/end markers."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 10:
            return 0.0
        
        lines = data.strip().split('\\n')
        confidence = 0.0
        
        # Check for UUencode header pattern
        if lines and lines[0].startswith('begin '):
            confidence += 0.6
        
        # Check for UUencode footer
        if lines and (lines[-1] == 'end' or lines[-1] == '`'):
            confidence += 0.2
        
        # Check for typical UUencode line format
        for line in lines[1:-1]:  # Skip header and footer
            if line and len(line) > 0:
                first_char = ord(line[0])
                # UUencode length character should be in printable range
                if 32 <= first_char <= 95:
                    confidence += 0.1
                    break
        
        return min(0.9, confidence)
    
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
                if line in ['end', '`']:
                    end_idx = i
                    break
            
            # Decode UUencoded lines
            result = []
            for line in lines[start_idx:end_idx]:
                if line:
                    decoded_line = self._decode_uu_line(line)
                    if decoded_line is not None:
                        result.extend(decoded_line)
            
            if result:
                decoded_text = bytes(result).decode('ascii', errors='ignore')
                return [f"UUdecoded: {decoded_text}"]
            
        except Exception:
            pass
        
        return ["Invalid UUencoded data"]
    
    def _decode_uu_line(self, line: str) -> list:
        if not line:
            return []
        
        # First character indicates length
        length = (ord(line[0]) - 32) % 64
        line = line[1:]  # Remove length character
        
        # Decode the rest of the line
        result = []
        for i in range(0, len(line), 4):
            if i + 3 < len(line):
                # Get 4 characters
                chars = [ord(c) - 32 for c in line[i:i+4]]
                
                # Convert to 3 bytes
                b1 = (chars[0] << 2) | (chars[1] >> 4)
                b2 = ((chars[1] & 15) << 4) | (chars[2] >> 2)
                b3 = ((chars[2] & 3) << 6) | chars[3]
                
                result.extend([b1 & 255, b2 & 255, b3 & 255])
        
        # Trim to actual length
        return result[:length]
