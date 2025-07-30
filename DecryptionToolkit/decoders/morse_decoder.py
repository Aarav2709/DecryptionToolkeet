"""
Morse code decoding module.
"""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class MorseDecoder(BaseDecoder):
    """Decoder for Morse code."""
    
    def __init__(self):
        super().__init__()
        self.description = "Decodes Morse code (dots, dashes, spaces)."
        
        # Morse code dictionary
        self.morse_to_letter = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z',
            '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5',
            '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0',
            '--..--': ',', '.-.-.-': '.', '..--..': '?', '.----.': "'", '-.-.--': '!',
            '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':',
            '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-', '..--.-': '_',
            '.-..-.': '"', '...-..-': '$', '.--.-.': '@'
        }
        
        # Reverse dictionary for encoding
        self.letter_to_morse = {v: k for k, v in self.morse_to_letter.items()}
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like Morse code."""
        if not data:
            return 0.0
        
        # Remove whitespace for analysis
        cleaned = re.sub(r'\s+', '', data)
        
        # Should only contain dots, dashes, spaces, and slash for word separation
        if not re.match(r'^[.\-\s/]+$', data):
            return 0.0
        
        # Should have a good ratio of dots and dashes
        dots = cleaned.count('.')
        dashes = cleaned.count('-')
        
        if dots == 0 and dashes == 0:
            return 0.0
        
        # Morse code typically has more dots than dashes
        total_symbols = dots + dashes
        if total_symbols > 0:
            confidence = 0.7
            
            # Higher confidence if it has reasonable spacing
            if ' ' in data or '/' in data:
                confidence = 0.9
            
            return confidence
        
        return 0.0
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode Morse code."""
        try:
            # Try different separators
            results = []
            
            # Try space-separated
            if ' ' in data:
                result = self._decode_with_separator(data, ' ')
                if result:
                    results.append(f"Space separated: {result}")
            
            # Try slash-separated
            if '/' in data:
                result = self._decode_with_separator(data, '/')
                if result:
                    results.append(f"Slash separated: {result}")
            
            # Try double-space for word separation
            if '  ' in data:
                result = self._decode_with_word_separator(data, ' ', '  ')
                if result:
                    results.append(f"Double-space words: {result}")
            
            # If no separators, try to decode as continuous
            if not results:
                result = self._decode_continuous(data)
                if result:
                    results.append(f"Continuous: {result}")
            
            return results if results else ["Could not decode Morse code"]
            
        except Exception as e:
            raise ValueError(f"Failed to decode Morse code: {str(e)}")
    
    def _decode_with_separator(self, data: str, separator: str) -> str:
        """Decode Morse code with given separator."""
        parts = data.split(separator)
        result = ""
        
        for part in parts:
            part = part.strip()
            if part in self.morse_to_letter:
                result += self.morse_to_letter[part]
            elif part == "":
                result += " "  # Empty part becomes space
            else:
                result += "?"  # Unknown code
        
        return result
    
    def _decode_with_word_separator(self, data: str, letter_sep: str, word_sep: str) -> str:
        """Decode Morse code with letter and word separators."""
        words = data.split(word_sep)
        result_words = []
        
        for word in words:
            letters = word.split(letter_sep)
            word_result = ""
            
            for letter in letters:
                letter = letter.strip()
                if letter in self.morse_to_letter:
                    word_result += self.morse_to_letter[letter]
                elif letter:
                    word_result += "?"
            
            if word_result:
                result_words.append(word_result)
        
        return " ".join(result_words)
    
    def _decode_continuous(self, data: str) -> str:
        """Try to decode continuous Morse code (difficult without separators)."""
        # This is challenging - we'll try to match known patterns
        cleaned = data.replace(' ', '')
        
        # Try to find valid Morse combinations
        result = ""
        i = 0
        
        while i < len(cleaned):
            found = False
            
            # Try longest patterns first
            for length in range(6, 0, -1):
                if i + length <= len(cleaned):
                    pattern = cleaned[i:i+length]
                    if pattern in self.morse_to_letter:
                        result += self.morse_to_letter[pattern]
                        i += length
                        found = True
                        break
            
            if not found:
                result += "?"
                i += 1
        
        return result if result else None
    
    def encode(self, data: str) -> str:
        """Encode string to Morse code."""
        result = []
        
        for char in data.upper():
            if char == ' ':
                result.append('/')  # Word separator
            elif char in self.letter_to_morse:
                result.append(self.letter_to_morse[char])
            else:
                result.append('?')  # Unknown character
        
        return ' '.join(result)
