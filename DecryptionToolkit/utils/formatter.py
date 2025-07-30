from typing import List, Dict, Any, Union
import textwrap


class OutputFormatter:
    
    def __init__(self, width: int = 80, use_colors: bool = True):
        self.width = width
        self.use_colors = use_colors
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'underline': '\033[4m',
            'blink': '\033[5m',
            'reverse': '\033[7m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bg_red': '\033[101m',
            'bg_green': '\033[102m',
            'bg_yellow': '\033[103m',
            'bg_blue': '\033[104m',
            'bg_magenta': '\033[105m',
            'bg_cyan': '\033[106m'
        }
    
    def format_detection_results(self, results: List[tuple], data: str) -> str:
        output = []
        
        # Enhanced header with gradient effect
        header = "🔍 AUTO-DETECTION RESULTS"
        output.append(self._colored(header, 'bold', 'bg_cyan', 'white'))
        output.append(self._colored("=" * 60, 'cyan', 'bold'))
        
        # Input info with better formatting
        truncated_input = self._truncate_string(data, 50)
        output.append(f"{self._colored('📥 Input:', 'bold', 'blue')} {self._colored(truncated_input, 'white')}")
        output.append(f"{self._colored('📏 Length:', 'bold', 'blue')} {self._colored(str(len(data)), 'yellow')} characters")
        
        # Add entropy and complexity info
        entropy = self._calculate_entropy(data)
        complexity = self._assess_complexity(data)
        output.append(f"{self._colored('📊 Entropy:', 'bold', 'blue')} {self._colored(f'{entropy:.2f}', 'yellow')} bits")
        output.append(f"{self._colored('⚡ Complexity:', 'bold', 'blue')} {self._colored(complexity, 'yellow')}")
        output.append("")
        
        if not results:
            output.append(self._colored("❌ No encodings detected!", 'red', 'bold'))
            return "\n".join(output)
        
        output.append(self._colored("🎯 Possible encodings (sorted by confidence):", 'bold', 'magenta'))
        output.append("")
        
        for i, (name, confidence, decoder) in enumerate(results, 1):
            confidence_color = self._get_confidence_color(confidence)
            
            # Enhanced confidence display with progress bar
            conf_percent = f"{confidence:.1%}"
            progress_bar = self._create_progress_bar(confidence)
            
            # Decoder name with icon
            icon = self._get_decoder_icon(name)
            decoder_line = f"{self._colored(f'{i:2d}.', 'bold', 'white')} {icon} {self._colored(name, 'bold', confidence_color)} "
            decoder_line += f"({self._colored(conf_percent, confidence_color, 'bold')})"
            
            output.append(decoder_line)
            output.append(f"    {progress_bar}")
            output.append(f"    {self._colored(decoder.description, 'dim')}")
            output.append("")
        
        return "\n".join(output)
    
    def format_decode_result(self, decoder_name: str, result: Union[str, List[str]], 
                           success: bool = True, error: str = None) -> str:
        output = []
        
        # Enhanced success/failure display
        icon = self._get_decoder_icon(decoder_name)
        if success:
            status_line = f"{icon} {self._colored(decoder_name.upper(), 'bold', 'green')} {self._colored('DECODING SUCCESS!', 'bold', 'bg_green', 'white')}"
        else:
            status_line = f"{icon} {self._colored(decoder_name.upper(), 'bold', 'red')} {self._colored('DECODING FAILED!', 'bold', 'bg_red', 'white')}"
        
        output.append(status_line)
        output.append(self._colored("─" * 50, 'cyan'))
        
        if error:
            output.append(f"{self._colored('❌ Error:', 'red', 'bold')} {self._colored(error, 'red')}")
        elif isinstance(result, list):
            if len(result) == 1:
                output.append(f"{self._colored('📤 Result:', 'bold', 'blue')} {self._colored(result[0], 'white', 'bold')}")
            else:
                output.append(f"{self._colored('📤 Multiple results:', 'bold', 'blue')}")
                for i, res in enumerate(result, 1):
                    output.append(f"{self._colored(f'{i:2d}.', 'bold', 'yellow')} {self._colored(res, 'white')}")
        else:
            output.append(f"{self._colored('📤 Result:', 'bold', 'blue')} {self._colored(result, 'white', 'bold')}")
        
        output.append("")
        return "\n".join(output)
    
    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        output = []
        
        output.append(self._colored("STRING ANALYSIS", 'bold', 'magenta'))
        output.append("=" * 40)
        output.append(f"Length: {analysis['length']} characters")
        output.append(f"Unique characters: {analysis['unique_chars']}")
        output.append(f"Entropy: {analysis['entropy']:.2f} bits")
        output.append("")
        
        output.append("Character distribution:")
        dist = analysis['char_distribution']
        total = sum(dist.values())
        for char_type, count in dist.items():
            if count > 0:
                percentage = (count / total) * 100
                output.append(f"  {char_type:12s}: {count:4d} ({percentage:5.1f}%)")
        output.append("")
        
        if analysis['patterns']:
            output.append("Detected patterns:")
            for pattern in analysis['patterns']:
                output.append(f"  • {pattern}")
            output.append("")
        
        if analysis['possible_encodings']:
            output.append("Possible encodings:")
            for encoding in analysis['possible_encodings']:
                conf_color = self._get_confidence_color(encoding['confidence'])
                confidence_str = f"{encoding['confidence']:.1%}"
                output.append(f"  • {encoding['name']} "
                             f"({self._colored(confidence_str, conf_color)})")
        
        return "\n".join(output)
    
    def format_help(self) -> str:
        output = []
        
        output.append(self._colored("DECRYPTION TOOLKIT HELP", 'bold', 'yellow'))
        output.append("=" * 50)
        output.append("")
        
        output.append("USAGE:")
        output.append("  python main.py [options] <input_string>")
        output.append("")
        
        output.append("OPTIONS:")
        output.append("  -a, --auto        Auto-detect encoding/cipher (default)")
        output.append("  -f, --force TYPE  Force specific decoder type")
        output.append("  -l, --list        List all available decoders")
        output.append("  -v, --verbose     Show detailed analysis")
        output.append("  -q, --quiet       Minimal output")
        output.append("  --analyze         Show string analysis only")
        output.append("  -h, --help        Show this help")
        output.append("")
        
        output.append("EXAMPLES:")
        output.append("  python main.py 'SGVsbG8gV29ybGQ='")
        output.append("  python main.py --force base64 'SGVsbG8gV29ybGQ='")
        output.append("  python main.py --analyze 'mysterious_string'")
        output.append("")
        
        return "\n".join(output)
    
    def format_decoder_list(self, decoders: List[Any]) -> str:
        output = []
        
        output.append(self._colored("AVAILABLE DECODERS", 'bold', 'blue'))
        output.append("=" * 50)
        output.append("")
        
        for decoder in decoders:
            output.append(f"{self._colored(decoder.name, 'bold')}")
            wrapped_desc = textwrap.fill(decoder.description, 
                                       width=self.width-4, 
                                       initial_indent="  ", 
                                       subsequent_indent="  ")
            output.append(wrapped_desc)
            output.append("")
        
        return "\n".join(output)
    
    def _colored(self, text, *styles):
        if not self.use_colors:
            return text
        
        codes = {
            'red': '\033[91m',
            'green': '\033[92m', 
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'underline': '\033[4m',
            'blink': '\033[5m',
            'reverse': '\033[7m',
            'bg_red': '\033[101m',
            'bg_green': '\033[102m',
            'bg_yellow': '\033[103m',
            'bg_blue': '\033[104m',
            'bg_magenta': '\033[105m',
            'bg_cyan': '\033[106m',
            'reset': '\033[0m'
        }
        
        result = text
        for style in styles:
            if style in codes:
                result = codes[style] + result
        
        return result + codes.get('reset', '')
    
    def _get_confidence_color(self, confidence: float) -> str:
        if confidence >= 0.8:
            return 'green'
        elif confidence >= 0.5:
            return 'yellow'
        else:
            return 'red'
    
    def _truncate_string(self, text: str, max_length: int) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of the text."""
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in char_counts.values():
            probability = count / length
            if probability > 0:
                import math
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _assess_complexity(self, text: str) -> str:
        """Assess the complexity level of the text."""
        if not text:
            return "Empty"
        
        unique_chars = len(set(text))
        total_chars = len(text)
        
        if unique_chars == 1:
            return "Trivial"
        elif unique_chars / total_chars > 0.8:
            return "Very High"
        elif unique_chars / total_chars > 0.6:
            return "High"
        elif unique_chars / total_chars > 0.4:
            return "Medium"
        elif unique_chars / total_chars > 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def _create_progress_bar(self, confidence: float, width: int = 20) -> str:
        """Create a visual progress bar for confidence."""
        filled = int(confidence * width)
        empty = width - filled
        
        bar_color = self._get_confidence_color(confidence)
        filled_bar = self._colored("█" * filled, bar_color)
        empty_bar = self._colored("░" * empty, 'dim')
        
        return f"[{filled_bar}{empty_bar}]"
    
    def _get_decoder_icon(self, decoder_name: str) -> str:
        """Get an appropriate icon for each decoder type."""
        icons = {
            'base64': '📦', 'base32': '📦', 'base85': '📦',
            'hex': '🔢', 'binary': '💻', 'ascii': '🔤',
            'url': '🌐', 'html': '🌐',
            'caesar': '🏛️', 'rot13': '🔄', 'atbash': '🔀',
            'vigenere': '🗝️', 'xor': '⚡', 'affine': '📐',
            'morse': '📡', 'baconian': '🥓', 'unicode': '🌍',
            'timestamp': '⏰', 'railfence': '🚂', 'columnar': '📊',
            'playfair': '🎲', 'polybius': '⚏'
        }
        
        return icons.get(decoder_name.lower(), '🔍')
    
    def _colored(self, text, *styles):
        """Apply color/style to text if colors are enabled."""
        if not self.use_colors:
            return text
        
        codes = {
            'red': '\033[91m',
            'green': '\033[92m', 
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
        
        result = text
        for style in styles:
            if style in codes:
                result = codes[style] + result
        
        return result + codes.get('reset', '')
    
    def _get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence level."""
        if confidence >= 0.8:
            return 'green'
        elif confidence >= 0.5:
            return 'yellow'
        else:
            return 'red'
    
    def _truncate_string(self, text: str, max_length: int) -> str:
        """Truncate string with ellipsis if too long."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."