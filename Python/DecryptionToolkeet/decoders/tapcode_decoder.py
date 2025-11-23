"""Tap code decoding module."""

from typing import Union, List
from .base_decoder import BaseDecoder


class TapCodeDecoder(BaseDecoder):
    """Decoder for Tap code (5x5 Polybius variant for POWs)."""

    name = "tapcode"
    description = "Decodes Tap code pairs (rows/columns 1-5, I/J combined)."

    _GRID = [
        ["A", "B", "C", "D", "E"],
        ["F", "G", "H", "I", "J"],
        ["L", "M", "N", "O", "P"],
        ["Q", "R", "S", "T", "U"],
        ["V", "W", "X", "Y", "Z"],
    ]

    def can_decode(self, data: str) -> float:
        tokens = self._tokenize(data)
        if not tokens or len(tokens) % 2 != 0:
            return 0.0

        valid_pairs = 0
        for row, col in tokens:
            if 1 <= row <= 5 and 1 <= col <= 5:
                valid_pairs += 1
        if valid_pairs != len(tokens):
            return 0.0

        confidence = 0.4
        if len(tokens) >= 4:
            confidence += 0.3
        return min(confidence, 0.85)

    def decode(self, data: str) -> Union[str, List[str]]:
        tokens = self._tokenize(data)
        if not tokens:
            raise ValueError("No tap code pairs detected")
        if len(tokens) % 2 != 0:
            raise ValueError("Tap code requires complete row/column pairs")

        chars = []
        for row, col in tokens:
            if not (1 <= row <= 5 and 1 <= col <= 5):
                raise ValueError(f"Invalid tap code coordinate: {row}{col}")
            letter = self._GRID[row - 1][col - 1]
            chars.append('I' if letter == 'J' else letter)

        return ''.join(chars)

    def _tokenize(self, data: str) -> List[tuple]:
        sanitized = data.replace('.', ' ').replace('-', ' ').replace('/', ' ')
        parts = [part for part in sanitized.split() if part]

        tokens: List[tuple] = []
        for part in parts:
            if len(part) == 2 and part.isdigit():
                tokens.append((int(part[0]), int(part[1])))
            elif len(part) == 1 and part.isdigit():
                tokens.append((int(part), 0))

        # Merge singles into pairs if data provided as separate row and column numbers
        if tokens and any(col == 0 for _, col in tokens):
            numbers = [int(part) for part in parts if part.isdigit()]
            tokens = []
            for i in range(0, len(numbers), 2):
                if i + 1 < len(numbers):
                    tokens.append((numbers[i], numbers[i + 1]))
        return tokens
