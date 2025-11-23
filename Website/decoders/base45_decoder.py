"""Base45 decoding module."""

import re
from typing import Union, List
from .base_decoder import BaseDecoder


class Base45Decoder(BaseDecoder):
    """Decoder for Base45-encoded strings (RFC 9285 / EU DCC)."""

    name = "base45"
    description = "Decodes Base45 strings used in QR payloads like EU Digital Certificates."

    _ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
    _CHAR_MAP = {ch: idx for idx, ch in enumerate(_ALPHABET)}

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        cleaned = re.sub(r"\s+", "", data)
        if not cleaned:
            return 0.0

        if any(ch not in self._CHAR_MAP for ch in cleaned):
            return 0.0

        # Base45 strings never have length mod 3 == 1
        if len(cleaned) % 3 == 1:
            return 0.0

        confidence = 0.6
        if len(cleaned) >= 9:
            confidence += 0.25
        elif len(cleaned) >= 6:
            confidence += 0.15

        if len(cleaned) % 3 in (0, 2):
            confidence += 0.1

        if all(ch.isupper() or ch.isdigit() or ch in " $%*+-./:" for ch in cleaned):
            confidence += 0.1

        if '=' in cleaned:
            confidence -= 0.3

        return max(0.0, min(confidence, 0.98))

    def decode(self, data: str) -> Union[str, List[str]]:
        cleaned = re.sub(r"\s+", "", data)
        if not cleaned:
            raise ValueError("No Base45 data provided")

        values = []
        for ch in cleaned:
            if ch not in self._CHAR_MAP:
                raise ValueError(f"Invalid Base45 character: {ch}")
            values.append(self._CHAR_MAP[ch])

        output = bytearray()
        i = 0
        length = len(values)

        while i < length:
            if i + 2 < length:
                x = values[i] + values[i + 1] * 45 + values[i + 2] * 45 * 45
                if x > 0xFFFF:
                    raise ValueError("Invalid Base45 triplet")
                output.append(x // 256)
                output.append(x % 256)
                i += 3
            else:
                if i + 1 >= length:
                    raise ValueError("Dangling Base45 value")
                x = values[i] + values[i + 1] * 45
                if x > 0xFF:
                    raise ValueError("Invalid Base45 pair")
                output.append(x)
                i += 2

        return self._decode_bytes(output)

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
