"""
Base decoder interface that all decoders must implement.
"""

from abc import ABC, abstractmethod
from typing import Union, List, Tuple, Optional


class BaseDecoder(ABC):
    """Base class for all decoders."""
    
    def __init__(self):
        # Use class attribute if defined, otherwise derive from class name
        if not hasattr(self.__class__, 'name') or self.__class__.name is None:
            self.name = self.__class__.__name__.replace('Decoder', '')
        else:
            self.name = self.__class__.name
            
        # Use class attribute if defined, otherwise empty
        if not hasattr(self.__class__, 'description') or self.__class__.description is None:
            self.description = ""
        else:
            self.description = self.__class__.description
    
    @abstractmethod
    def can_decode(self, data: str) -> float:
        """
        Check if this decoder can handle the given data.
        
        Args:
            data: The string to check
            
        Returns:
            Confidence score (0.0 to 1.0) that this decoder can handle the data
        """
        pass
    
    @abstractmethod
    def decode(self, data: str) -> Union[str, List[str]]:
        """
        Decode the given data.
        
        Args:
            data: The string to decode
            
        Returns:
            Decoded string(s). Can return a single string or list of possibilities.
        """
        pass
    
    def get_info(self) -> dict:
        """Get information about this decoder."""
        return {
            'name': self.name,
            'description': self.description,
            'class': self.__class__.__name__
        }
    
    def is_printable(self, text: str) -> bool:
        """Check if text contains mostly printable characters."""
        if not text:
            return False
        
        printable_count = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
        return printable_count / len(text) > 0.8
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
        
        from collections import Counter
        import math
        
        counts = Counter(text)
        length = len(text)
        
        entropy = 0.0
        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
