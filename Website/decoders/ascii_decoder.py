"""
ASCII code decoding module.
"""

from typing import Union, List
from .base_decoder import BaseDecoder


class AsciiDecoder(BaseDecoder):
    """Decoder for ASCII code sequences."""

    def __init__(self):
        super().__init__()
        self.description = "Decodes ASCII code sequences (space or comma separated)."

    def can_decode(self, data: str) -> float:
        """Check if data looks like ASCII codes."""
        tokens = self._tokenize(data)
        if not tokens:
            return 0.0

        codes = [int(token) for token in tokens]
        if not codes:
            return 0.0

        if all(1 <= value <= 26 for value in codes):
            return 0.25

        printable = sum(1 for value in codes if 32 <= value <= 126)
        ratio = printable / len(codes)

        confidence = 0.4
        if ratio >= 0.9:
            confidence = 0.95
        elif ratio >= 0.7:
            confidence = 0.75
        elif ratio >= 0.5:
            confidence = 0.55

        if len(codes) == 1:
            confidence = min(confidence, 0.6)

        return confidence

    def _is_ascii_code(self, s: str) -> bool:
        """Check if string represents a valid ASCII code."""
        try:
            num = int(s)
            return 0 <= num <= 127
        except ValueError:
            return False

    def _tokenize(self, data: str) -> List[str]:
        """Extract numeric tokens from typical ASCII representations."""
        if not data:
            return []

        space_parts = [part for part in data.strip().split() if part]
        if len(space_parts) > 1 and all(part.isdigit() for part in space_parts):
            return space_parts

        comma_parts = [part.strip() for part in data.split(',') if part.strip()]
        if len(comma_parts) > 1 and all(part.isdigit() for part in comma_parts):
            return comma_parts

        stripped = data.strip()
        if stripped.isdigit():
            return [stripped]

        return []

    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode ASCII code sequence."""
        try:
            tokens = self._tokenize(data)
            if not tokens:
                raise ValueError("No valid ASCII codes found")

            if len(tokens) == 1:
                code = tokens[0]
                if self._is_ascii_code(code):
                    return chr(int(code))
                raise ValueError("Invalid ASCII code")

            return self._decode_parts(tokens)

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
