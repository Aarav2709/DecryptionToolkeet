#!/usr/bin/env python3
"""
Decryption Toolkit Web Application

A Flask web application that provides a sleek interface for the
Decryption Toolkit functionality.

Author: Aarav Gupta
Version: 1.0.0
"""

import sys
import os
import traceback
import logging
from flask import Flask, render_template, request, jsonify
from typing import List, Dict, Any

# Import from local Website directories (copied from Python folder)
try:
    from utils.detector import AutoDetector
    from utils.formatter import OutputFormatter
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you have copied the decoder and utils files to the Website folder")
    sys.exit(1)

# Make static folder explicit so static files are served correctly
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize the decryption components safely
detector = None
decoders = []
decoder_map = {}
try:
    detector = AutoDetector()
    formatter = OutputFormatter(use_colors=False)  # Disable colors for web
    decoders = detector.decoders
    # Create decoder name mapping
    decoder_map = {decoder.name.lower(): decoder for decoder in decoders}
except Exception as e:
    # Don't crash on import; return useful errors from endpoints instead
    print(f"Error initializing AutoDetector: {e}")
    traceback.print_exc()
    detector = None
    decoders = []
    decoder_map = {}

# Configure basic logging so Vercel shows tracebacks in logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.errorhandler(Exception)
def handle_exception(e):
    # Log full traceback for debugging in Vercel logs
    tb = traceback.format_exc()
    logger.error('Unhandled exception: %s', tb)
    # Return error and traceback (helpful for debugging deployment issues)
    return jsonify({'error': str(e), 'traceback': tb}), 500


@app.route('/')
def index():
    """Main page with the decryption interface."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_string():
    """Analyze a string and return possible encodings."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        if detector is None:
            return jsonify({'error': 'Service not available: detector failed to initialize'}), 503

        input_text = data['text'].strip()
        if not input_text:
            return jsonify({'error': 'Empty text provided'}), 400

        # Analyze the string
        analysis = detector.analyze_string(input_text)

        # Get detection results
        threshold = data.get('threshold', 0.5)
        detections = detector.detect(input_text, threshold)

        # Format detections for web response
        detection_results = []
        for name, confidence, decoder_obj in detections:
            detection_results.append({
                'name': name,
                'confidence': round(confidence, 3),
                'description': decoder_obj.description
            })

        return jsonify({
            'analysis': {
                'length': analysis['length'],
                'characters': analysis['characters'],
                'entropy': round(analysis['entropy'], 3),
                'patterns': analysis['patterns']
            },
            'detections': detection_results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/decode', methods=['POST'])
def decode_string():
    """Decode a string using auto-detection or forced decoder."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        if detector is None:
            return jsonify({'error': 'Service not available: detector failed to initialize'}), 503

        input_text = data['text'].strip()
        if not input_text:
            return jsonify({'error': 'Empty text provided'}), 400

        force_decoder = data.get('force_decoder', None)
        threshold = data.get('threshold', 0.5)

        results = []

        if force_decoder:
            # Force specific decoder
            decoder_type_lower = force_decoder.lower()
            if decoder_type_lower not in decoder_map:
                return jsonify({'error': f'Unknown decoder type: {force_decoder}'}), 400

            decoder_obj = decoder_map[decoder_type_lower]
            try:
                result = decoder_obj.decode(input_text)
                if isinstance(result, list):
                    for r in result:
                        results.append({
                            'decoder': decoder_obj.name,
                            'result': r,
                            'success': True,
                            'confidence': 1.0
                        })
                else:
                    results.append({
                        'decoder': decoder_obj.name,
                        'result': result,
                        'success': True,
                        'confidence': 1.0
                    })
            except Exception as e:
                results.append({
                    'decoder': decoder_obj.name,
                    'error': str(e),
                    'success': False,
                    'confidence': 0.0
                })
        else:
            # Auto-detect and decode
            detections = detector.detect(input_text, threshold)

            if not detections:
                return jsonify({'error': 'No encodings detected above threshold'}), 400

            # Try each detected encoding
            for name, confidence, decoder_obj in detections:
                try:
                    result = decoder_obj.decode(input_text)
                    if isinstance(result, list):
                        for r in result:
                            results.append({
                                'decoder': name,
                                'result': r,
                                'success': True,
                                'confidence': round(confidence, 3)
                            })
                    else:
                        results.append({
                            'decoder': name,
                            'result': result,
                            'success': True,
                            'confidence': round(confidence, 3)
                        })
                except Exception as e:
                    results.append({
                        'decoder': name,
                        'error': str(e),
                        'success': False,
                        'confidence': round(confidence, 3)
                    })

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/decoders', methods=['GET'])
def get_decoders():
    """Get list of all available decoders."""
    try:
        if detector is None:
            return jsonify({'error': 'Service not available: detector failed to initialize'}), 503

        decoder_list = []
        for decoder in decoders:
            decoder_list.append({
                'name': decoder.name,
                'description': decoder.description,
                'id': decoder.name.lower()
            })

        # Sort by name
        decoder_list.sort(key=lambda x: x['name'])

        return jsonify({'decoders': decoder_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'decoders_loaded': len(decoders)})


if __name__ == '__main__':
    # Check if we're running on Vercel or locally
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    print(f"🔓 Decryption Toolkit Web App starting on port {port}")
    print(f"📊 Loaded {len(decoders)} decoders")
    print(f"📁 Static folder: {app.static_folder} -> URL path: {app.static_url_path}")

    app.run(host='0.0.0.0', port=port, debug=debug)
