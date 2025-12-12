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

app = Flask(__name__)

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
    return render_template('index.html')

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

