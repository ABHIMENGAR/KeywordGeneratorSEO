#!/usr/bin/env python3
import requests
import json
import pandas as pd

keyword = input('Add your keyword: ')

def api_call(keyword):
    keywords = [keyword]
    url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + keyword
    response = requests.get(url, verify=False)
    suggestions = json.loads(response.text)
    for word in suggestions[1]:
        keywords.append(word)

    prefixes(keyword, keywords)
    suffixes(keyword, keywords)
    numbers(keyword, keywords)
    get_more(keyword, keywords)
    clean_df(keywords, keyword)

def prefixes(keyword, keywords):
    prefixes = [
        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
        'u','v','w','x','y','z',
        'how','which','why','where','who','when','are','what'
    ]
    for prefix in prefixes:
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + prefix + " " + keyword
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)
        for kw in suggestions[1]:
            keywords.append(kw)

def suffixes(keyword, keywords):
    suffixes = [
        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
        'u','v','w','x','y','z',
        'like','for','without','with','versus','vs','to','near','except','has'
    ]
    for suffix in suffixes:
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + keyword + " " + suffix
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)
        for kw in suggestions[1]:
            keywords.append(kw)

def numbers(keyword, keywords):
    for num in range(10):
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + keyword + " " + str(num)
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)
        for kw in suggestions[1]:
            keywords.append(kw)

def get_more(keyword, keywords):
    for i in keywords:
        url = "http://suggestqueries.google.com/complete/search?output=firefox&q=" + i
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)
        for kw in suggestions[1]:
            keywords.append(kw)
        if len(keywords) >= 1000:
            break

def clean_df(keywords, keyword):
    keywords = list(dict.fromkeys(keywords))
    new_list = [word for word in keywords if all(val in word for val in keyword.split())]
    df = pd.DataFrame(new_list, columns=['Keywords'])
    df.to_csv(keyword + '-keywords.csv', index=False)
    df.to_json(keyword + '-keywords.json', orient="records")

if __name__ == "__main__":
    api_call(keyword)
