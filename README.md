# Abhi Mengar

# Keyword-generator-SEO

Keyword generator using Google autocomplete API.

### How it works:
- Enter your keyword
- Script fetches:
  - Google autocomplete
  - Prefix-based results
  - Suffix-based results
  - Number appended results
  - Deep recursive autocomplete

### Output:
- `[keyword]-keywords.csv`
- `[keyword]-keywords.json`

### Web Application (Recommended):

Run the web application for easy access:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web server
python app.py
```

Then open your browser and go to: `http://localhost:5000`

The web interface allows anyone to:
- Enter keywords easily through a web form
- See results instantly
- Download CSV or JSON files
- Access from any device on your network

### Command Line (Original):

```bash
python3 suggestqueries.py
```

### Requirements:
```
pip install -r requirements.txt
```

Or manually:
```
pip install Flask requests pandas
```
