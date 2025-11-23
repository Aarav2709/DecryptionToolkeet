"""DNA sequence decoding module."""

from typing import Union, List
from .base_decoder import BaseDecoder


class DNADecoder(BaseDecoder):
    """Decoder for DNA-style encodings (A/C/G/T mapping to 2-bit pairs)."""

    name = "dna"
    description = "Decodes DNA strings (A,C,G,T) by mapping 2-bit pairs back to bytes."

    _MAP = {
        'A': '00',
        'C': '01',
        'G': '10',
        'T': '11',
    }

    def can_decode(self, data: str) -> float:
        if not data:
            return 0.0
        letters = ''.join(ch for ch in data.upper() if ch in self._MAP)
        if not letters:
            return 0.0
        ratio = len(letters) / len(data.replace('\n', '').replace('\r', ''))
        if ratio < 0.9:
            return 0.0
        if len(letters) % 4 != 0:
            return 0.2
        return 0.75

    def decode(self, data: str) -> Union[str, List[str]]:
        letters = ''.join(ch for ch in data.upper() if ch in self._MAP)
        if len(letters) % 4 != 0:
            raise ValueError("DNA data length must be a multiple of 4 bases")

        bitstring = ''.join(self._MAP[ch] for ch in letters)
        bytes_out = bytearray()
        for i in range(0, len(bitstring), 8):
            byte = bitstring[i:i + 8]
            if len(byte) < 8:
                break
            bytes_out.append(int(byte, 2))

        if not bytes_out:
            return ""

        for encoding in ("utf-8", "latin-1", "ascii", "cp1252"):
            try:
                decoded = bytes_out.decode(encoding)
                if self.is_printable(decoded):
                    return decoded
            except UnicodeDecodeError:
                continue
        return bytes_out.hex()
