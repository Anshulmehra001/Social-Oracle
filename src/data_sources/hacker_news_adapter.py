import requests
from typing import List, Dict
from .base import BaseAdapter


class HackerNewsAdapter(BaseAdapter):
    source_name = "hacker_news"
    SEARCH_URL = "https://hn.algolia.com/api/v1/search"

    def fetch(self, keywords: List[str], tickers: List[str], limit: int = 40) -> List[Dict]:
        records: List[Dict] = []
        if not keywords:
            return records
        query = "+".join(keywords[:3])  # simple concatenation
        try:
            resp = requests.get(self.SEARCH_URL, params={"query": query, "tags": "story", "hitsPerPage": limit}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for hit in data.get('hits', [])[:limit]:
                    title = hit.get('title') or ''
                    if not title:
                        continue
                    rec_tickers = self._filter_tickers(title, tickers)
                    records.append({
                        'source': self.source_name,
                        'timestamp': self._now_iso(),
                        'text': title,
                        'tickers': rec_tickers
                    })
        except Exception:
            return []
        return records
