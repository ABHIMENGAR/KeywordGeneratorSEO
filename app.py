#!/usr/bin/env python3
import os
import asyncio
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from io import BytesIO
from services import GoogleKeywordService

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure Flask with robust paths for Vercel
# Detect environment
IS_VERCEL = os.environ.get('VERCEL') == '1' or 'var/task' in BASE_DIR

def find_file(folder_name, file_name):
    """Search for a file in multiple possible locations on Vercel"""
    search_paths = [
        os.path.join(BASE_DIR, folder_name, file_name),
        os.path.join(os.getcwd(), folder_name, file_name),
        os.path.join('/var/task', folder_name, file_name),
        os.path.join(BASE_DIR, '..', folder_name, file_name),
        f"{folder_name}/{file_name}"
    ]
    for path in search_paths:
        if os.path.exists(path):
            return path
    return None

app = Flask(__name__)

# Initialize Service
keyword_service = GoogleKeywordService()

@app.route('/static/style.css')
def serve_css():
    path = find_file('static', 'style.css')
    if path:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/css'}
    return "", 404

@app.route('/static/script.js')
def serve_js():
    path = find_file('static', 'script.js')
    if path:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    return "", 404

@app.route('/')
def index():
    path = find_file('templates', 'index.html')
    if path:
        try:
            # We can't use render_template easily if we are manually finding the path
            # but we can try to use it if the path is relative to Flask's expectations
            # or just read and return it.
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple replacement for url_for to ensure static links work
                content = content.replace("{{ url_for('static', filename='style.css') }}", "/static/style.css")
                content = content.replace("{{ url_for('static', filename='script.js') }}", "/static/script.js")
                return content, 200, {'Content-Type': 'text/html'}
        except Exception:
            pass
    return "<h1>Keyword Generator SEO</h1><p>The application is running, but the template could not be loaded.</p>", 200, {'Content-Type': 'text/html'}

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Flask app is running'}), 200

@app.route('/api/generate', methods=['POST'])
async def generate_keywords():
    data = request.json
    keyword = data.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({'error': 'Please provide a keyword'}), 400
    
    try:
        # Use the async service
        keywords = await keyword_service.generate_keywords(keyword)
        
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Threaded=True is default, but for async usually we want to be careful with WSGI servers.
    # For development, app.run is fine.
    app.run(debug=True, host='0.0.0.0', port=port)
