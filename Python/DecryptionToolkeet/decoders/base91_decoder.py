"""Base91 decoding module."""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class Base91Decoder(BaseDecoder):
    """Decoder for Base91 encoded strings."""

    name = "base91"
    description = "Decodes Base91 strings (high-density ASCII armoring)."

    _ALPHABET = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        "0123456789!#$%&()*+,./:;=?@[]^_`{|}~\"'"
    )
    _DECODE_TABLE = {ch: idx for idx, ch in enumerate(_ALPHABET)}

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        cleaned = data.strip()
        if not cleaned:
            return 0.0

        allowed_chars = sum(1 for ch in cleaned if ch in self._DECODE_TABLE or ch.isspace())
        ratio = allowed_chars / len(cleaned)
        if ratio < 0.85:
            return 0.0

        confidence = 0.6
        if len(cleaned) >= 16:
            confidence += 0.25
        elif len(cleaned) > 12:
            confidence += 0.15

        punctuation_ratio = sum(1 for ch in cleaned if not ch.isalnum()) / len(cleaned)
        if punctuation_ratio >= 0.15:
            confidence += 0.15
        elif punctuation_ratio >= 0.08:
            confidence += 0.08

        return min(confidence, 0.97)

    def decode(self, data: str) -> Union[str, List[str]]:
        cleaned = ''.join(ch for ch in data if not ch.isspace())
        if not cleaned:
            raise ValueError("No Base91 data provided")

        v = -1
        b = 0
        n = 0
        output = bytearray()

        for char in cleaned:
            if char not in self._DECODE_TABLE:
                raise ValueError(f"Invalid Base91 character: {char}")
            c = self._DECODE_TABLE[char]
            if v < 0:
                v = c
            else:
                v += c * 91
                b |= v << n
                if (v & 8191) > 88:
                    n += 13
                else:
                    n += 14
                while n >= 8:
                    output.append(b & 255)
                    b >>= 8
                    n -= 8
                v = -1

        if v >= 0:
            output.append((b | v << n) & 255)

        return self._decode_bytes(bytes(output))

    def _decode_bytes(self, payload: bytes) -> Union[str, List[str]]:
        if not payload:
            return ""

        for encoding in ("utf-8", "latin-1", "ascii", "cp1252"):
            try:
                decoded = payload.decode(encoding)
                if self.is_printable(decoded):
                    return decoded
            except UnicodeDecodeError:
                continue
        return payload.hex()
