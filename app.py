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

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback: try to read template file directly
        try:
            template_paths = [
                os.path.join(BASE_DIR, 'templates', 'index.html'),
                os.path.join(app.template_folder, 'index.html') if app.template_folder else None,
                os.path.join('templates', 'index.html'),
                os.path.join(os.getcwd(), 'templates', 'index.html'),
                '/var/task/templates/index.html',
                'templates/index.html'
            ]
            
            # Filter out None values
            template_paths = [p for p in template_paths if p is not None]
            
            for template_path in template_paths:
                try:
                    if os.path.exists(template_path) and os.path.isfile(template_path):
                        with open(template_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        # Use Flask's url_for for static files - need to process template
                        from flask import url_for
                        # Simple replacement for url_for('static', filename='style.css')
                        html_content = html_content.replace(
                            "{{ url_for('static', filename='style.css') }}",
                            '/static/style.css'
                        )
                        return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
                except Exception as path_error:
                    continue
            
            # If template file not found, return error with helpful message
            import traceback
            error_trace = traceback.format_exc()
            return f"""
            <html>
            <head><title>Template Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>Template Not Found</h1>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><strong>Checked paths:</strong></p>
                <ul>
                    {''.join([f'<li>{p} - {"EXISTS" if os.path.exists(p) else "NOT FOUND"}</li>' for p in template_paths])}
                </ul>
                <p><strong>Current directory:</strong> {os.getcwd()}</p>
                <p><strong>BASE_DIR:</strong> {BASE_DIR}</p>
                <p><strong>Template folder:</strong> {app.template_folder}</p>
                <p><strong>Static folder:</strong> {app.static_folder}</p>
                <pre>{error_trace}</pre>
            </body>
            </html>
            """, 500
        except Exception as fallback_error:
            import traceback
            error_trace = traceback.format_exc()
            return f"Error loading template: {str(e)}<br>Fallback error: {str(fallback_error)}<br><pre>{error_trace}</pre>", 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Flask app is running'}), 200

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

