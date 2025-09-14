"""
Auto-detection utilities for determining the most likely encoding/cipher type.
"""

from typing import List, Tuple, Dict
import sys
import os

# Add parent directory to path to import decoders
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decoders import *


class AutoDetector:
    """Automatically detects the most likely encoding or cipher type."""

    def __init__(self):
        # Initialize all decoders
        self.decoders = [
            Base64Decoder(),
            Base32Decoder(),
            Base85Decoder(),
            HexDecoder(),
            BinaryDecoder(),
            AsciiDecoder(),
            URLDecoder(),
            HTMLDecoder(),
            CaesarDecoder(),
            ROT13Decoder(),
            AtbashDecoder(),
            VigenereDecoder(),
            XORDecoder(),
            MorseDecoder(),
            BaconianDecoder(),
            AffineDecoder(),
            UnicodeDecoder(),
            TimestampDecoder(),
            RailFenceDecoder(),
            ColumnarDecoder(),
            PlayfairDecoder(),
            PolybusDecoder(),
            FourSquareDecoder(),
            TwoSquareDecoder(),
            TrifidDecoder(),
            BifidDecoder(),
            GromarkDecoder(),
            BeaufortDecoder(),
            PhillipsDecoder(),
            NihilistDecoder(),
            UUDecoder(),
            XXDecoder()
        ]

    def detect(self, data: str, threshold: float = 0.5) -> List[Tuple[str, float, BaseDecoder]]:
        """
        Detect possible encodings/ciphers for the given data.

        Args:
            data: The string to analyze
            threshold: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            List of tuples (decoder_name, confidence, decoder_instance) sorted by confidence
        """
        results = []

        for decoder in self.decoders:
            try:
                confidence = decoder.can_decode(data)
                if confidence >= threshold:
                    results.append((decoder.name, confidence, decoder))
            except Exception:
                # Skip decoders that fail during detection
                continue

        # Sort by confidence (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def get_best_match(self, data: str) -> Tuple[str, float, BaseDecoder]:
        """
        Get the single best matching decoder.

        Args:
            data: The string to analyze

        Returns:
            Tuple of (decoder_name, confidence, decoder_instance) or (None, 0.0, None)
        """
        matches = self.detect(data, threshold=0.0)
        return matches[0] if matches else (None, 0.0, None)

    def analyze_string(self, data: str) -> Dict[str, any]:
        """
        Perform comprehensive analysis of a string.

        Args:
            data: The string to analyze

        Returns:
            Dictionary with analysis results
        """
        analysis = {
            'length': len(data),
            'unique_chars': len(set(data)),
            'entropy': self._calculate_entropy(data),
            'char_distribution': self._get_char_distribution(data),
            'patterns': self._detect_patterns(data),
            'possible_encodings': []
        }

        # Get all possible decoders with confidence > 0
        matches = self.detect(data, threshold=0.1)
        for name, confidence, decoder in matches:
            analysis['possible_encodings'].append({
                'name': name,
                'confidence': confidence,
                'description': decoder.description
            })

        return analysis

    def _calculate_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of the string."""
        if not data:
            return 0.0

        from collections import Counter
        import math

        counts = Counter(data)
        length = len(data)

        entropy = 0.0
        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _get_char_distribution(self, data: str) -> Dict[str, int]:
        """Get character type distribution."""
        distribution = {
            'letters': 0,
            'digits': 0,
            'spaces': 0,
            'punctuation': 0,
            'symbols': 0,
            'control': 0
        }

        for char in data:
            if char.isalpha():
                distribution['letters'] += 1
            elif char.isdigit():
                distribution['digits'] += 1
            elif char.isspace():
                distribution['spaces'] += 1
            elif char in '.,;:!?':
                distribution['punctuation'] += 1
            elif char.isprintable():
                distribution['symbols'] += 1
            else:
                distribution['control'] += 1

        return distribution

    def _detect_patterns(self, data: str) -> List[str]:
        """Detect common patterns in the string."""
        patterns = []

        import re

        # Check for common encoding patterns
        if re.search(r'[A-Za-z0-9+/]+=*$', data):
            patterns.append('Base64-like')

        if re.search(r'^[A-Z2-7]+=*$', data):
            patterns.append('Base32-like')

        if re.search(r'^[0-9a-fA-F]+$', data):
            patterns.append('Hexadecimal')

        if re.search(r'^[01]+$', data):
            patterns.append('Binary')

        if re.search(r'%[0-9a-fA-F]{2}', data):
            patterns.append('URL-encoded')

        if re.search(r'&[a-zA-Z]+;', data):
            patterns.append('HTML-entities')

        if re.search(r'^[.\-\s]+$', data):
            patterns.append('Morse-like')

        if re.search(r'^[AB\s]+$', data) and len(data) % 5 == 0:
            patterns.append('Baconian-like')

        if re.search(r'^\d{10,19}$', data):
            patterns.append('Timestamp-like')

        return patterns
