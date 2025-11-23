"""A1Z26 decoding module."""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class A1Z26Decoder(BaseDecoder):
    """Decoder for A1Z26 numeral substitution."""

    name = "a1z26"
    description = "Decodes A1Z26 where numbers 1-26 map to letters (e.g., 1 = A)."

    _TOKEN_PATTERN = re.compile(r"\d{1,2}")

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        tokens = self._tokenize(data)
        if not tokens or len(tokens) < 2:
            return 0.0

        valid = sum(1 for tok in tokens if 1 <= int(tok) <= 26)
        ratio = valid / len(tokens)
        if ratio < 0.9:
            return 0.0

        return min(0.4 + 0.1 * (len(tokens) > 4), 0.85)

    def decode(self, data: str) -> Union[str, List[str]]:
        tokens = self._tokenize(data)
        if not tokens:
            raise ValueError("No numeric tokens found for A1Z26 decoding")

        chars = []
        for tok in tokens:
            value = int(tok)
            if not 1 <= value <= 26:
                raise ValueError(f"Invalid A1Z26 value: {value}")
            if value == 0:
                chars.append(' ')
            else:
                chars.append(chr(ord('A') + value - 1))

        return ''.join(chars)

    def _tokenize(self, data: str) -> List[str]:
        normalized = data.replace('-', ' ').replace('/', ' ').replace(',', ' ')
        tokens = [tok for tok in normalized.split() if tok.isdigit()]
        if tokens:
            return tokens
        return self._TOKEN_PATTERN.findall(data)
