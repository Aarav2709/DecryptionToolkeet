"""Quoted-Printable decoding module."""

import quopri
import re
from typing import Union, List
from .base_decoder import BaseDecoder


class QuotedPrintableDecoder(BaseDecoder):
    """Decoder for MIME Quoted-Printable strings."""

    name = "quoted-printable"
    description = "Decodes MIME Quoted-Printable payloads (e.g., emails)."

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0

        if "=" not in data:
            return 0.0

        soft_breaks = data.count("=\n") + data.count("=\r\n")
        hex_sequences = len(re.findall(r"=[0-9A-Fa-f]{2}", data))
        if hex_sequences == 0 and soft_breaks == 0:
            return 0.0

        confidence = 0.5 + 0.1 * min(hex_sequences / 5, 3)
        confidence += 0.1 * min(soft_breaks, 2)
        return min(confidence, 0.9)

    def decode(self, data: str) -> Union[str, List[str]]:
        try:
            decoded_bytes = quopri.decodestring(data)
        except Exception as exc:
            raise ValueError(f"Failed to decode Quoted-Printable: {exc}")

        if not decoded_bytes:
            return ""

        for encoding in ("utf-8", "latin-1", "ascii", "cp1252"):
            try:
                decoded = decoded_bytes.decode(encoding)
                if self.is_printable(decoded):
                    return decoded
            except UnicodeDecodeError:
                continue
        return decoded_bytes.hex()
