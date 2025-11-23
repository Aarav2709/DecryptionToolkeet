"""ROT5 decoding module."""

from typing import Union, List
from .base_decoder import BaseDecoder


class ROT5Decoder(BaseDecoder):
    """Decoder for ROT5 digit rotation."""

    name = "rot5"
    description = "Decodes ROT5 cipher that rotates digits by 5 (0-9)."

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        digits = sum(1 for ch in data if ch.isdigit())
        if digits == 0:
            return 0.0

        ratio = digits / len(data)
        if ratio < 0.5:
            return 0.2

        decoded = self._rot5(data)
        if any(ch.isdigit() for ch in decoded) is False:
            return 0.6
        return 0.4

    def decode(self, data: str) -> Union[str, List[str]]:
        return self._rot5(data)

    def _rot5(self, text: str) -> str:
        result = []
        for char in text:
            if char.isdigit():
                rotated = (int(char) + 5) % 10
                result.append(str(rotated))
            else:
                result.append(char)
        return ''.join(result)
