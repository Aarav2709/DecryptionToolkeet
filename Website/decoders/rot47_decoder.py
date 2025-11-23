"""ROT47 decoding module."""

from typing import Union, List
from .base_decoder import BaseDecoder


class ROT47Decoder(BaseDecoder):
    """Decoder for ROT47 substitution (printable ASCII shift)."""

    name = "rot47"
    description = "Decodes ROT47 cipher that shifts printable ASCII by 47 positions."

    _START = 33
    _END = 126
    _RANGE = _END - _START + 1

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        printable = sum(1 for ch in data if self._START <= ord(ch) <= self._END)
        ratio = printable / len(data)
        if ratio < 0.7:
            return 0.0

        decoded = self._rot47(data)
        letters = sum(1 for c in decoded if c.isalpha())
        letter_ratio = letters / len(decoded) if decoded else 0
        if letter_ratio < 0.3:
            return 0.2

        if self._looks_like_text(decoded):
            return 0.85
        return 0.4

    def decode(self, data: str) -> Union[str, List[str]]:
        return self._rot47(data)

    def _rot47(self, text: str) -> str:
        result_chars = []
        for char in text:
            code = ord(char)
            if self._START <= code <= self._END:
                rotated = ((code - self._START + 47) % self._RANGE) + self._START
                result_chars.append(chr(rotated))
            else:
                result_chars.append(char)
        return ''.join(result_chars)

    def _looks_like_text(self, text: str) -> bool:
        if not text:
            return False
        letters = sum(1 for c in text if c.isalpha())
        spaces = text.count(' ')
        return (letters + spaces) / len(text) > 0.6
