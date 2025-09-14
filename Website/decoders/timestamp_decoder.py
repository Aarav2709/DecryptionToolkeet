"""
Timestamp decoding module for epoch timestamps.
"""

import re
from datetime import datetime, timezone
from typing import Union, List
from .base_decoder import BaseDecoder


class TimestampDecoder(BaseDecoder):
    """Decoder for various timestamp formats."""
    
    def __init__(self):
        super().__init__()
        self.description = "Converts epoch timestamps to human-readable dates."
    
    def can_decode(self, data: str) -> float:
        """Check if data looks like a timestamp."""
        if not data:
            return 0.0
        
        # Remove whitespace
        cleaned = data.strip()
        
        # Check for Unix timestamp (10 digits for seconds, 13 for milliseconds)
        if re.match(r'^\d{10}$', cleaned):
            # Unix timestamp in seconds
            try:
                timestamp = int(cleaned)
                # Check if it's a reasonable timestamp (between 1970 and 2050)
                if 0 <= timestamp <= 2524608000:  # Jan 1, 2050
                    return 0.95
            except ValueError:
                pass
        
        if re.match(r'^\d{13}$', cleaned):
            # Unix timestamp in milliseconds
            try:
                timestamp = int(cleaned) // 1000
                if 0 <= timestamp <= 2524608000:
                    return 0.95
            except ValueError:
                pass
        
        # Check for other timestamp patterns
        if re.match(r'^\d{16}$', cleaned):
            # Microseconds
            return 0.7
        
        if re.match(r'^\d{19}$', cleaned):
            # Nanoseconds
            return 0.7
        
        # Check for hex timestamps
        if re.match(r'^[0-9a-fA-F]{8}$', cleaned):
            try:
                timestamp = int(cleaned, 16)
                if 0 <= timestamp <= 2524608000:
                    return 0.8
            except ValueError:
                pass
        
        return 0.0
    
    def decode(self, data: str) -> Union[str, List[str]]:
        """Decode timestamp to human-readable format."""
        results = []
        cleaned = data.strip()
        
        try:
            # Try Unix timestamp in seconds (10 digits)
            if re.match(r'^\d{10}$', cleaned):
                timestamp = int(cleaned)
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                results.append(f"Unix seconds: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                # Also show local time
                dt_local = datetime.fromtimestamp(timestamp)
                results.append(f"Unix seconds (local): {dt_local.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Try Unix timestamp in milliseconds (13 digits)
            elif re.match(r'^\d{13}$', cleaned):
                timestamp = int(cleaned) / 1000
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                results.append(f"Unix milliseconds: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC")
                
                dt_local = datetime.fromtimestamp(timestamp)
                results.append(f"Unix milliseconds (local): {dt_local.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            
            # Try Unix timestamp in microseconds (16 digits)
            elif re.match(r'^\d{16}$', cleaned):
                timestamp = int(cleaned) / 1000000
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                results.append(f"Unix microseconds: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')} UTC")
            
            # Try Unix timestamp in nanoseconds (19 digits)
            elif re.match(r'^\d{19}$', cleaned):
                timestamp = int(cleaned) / 1000000000
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                results.append(f"Unix nanoseconds: {dt.strftime('%Y-%m-%d %H:%M:%S.%f')} UTC")
            
            # Try hex timestamp
            elif re.match(r'^[0-9a-fA-F]{8}$', cleaned):
                timestamp = int(cleaned, 16)
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                results.append(f"Hex timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Try as a general number that might be a timestamp
            else:
                try:
                    # Try interpreting as seconds
                    timestamp = float(cleaned)
                    if 0 <= timestamp <= 2524608000:
                        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        results.append(f"As seconds: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    
                    # Try interpreting as milliseconds
                    if timestamp > 1000000000000:  # Looks like milliseconds
                        timestamp_ms = timestamp / 1000
                        if 0 <= timestamp_ms <= 2524608000:
                            dt = datetime.fromtimestamp(timestamp_ms, tz=timezone.utc)
                            results.append(f"As milliseconds: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                except ValueError:
                    pass
            
        except Exception as e:
            raise ValueError(f"Failed to decode timestamp: {str(e)}")
        
        return results if results else ["Could not decode as timestamp"]
    
    def encode(self, date_str: str = None) -> str:
        """Encode current time or given date to Unix timestamp."""
        if date_str:
            # Try to parse the date string
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return str(int(dt.timestamp()))
            except:
                raise ValueError(f"Could not parse date: {date_str}")
        else:
            # Return current timestamp
            return str(int(datetime.now().timestamp()))
