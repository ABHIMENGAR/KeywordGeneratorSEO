#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import pandas as pd
import urllib.parse
import os
from io import BytesIO
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# For Vercel serverless, the file structure might be different
# Try to detect if we're running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1' or '/var/task' in BASE_DIR

# For Vercel, check multiple possible template locations
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'templates'),
    'templates',
    os.path.join(os.getcwd(), 'templates'),
    '/var/task/templates',  # Vercel serverless path
    os.path.join(BASE_DIR, '..', 'templates'),  # Parent directory
]

STATIC_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    'static',
    os.path.join(os.getcwd(), 'static'),
    '/var/task/static',  # Vercel serverless path
    os.path.join(BASE_DIR, '..', 'static'),  # Parent directory
]

# Find the first existing template directory
template_folder = None
for td in TEMPLATE_DIRS:
    if os.path.exists(td) and os.path.isdir(td):
        template_folder = td
        break

# If no template folder found, use relative path (Flask default)
if template_folder is None:
    template_folder = 'templates'

# Find the first existing static directory
static_folder = None
for sd in STATIC_DIRS:
    if os.path.exists(sd) and os.path.isdir(sd):
        static_folder = sd
        break

# If no static folder found, use relative path (Flask default)
if static_folder is None:
    static_folder = 'static'

# Configure Flask for Vercel deployment
app = Flask(
    __name__,
    template_folder=template_folder,
    static_folder=static_folder
)

def api_call(keyword):
    keywords = [keyword]
    url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + urllib.parse.quote(keyword)
    try:
        response = requests.get(url, verify=False, timeout=5)
        response.raise_for_status()
        suggestions = json.loads(response.text)
        if len(suggestions) > 1 and isinstance(suggestions[1], list):
            for word in suggestions[1]:
                keywords.append(word)
    except Exception as e:
        print(f"Error in api_call: {str(e)}")
        pass

    prefixes(keyword, keywords)
    suffixes(keyword, keywords)
    numbers(keyword, keywords)
    get_more(keyword, keywords)
    return clean_keywords(keywords, keyword)

def prefixes(keyword, keywords):
    prefixes_list = [
        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
        'u','v','w','x','y','z',
        'how','which','why','where','who','when','are','what'
    ]
    for prefix in prefixes_list:
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + urllib.parse.quote(prefix + " " + keyword)
        try:
            response = requests.get(url, verify=False, timeout=5)
            response.raise_for_status()
            suggestions = json.loads(response.text)
            if len(suggestions) > 1 and isinstance(suggestions[1], list):
                for kw in suggestions[1]:
                    keywords.append(kw)
        except Exception as e:
            print(f"Error in prefixes: {str(e)}")
            continue

def suffixes(keyword, keywords):
    suffixes_list = [
        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
        'u','v','w','x','y','z',
        'like','for','without','with','versus','vs','to','near','except','has'
    ]
    for suffix in suffixes_list:
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + urllib.parse.quote(keyword + " " + suffix)
        try:
            response = requests.get(url, verify=False, timeout=5)
            response.raise_for_status()
            suggestions = json.loads(response.text)
            if len(suggestions) > 1 and isinstance(suggestions[1], list):
                for kw in suggestions[1]:
                    keywords.append(kw)
        except Exception as e:
            print(f"Error in prefixes: {str(e)}")
            continue

def numbers(keyword, keywords):
    for num in range(10):
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + urllib.parse.quote(keyword + " " + str(num))
        try:
            response = requests.get(url, verify=False, timeout=5)
            response.raise_for_status()
            suggestions = json.loads(response.text)
            if len(suggestions) > 1 and isinstance(suggestions[1], list):
                for kw in suggestions[1]:
                    keywords.append(kw)
        except Exception as e:
            print(f"Error in prefixes: {str(e)}")
            continue

def get_more(keyword, keywords):
    for i in keywords[:50]:  # Limit to avoid too many requests
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + urllib.parse.quote(i)
        try:
            response = requests.get(url, verify=False, timeout=5)
            response.raise_for_status()
            suggestions = json.loads(response.text)
            if len(suggestions) > 1 and isinstance(suggestions[1], list):
                for kw in suggestions[1]:
                    keywords.append(kw)
            if len(keywords) >= 1000:
                break
        except Exception as e:
            print(f"Error in get_more: {str(e)}")
            continue

def clean_keywords(keywords, keyword):
    keywords = list(dict.fromkeys(keywords))
    keyword_parts = keyword.split()
    new_list = [word for word in keywords if all(val.lower() in word.lower() for val in keyword_parts)]
    return new_list

# Embedded CSS for Vercel deployment
EMBEDDED_CSS = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 30px;
    text-align: center;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-weight: 700;
}

.subtitle {
    font-size: 1.1em;
    opacity: 0.95;
}

.search-section {
    padding: 40px 30px;
    background: #f8f9fa;
}

.input-group {
    display: flex;
    gap: 15px;
    max-width: 800px;
    margin: 0 auto;
}

#keywordInput {
    flex: 1;
    padding: 15px 20px;
    font-size: 16px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    outline: none;
    transition: all 0.3s ease;
}

#keywordInput:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

#generateBtn {
    padding: 15px 30px;
    font-size: 16px;
    font-weight: 600;
    color: white;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;
}

#generateBtn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

#generateBtn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.error-message {
    margin: 20px 30px;
    padding: 15px 20px;
    background: #fee;
    color: #c33;
    border-radius: 10px;
    border-left: 4px solid #c33;
}

.results-section {
    padding: 30px;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    flex-wrap: wrap;
    gap: 15px;
}

.results-header h2 {
    color: #333;
    font-size: 1.8em;
}

.results-info {
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}

.count-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
}

.download-buttons {
    display: flex;
    gap: 10px;
}

.download-btn {
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    color: #667eea;
    background: white;
    border: 2px solid #667eea;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.download-btn:hover {
    background: #667eea;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
}

.keywords-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px;
    max-height: 600px;
    overflow-y: auto;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 10px;
}

.keyword-item {
    padding: 12px 16px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    transition: all 0.2s ease;
    font-size: 14px;
    word-break: break-word;
}

.keyword-item:hover {
    border-color: #667eea;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
}

.no-results {
    grid-column: 1 / -1;
    text-align: center;
    padding: 40px;
    color: #999;
    font-size: 16px;
}

.info-section {
    padding: 30px;
    background: #f8f9fa;
    border-top: 1px solid #e0e0e0;
}

.info-section h3 {
    color: #333;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.info-section ul {
    list-style: none;
    padding-left: 0;
}

.info-section li {
    padding: 8px 0;
    padding-left: 25px;
    position: relative;
    color: #666;
}

.info-section li:before {
    content: "✓";
    position: absolute;
    left: 0;
    color: #667eea;
    font-weight: bold;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 2em;
    }
    
    .input-group {
        flex-direction: column;
    }
    
    #generateBtn {
        width: 100%;
    }
    
    .results-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .download-buttons {
        width: 100%;
        flex-direction: column;
    }
    
    .download-btn {
        width: 100%;
    }
    
    .keywords-list {
        grid-template-columns: 1fr;
    }
}'''

# Embedded HTML template as fallback for Vercel
EMBEDDED_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Keyword Generator</title>
    <style>
    ''' + EMBEDDED_CSS + '''
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 SEO Keyword Generator</h1>
            <p class="subtitle">Generate SEO keywords instantly using Google autocomplete</p>
        </header>

        <div class="search-section">
            <form id="keywordForm">
                <div class="input-group">
                    <input 
                        type="text" 
                        id="keywordInput" 
                        placeholder="Enter your keyword or topic (e.g., 'coffee maker', 'camping gear')" 
                        required
                        autocomplete="off"
                    >
                    <button type="submit" id="generateBtn">
                        <span class="btn-text">Generate Keywords</span>
                        <span class="btn-loader" style="display: none;">⏳ Generating...</span>
                    </button>
                </div>
            </form>
        </div>

        <div id="errorMessage" class="error-message" style="display: none;"></div>

        <div id="resultsSection" class="results-section" style="display: none;">
            <div class="results-header">
                <h2>Generated Keywords</h2>
                <div class="results-info">
                    <span id="keywordCount" class="count-badge"></span>
                    <div class="download-buttons">
                        <button id="downloadCsv" class="download-btn">📥 Download CSV</button>
                        <button id="downloadJson" class="download-btn">📥 Download JSON</button>
                    </div>
                </div>
            </div>
            <div id="keywordsList" class="keywords-list"></div>
        </div>

        <div class="info-section">
            <h3>How it works:</h3>
            <ul>
                <li>Enter your keyword or topic</li>
                <li>Get Google autocomplete suggestions</li>
                <li>Receive prefix-based, suffix-based, and number variations</li>
                <li>Download results as CSV or JSON</li>
            </ul>
        </div>
    </div>

    <script>
        const form = document.getElementById('keywordForm');
        const keywordInput = document.getElementById('keywordInput');
        const generateBtn = document.getElementById('generateBtn');
        const resultsSection = document.getElementById('resultsSection');
        const keywordsList = document.getElementById('keywordsList');
        const errorMessage = document.getElementById('errorMessage');
        const keywordCount = document.getElementById('keywordCount');
        const downloadCsv = document.getElementById('downloadCsv');
        const downloadJson = document.getElementById('downloadJson');

        let currentKeyword = '';
        let currentKeywords = [];

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const keyword = keywordInput.value.trim();
            
            if (!keyword) {
                showError('Please enter a keyword');
                return;
            }

            currentKeyword = keyword;
            generateBtn.disabled = true;
            generateBtn.querySelector('.btn-text').style.display = 'none';
            generateBtn.querySelector('.btn-loader').style.display = 'inline';
            resultsSection.style.display = 'none';
            errorMessage.style.display = 'none';

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ keyword: keyword })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    currentKeywords = data.keywords;
                    displayResults(data.keywords, data.count);
                } else {
                    showError(data.error || 'An error occurred while generating keywords');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                generateBtn.disabled = false;
                generateBtn.querySelector('.btn-text').style.display = 'inline';
                generateBtn.querySelector('.btn-loader').style.display = 'none';
            }
        });

        function displayResults(keywords, count) {
            keywordCount.textContent = `${count} keywords found`;
            keywordsList.innerHTML = '';
            
            if (keywords.length === 0) {
                keywordsList.innerHTML = '<p class="no-results">No keywords found. Try a different keyword.</p>';
            } else {
                keywords.forEach((keyword, index) => {
                    const keywordItem = document.createElement('div');
                    keywordItem.className = 'keyword-item';
                    keywordItem.textContent = keyword;
                    keywordsList.appendChild(keywordItem);
                });
            }
            
            resultsSection.style.display = 'block';
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }

        downloadCsv.addEventListener('click', async () => {
            if (!currentKeyword || currentKeywords.length === 0) return;
            
            try {
                const response = await fetch('/api/download/csv', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        keyword: currentKeyword,
                        keywords: currentKeywords
                    })
                });

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${currentKeyword}-keywords.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                showError('Error downloading CSV: ' + error.message);
            }
        });

        downloadJson.addEventListener('click', async () => {
            if (!currentKeyword || currentKeywords.length === 0) return;
            
            try {
                const response = await fetch('/api/download/json', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        keyword: currentKeyword,
                        keywords: currentKeywords
                    })
                });

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${currentKeyword}-keywords.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                showError('Error downloading JSON: ' + error.message);
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    # Try to use Flask's template system first (for local development)
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback: Use embedded HTML (for Vercel deployment)
        # This ensures the app works even if templates folder isn't included
        return EMBEDDED_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Flask app is running'}), 200

@app.route('/static/style.css')
def serve_css():
    """Serve CSS file directly for Vercel deployment"""
    try:
        # Try to read from static folder first
        css_paths = [
            os.path.join(BASE_DIR, 'static', 'style.css'),
            os.path.join(app.static_folder, 'style.css') if app.static_folder else None,
            'static/style.css',
            os.path.join(os.getcwd(), 'static', 'style.css'),
            '/var/task/static/style.css'
        ]
        
        css_paths = [p for p in css_paths if p is not None]
        
        for css_path in css_paths:
            if os.path.exists(css_path) and os.path.isfile(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                return css_content, 200, {'Content-Type': 'text/css; charset=utf-8'}
        
        # Fallback: return embedded CSS
        return EMBEDDED_CSS, 200, {'Content-Type': 'text/css; charset=utf-8'}
    except Exception as e:
        # Return embedded CSS as fallback
        return EMBEDDED_CSS, 200, {'Content-Type': 'text/css; charset=utf-8'}

@app.route('/api/generate', methods=['POST'])
def generate_keywords():
    data = request.json
    keyword = data.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({'error': 'Please provide a keyword'}), 400
    
    try:
        keywords = api_call(keyword)
        return jsonify({
            'success': True,
            'keyword': keyword,
            'keywords': keywords,
            'count': len(keywords)
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in generate_keywords: {error_trace}")
        return jsonify({'error': str(e), 'traceback': error_trace}), 500

@app.route('/api/download/csv', methods=['POST'])
def download_csv():
    data = request.json
    keyword = data.get('keyword', '')
    keywords = data.get('keywords', [])
    
    df = pd.DataFrame(keywords, columns=['Keywords'])
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{keyword}-keywords.csv'
    )

@app.route('/api/download/json', methods=['POST'])
def download_json():
    data = request.json
    keyword = data.get('keyword', '')
    keywords = data.get('keywords', [])
    
    df = pd.DataFrame(keywords, columns=['Keywords'])
    output = BytesIO()
    df.to_json(output, orient="records")
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'{keyword}-keywords.json'
    )

# Export app for Vercel
# The @vercel/python builder will automatically detect this Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

