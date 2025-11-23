"""ROT18 decoding module."""

from typing import Union, List
from .base_decoder import BaseDecoder


class ROT18Decoder(BaseDecoder):
    """Decoder for ROT18 (ROT13 for letters + ROT5 for digits)."""

    name = "rot18"
    description = "Decodes ROT18 cipher (ROT13 applied to letters plus ROT5 to digits)."

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0
        alnum = sum(1 for ch in data if ch.isalnum())
        if alnum / len(data) < 0.6:
            return 0.0
        decoded = self._rot18(data)
        if self._looks_like_text(decoded):
            return 0.85
        return 0.4

    def decode(self, data: str) -> Union[str, List[str]]:
        return self._rot18(data)

    def _rot18(self, text: str) -> str:
        result = []
        for char in text:
            if char.isalpha():
                start = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - start + 13) % 26
                result.append(chr(start + shifted))
            elif char.isdigit():
                result.append(str((int(char) + 5) % 10))
            else:
                result.append(char)
        return ''.join(result)

    def _looks_like_text(self, text: str) -> bool:
        letters = sum(1 for c in text if c.isalpha())
        spaces = text.count(' ')
        return len(text) > 0 and (letters + spaces) / len(text) > 0.6
