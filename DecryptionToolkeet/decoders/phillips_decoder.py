from .base_decoder import BaseDecoder
import re


class PhillipsDecoder(BaseDecoder):
    name = "phillips"
    description = "Decodes Phillips cipher using 8x8 grid with coordinate pairs."
    
    def can_decode(self, data: str) -> float:
        if not data or len(data) < 4:
            return 0.0
        
        # Phillips uses digit pairs for coordinates
        clean_data = ''.join(c for c in data if c.isdigit())
        
        if not clean_data or len(clean_data) % 2 != 0:
            return 0.1
        
        # Check if all digits are valid Phillips coordinates (1-8)
        valid_coords = all(d in '12345678' for d in clean_data)
        
        if not valid_coords:
            return 0.2
        
        confidence = 0.7
        
        # Check for reasonable patterns
        pairs = [clean_data[i:i+2] for i in range(0, len(clean_data), 2)]
        unique_pairs = len(set(pairs))
        
        if unique_pairs / len(pairs) > 0.5:
            confidence += 0.2
        
        return min(0.9, confidence)
    
    def decode(self, data: str) -> list:
        results = []
        clean_data = ''.join(c for c in data if c.isdigit())
        
        if len(clean_data) % 2 != 0:
            return ["Input must be even length for Phillips cipher"]
        
        try:
            decoded = self._decode_phillips(clean_data)
            if decoded:
                results.append(f"Standard grid: {decoded}")
        except:
            pass
        
        return results if results else ["Invalid Phillips coordinates"]
    
    def _decode_phillips(self, data: str) -> str:
        # Standard 8x8 Phillips square
        phillips_grid = [
            ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
            ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P'],
            ['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X'],
            ['Y', 'Z', '0', '1', '2', '3', '4', '5'],
            ['6', '7', '8', '9', '.', ',', '?', '!'],
            [' ', '(', ')', '-', ':', ';', '"', "'"],
            ['/', '\\', '+', '=', '*', '&', '%', '$'],
            ['@', '#', '<', '>', '[', ']', '{', '}']
        ]
        
        result = []
        for i in range(0, len(data), 2):
            row = int(data[i]) - 1
            col = int(data[i+1]) - 1
            
            if 0 <= row < 8 and 0 <= col < 8:
                result.append(phillips_grid[row][col])
            else:
                result.append('?')
        
        return ''.join(result)
