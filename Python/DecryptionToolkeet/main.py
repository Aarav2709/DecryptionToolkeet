#!/usr/bin/env python3
"""
Decryption Toolkit - A comprehensive tool for decoding and decrypting strings.

A modular, high-performance Python CLI tool that can automatically decode or decrypt
strings using a wide range of classic ciphers, encodings, and techniques.

Author: Aarav Gupta
Version: 1.0.0
"""

import sys
import argparse
from typing import List, Optional

from decoders import *
from utils import AutoDetector, OutputFormatter


class DecryptionToolkit:
    """Main application class for the Decryption Toolkit."""
    
    def __init__(self):
        self.detector = AutoDetector()
        self.formatter = OutputFormatter(use_colors=True)  # Enable colors
        self.decoders = self.detector.decoders
        
        # Create decoder name mapping for forced decoding
        self.decoder_map = {decoder.name.lower(): decoder for decoder in self.decoders}
    
    def run(self, args: List[str] = None) -> int:
        """Run the application with given arguments."""
        if args is None:
            args = sys.argv[1:]
        
        try:
            parsed_args = self._parse_arguments(args)
            return self._execute_command(parsed_args)
        except KeyboardInterrupt:
            print("\\n⚠️  Operation cancelled by user")
            return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def _parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="Decryption Toolkit - Decode and decrypt strings automatically",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s 'SGVsbG8gV29ybGQ='
  %(prog)s --force base64 'SGVsbG8gV29ybGQ='
  %(prog)s --analyze 'mysterious_string'
  %(prog)s --list
            """
        )
        
        parser.add_argument(
            'input_string',
            nargs='?',
            help='String to decode/decrypt'
        )
        
        parser.add_argument(
            '-i', '--input',
            action='store_true',
            help='Run in input mode (prompt for text)'
        )
        
        parser.add_argument(
            '-a', '--auto',
            action='store_true',
            default=True,
            help='Auto-detect encoding/cipher (default)'
        )
        
        parser.add_argument(
            '-f', '--force',
            metavar='TYPE',
            help='Force specific decoder type'
        )
        
        parser.add_argument(
            '-l', '--list',
            action='store_true',
            help='List all available decoders'
        )
        
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Show string analysis only'
        )
        
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Show detailed analysis and all attempts'
        )
        
        parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='Minimal output (results only)'
        )
        
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.5,
            metavar='FLOAT',
            help='Confidence threshold for auto-detection (0.0-1.0, default: 0.5)'
        )
        
        parser.add_argument(
            '--no-color',
            action='store_true',
            help='Disable colored output'
        )
        
        return parser.parse_args(args)
    
    def _execute_command(self, args: argparse.Namespace) -> int:
        """Execute the parsed command."""
        # Disable colors if requested or if not in a terminal
        if args.no_color or not sys.stdout.isatty():
            self.formatter.use_colors = False
        
        # Handle input mode
        if args.input:
            return self._run_input_mode(args)
        
        # Handle list command
        if args.list:
            print(self.formatter.format_decoder_list(self.decoders))
            return 0
        
        # Require input string for other commands
        if not args.input_string:
            print("❌ Error: Input string is required")
            print("Use -i or --input for input mode")
            print("Use --help for usage information")
            return 1
        
        input_data = args.input_string
        
        # Handle analyze command
        if args.analyze:
            analysis = self.detector.analyze_string(input_data)
            print(self.formatter.format_analysis(analysis))
            return 0
        
        # Handle forced decoding
        if args.force:
            return self._force_decode(input_data, args.force, args.quiet)
        
        # Handle auto-detection and decoding
        return self._auto_decode(input_data, args.threshold, args.verbose, args.quiet)
    
    def _force_decode(self, data: str, decoder_type: str, quiet: bool) -> int:
        """Force decode with specific decoder type."""
        decoder_type_lower = decoder_type.lower()
        
        if decoder_type_lower not in self.decoder_map:
            available = ', '.join(sorted(self.decoder_map.keys()))
            print(f"❌ Unknown decoder type: {decoder_type}")
            print(f"Available types: {available}")
            return 1
        
        decoder = self.decoder_map[decoder_type_lower]
        
        try:
            result = decoder.decode(data)
            if not quiet:
                print(self.formatter.format_decode_result(decoder.name, result, True))
            else:
                if isinstance(result, list):
                    for r in result:
                        print(r)
                else:
                    print(result)
            return 0
        except Exception as e:
            if not quiet:
                print(self.formatter.format_decode_result(decoder.name, None, False, str(e)))
            else:
                print(f"Error: {e}")
            return 1
    
    def _auto_decode(self, data: str, threshold: float, verbose: bool, quiet: bool) -> int:
        """Auto-detect and decode data."""
        # Detect possible encodings
        detections = self.detector.detect(data, threshold)
        
        if not detections:
            if not quiet:
                print("❌ No encodings detected above threshold")
                if verbose:
                    # Show analysis anyway
                    analysis = self.detector.analyze_string(data)
                    print(self.formatter.format_analysis(analysis))
            return 1
        
        if verbose and not quiet:
            print(self.formatter.format_detection_results(detections, data))
        
        success_count = 0
        
        # Try each detected encoding
        for name, confidence, decoder in detections:
            try:
                result = decoder.decode(data)
                success_count += 1
                
                if not quiet:
                    print(self.formatter.format_decode_result(name, result, True))
                else:
                    # In quiet mode, just print the result
                    if isinstance(result, list):
                        for r in result:
                            print(f"{name}: {r}")
                    else:
                        print(f"{name}: {result}")
                
                # If not verbose, stop after first successful decode
                if not verbose:
                    break
                    
            except Exception as e:
                if verbose and not quiet:
                    print(self.formatter.format_decode_result(name, None, False, str(e)))
                continue
        
        return 0 if success_count > 0 else 1
    
    def _run_input_mode(self, args: argparse.Namespace) -> int:
        """Run in input mode - prompt for text to decode."""
        print(self.formatter._colored("🔓 DECRYPTION TOOLKIT - INPUT MODE", 'bold', 'cyan'))
        print("=" * 50)
        
        try:
            user_input = input("Enter text to decode: ").strip()
            
            if not user_input:
                print("❌ No input provided")
                return 1
            
            print()
            result = self._auto_decode(user_input, args.threshold, args.verbose, args.quiet)
            return result
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return 0
        except EOFError:
            print("\n👋 Goodbye!")
            return 0


def main():
    """Main entry point."""
    toolkit = DecryptionToolkit()
    return toolkit.run()


if __name__ == '__main__':
    sys.exit(main())
