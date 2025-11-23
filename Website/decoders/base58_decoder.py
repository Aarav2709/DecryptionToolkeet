"""Base58 decoding module."""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class Base58Decoder(BaseDecoder):
    """Decoder for Base58 strings (Bitcoin-style alphabet)."""

    name = "base58"
    description = "Decodes Base58 strings used in Bitcoin, IPFS, and short IDs."

    _ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    _CHAR_MAP = {ch: idx for idx, ch in enumerate(_ALPHABET)}

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        cleaned = re.sub(r"\s+", "", data)
        if not cleaned:
            return 0.0

        if any(ch not in self._CHAR_MAP for ch in cleaned):
            return 0.0

        confidence = 0.55
        if len(cleaned) >= 16:
            confidence += 0.25
        elif len(cleaned) >= 10:
            confidence += 0.15

        if cleaned.startswith("1"):
            confidence += 0.05

        has_upper = any(ch.isupper() for ch in cleaned)
        has_lower = any(ch.islower() for ch in cleaned)
        has_digits = any(ch.isdigit() for ch in cleaned)
        if (has_upper and has_lower) or (has_lower and has_digits) or (has_upper and has_digits):
            confidence += 0.1

        return min(confidence, 0.97)

    def decode(self, data: str) -> Union[str, List[str]]:
        cleaned = re.sub(r"\s+", "", data)
        if not cleaned:
            raise ValueError("No Base58 data provided")

        num = 0
        for ch in cleaned:
            if ch not in self._CHAR_MAP:
                raise ValueError(f"Invalid Base58 character: {ch}")
            num = num * 58 + self._CHAR_MAP[ch]

        encoded_bytes = bytearray()
        while num > 0:
            num, remainder = divmod(num, 256)
            encoded_bytes.append(remainder)
        encoded_bytes.reverse()

        leading_zeroes = len(cleaned) - len(cleaned.lstrip('1'))
        result = b"\x00" * leading_zeroes + bytes(encoded_bytes)

        if not result:
            return ""

        return self._decode_bytes(result)

    def _decode_bytes(self, payload: bytes) -> Union[str, List[str]]:
        for encoding in ("utf-8", "latin-1", "ascii", "cp1252"):
            try:
                decoded = payload.decode(encoding)
                if self.is_printable(decoded):
                    return decoded
            except UnicodeDecodeError:
                continue
        return payload.hex()
