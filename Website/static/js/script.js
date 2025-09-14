/**
 * DecryptionToolkeet Web Application JavaScript
 *
 * Handles all client-side interactions, API calls, and UI updates
 * for the decryption toolkit web interface.
 */

// Landing page functions
function showApp() {
    document.getElementById('landing-page').classList.add('page-hidden');
    document.getElementById('main-app').classList.remove('page-hidden');
    document.getElementById('main-app').classList.add('page-visible');
}

function showLanding() {
    document.getElementById('main-app').classList.add('page-hidden');
    document.getElementById('main-app').classList.remove('page-visible');
    document.getElementById('landing-page').classList.remove('page-hidden');
}

class DecryptionToolkit {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.loadDecoders();
    }

    initializeElements() {
        // Input elements
        this.inputText = document.getElementById('input-text');
        this.decoderSelect = document.getElementById('decoder-select');
        this.thresholdSlider = document.getElementById('threshold-slider');
        this.thresholdValue = document.getElementById('threshold-value');

        // Buttons
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.decodeBtn = document.getElementById('decode-btn');

        // Result sections
        this.loadingDiv = document.getElementById('loading');
        this.analysisSection = document.getElementById('analysis-section');
        this.resultsSection = document.getElementById('results-section');
        this.errorMessage = document.getElementById('error-message');

        // Analysis elements
        this.analysisLength = document.getElementById('analysis-length');
        this.analysisCharset = document.getElementById('analysis-charset');
        this.analysisEntropy = document.getElementById('analysis-entropy');
        this.analysisPatterns = document.getElementById('analysis-patterns');
        this.detectionsList = document.getElementById('detections-list');

        // Results elements
        this.resultsList = document.getElementById('results-list');
        this.errorText = document.getElementById('error-text');
    }

    bindEvents() {
        // Threshold slider
        this.thresholdSlider.addEventListener('input', (e) => {
            this.thresholdValue.textContent = e.target.value;
        });

        // Buttons
        this.analyzeBtn.addEventListener('click', () => this.analyzeText());
        this.decodeBtn.addEventListener('click', () => this.decodeText());

        // Enter key support
        this.inputText.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.decodeText();
            }
        });

        // Auto-resize textarea
        this.inputText.addEventListener('input', () => {
            this.inputText.style.height = 'auto';
            this.inputText.style.height = Math.max(120, this.inputText.scrollHeight) + 'px';
        });
    }

    async loadDecoders() {
        try {
            const response = await fetch('/api/decoders');
            const data = await response.json();

            if (data.decoders) {
                this.populateDecoderSelect(data.decoders);
            }
        } catch (error) {
            console.error('Failed to load decoders:', error);
        }
    }

    populateDecoderSelect(decoders) {
        // Clear existing options except the first one (Auto-detect)
        while (this.decoderSelect.children.length > 1) {
            this.decoderSelect.removeChild(this.decoderSelect.lastChild);
        }

        // Add decoder options
        decoders.forEach(decoder => {
            const option = document.createElement('option');
            option.value = decoder.id;
            option.textContent = decoder.name;
            option.title = decoder.description;
            this.decoderSelect.appendChild(option);
        });
    }

    async analyzeText() {
        const text = this.inputText.value.trim();

        if (!text) {
            this.showError('Please enter some text to analyze.');
            return;
        }

        this.showLoading();
        this.hideError();

        // Add 1-second delay for better UX
        await new Promise(resolve => setTimeout(resolve, 1000));

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    threshold: parseFloat(this.thresholdSlider.value)
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed.');
            }

            this.displayAnalysis(data);

        } catch (error) {
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    async decodeText() {
        const text = this.inputText.value.trim();

        if (!text) {
            this.showError('Please enter some text to decode.');
            return;
        }

        this.showLoading();
        this.hideError();

        // Add 1-second delay for better UX
        await new Promise(resolve => setTimeout(resolve, 1000));

        try {
            const forceDecoder = this.decoderSelect.value || null;

            const response = await fetch('/api/decode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    force_decoder: forceDecoder,
                    threshold: parseFloat(this.thresholdSlider.value)
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Decoding failed.');
            }

            this.displayResults(data.results);

        } catch (error) {
            this.showError(`Decoding failed: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayAnalysis(data) {
        const { analysis, detections } = data;

        // Update analysis data
        this.analysisLength.textContent = analysis.length;
        this.analysisCharset.textContent = analysis.characters.join(', ') || 'None';
        this.analysisEntropy.textContent = analysis.entropy;
        this.analysisPatterns.textContent = analysis.patterns.join(', ') || 'None';

        // Update detections
        this.detectionsList.innerHTML = '';

        if (detections.length === 0) {
            this.detectionsList.innerHTML = '<p class="text-muted">No encodings detected above threshold</p>';
        } else {
            detections.forEach(detection => {
                const item = this.createDetectionItem(detection);
                this.detectionsList.appendChild(item);
            });
        }

        this.showAnalysis();
    }

    createDetectionItem(detection) {
        const item = document.createElement('div');
        item.className = 'detection-item';

        const confidencePercentage = Math.round(detection.confidence * 100);

        item.innerHTML = `
            <div class="detection-info">
                <h4>${this.escapeHtml(detection.name)}</h4>
                <p>${this.escapeHtml(detection.description)}</p>
            </div>
            <span class="confidence-badge">${confidencePercentage}%</span>
        `;

        return item;
    }

    displayResults(results) {
        this.resultsList.innerHTML = '';

        if (results.length === 0) {
            this.resultsList.innerHTML = '<p class="text-muted">No results found</p>';
        } else {
            results.forEach((result, index) => {
                const item = this.createResultItem(result, index);
                this.resultsList.appendChild(item);
            });
        }

        this.showResults();
    }

    createResultItem(result, index) {
        const item = document.createElement('div');
        item.className = `result-item ${result.success ? '' : 'error'}`;

        const confidencePercentage = Math.round(result.confidence * 100);

        if (result.success) {
            item.innerHTML = `
                <div class="result-header">
                    <span class="result-decoder">${this.escapeHtml(result.decoder)}</span>
                    <span class="result-confidence">${confidencePercentage}%</span>
                </div>
                <div class="result-content">
                    <div class="result-text">${this.escapeHtml(result.result)}</div>
                    <button class="btn btn-secondary copy-btn" onclick="app.copyResult(${index})">
                        Copy
                    </button>
                </div>
            `;
        } else {
            item.innerHTML = `
                <div class="result-header">
                    <span class="result-decoder">${this.escapeHtml(result.decoder)}</span>
                    <span class="result-confidence error">${confidencePercentage}%</span>
                </div>
                <div class="result-content">
                    <div class="result-error">Error: ${this.escapeHtml(result.error)}</div>
                </div>
            `;
        }

        return item;
    }

    async copyResult(index) {
        const resultItems = document.querySelectorAll('.result-item');
        const resultText = resultItems[index].querySelector('.result-text');

        if (!resultText) return;

        try {
            await navigator.clipboard.writeText(resultText.textContent);

            const copyBtn = resultItems[index].querySelector('.copy-btn');
            const originalText = copyBtn.innerHTML;

            copyBtn.innerHTML = 'Copied!';
            copyBtn.classList.add('copied');            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('copied');
            }, 2000);

        } catch (error) {
            console.error('Failed to copy text:', error);
            this.showError('Failed to copy text to clipboard.');
        }
    }

    showLoading() {
        this.loadingDiv.classList.remove('hidden');
        this.analyzeBtn.disabled = true;
        this.decodeBtn.disabled = true;
    }

    hideLoading() {
        this.loadingDiv.classList.add('hidden');
        this.analyzeBtn.disabled = false;
        this.decodeBtn.disabled = false;
    }

    showAnalysis() {
        this.analysisSection.classList.remove('hidden');
        this.resultsSection.classList.add('hidden');
    }

    showResults() {
        this.resultsSection.classList.remove('hidden');
        this.analysisSection.classList.add('hidden');
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.errorMessage.classList.add('hidden');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Modal functions
function showHelp() {
    document.getElementById('help-modal').classList.remove('hidden');
}

function showAbout() {
    document.getElementById('about-modal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.add('hidden');
    }
});

// Close modals with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal:not(.hidden)');
        modals.forEach(modal => modal.classList.add('hidden'));
    }
});

// Initialize the application when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new DecryptionToolkit();
    console.log('🔓 DecryptionToolkeet Web App initialized.');
});

// Service Worker registration for PWA support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
