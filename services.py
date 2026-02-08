import asyncio
import aiohttp
import urllib.parse
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleKeywordService:
    BASE_URL = "http://suggestqueries.google.com/complete/search"
    
    def __init__(self):
        self.prefixes_list = [
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
            'u','v','w','x','y','z',
            'how','which','why','where','who','when','are','what'
        ]
        self.suffixes_list = [
            'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
            'u','v','w','x','y','z',
            'like','for','without','with','versus','vs','to','near','except','has'
        ]

    async def fetch_suggestions(self, session, query):
        url = f"{self.BASE_URL}?output=firefox&q={urllib.parse.quote(query)}"
        try:
            async with session.get(url, verify_ssl=False, timeout=5) as response:
                response.raise_for_status()
                text = await response.text()
                data = json.loads(text)
                if len(data) > 1 and isinstance(data[1], list):
                    return data[1]
        except Exception as e:
            logger.error(f"Error fetching suggestions for '{query}': {e}")
        return []

    async def generate_keywords(self, root_keyword):
        all_keywords = set()
        all_keywords.add(root_keyword)

        async with aiohttp.ClientSession() as session:
            # 1. Base keyword
            base_suggestions = await self.fetch_suggestions(session, root_keyword)
            all_keywords.update(base_suggestions)

            # Prepare tasks for variations
            tasks = []

            # Prefixes
            for prefix in self.prefixes_list:
                tasks.append(self.fetch_suggestions(session, f"{prefix} {root_keyword}"))

            # Suffixes
            for suffix in self.suffixes_list:
                tasks.append(self.fetch_suggestions(session, f"{root_keyword} {suffix}"))

            # Numbers
            for num in range(10):
                tasks.append(self.fetch_suggestions(session, f"{root_keyword} {num}"))

            # Run all primary variations concurrently
            results = await asyncio.gather(*tasks)
            for res in results:
                all_keywords.update(res)

            # Get more (second level) - Limit to top 50 to avoid ease of banning but still get good breadth
            # We can't reuse the same loop easily because we need the results of the first pass.
            # Convert to list to iterate
            current_list = list(all_keywords)[:50] 
            
            more_tasks = []
            for kw in current_list:
                if kw != root_keyword: # Avoid re-fetching base
                    more_tasks.append(self.fetch_suggestions(session, kw))
            
            more_results = await asyncio.gather(*more_tasks)
            for res in more_results:
                all_keywords.update(res)

        return self.filter_keywords(list(all_keywords), root_keyword)

    def filter_keywords(self, keywords, root_keyword):
        # Ensure all parts of the root keyword are in the result (fuzzy match logic from original)
        # Original logic: all(val.lower() in word.lower() for val in keyword_parts)
        # This might be too strict if the user wants broad suggestions, but maintaining original logic for now.
        # However, improved slightly to be case-insensitive properly.
        
        root_parts = root_keyword.lower().split()
        filtered = []
        
        for kw in keywords:
            kw_lower = kw.lower()
            if all(part in kw_lower for part in root_parts):
                filtered.append(kw)
        
        return sorted(filtered)
