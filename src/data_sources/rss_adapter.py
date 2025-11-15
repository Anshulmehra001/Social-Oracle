import feedparser
from typing import List, Dict
from .base import BaseAdapter


FINANCE_RSS_FEEDS = [
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
    "https://www.marketwatch.com/rss/topstories",
    "https://www.investing.com/rss/news_25.rss",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",  # CNBC Top News
]


class RSSAdapter(BaseAdapter):
    source_name = "rss_news"

    def fetch(self, keywords: List[str], tickers: List[str], limit: int = 50) -> List[Dict]:
        records: List[Dict] = []
        kw_lower = [k.lower() for k in keywords]

        for feed_url in FINANCE_RSS_FEEDS:
            try:
                parsed = feedparser.parse(feed_url)
                for entry in parsed.entries[:limit]:
                    title = getattr(entry, 'title', '') or ''
                    summary = getattr(entry, 'summary', '') or ''
                    text = f"{title}\n{summary}".strip()
                    if not text:
                        continue
                    if kw_lower and not any(k in text.lower() for k in kw_lower):
                        continue
                    rec_tickers = self._filter_tickers(text, tickers)
                    records.append({
                        'source': self.source_name,
                        'timestamp': self._now_iso(),
                        'text': text,
                        'tickers': rec_tickers
                    })
            except Exception:
                continue
        return records[:limit]
