from typing import List, Dict
import os
import logging
import requests
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class StocktwitsAdapter(BaseAdapter):
    """Optional adapter for Stocktwits public streams.

    If no API token or failures occur, returns empty list. This keeps pipeline optional.
    Note: Official API may have restrictions; this is best-effort.
    """

    source_name = "stocktwits"
    BASE_URL = "https://api.stocktwits.com/api/2/streams/symbol/{}.json"

    def _enabled(self) -> bool:
        # Stocktwits public endpoint can work without token, but we allow token env for future
        return True  # keep always attempt but will limit tickers
    
    def is_available(self) -> bool:
        """Check if Stocktwits adapter is available."""
        return self._enabled()

    def fetch(self, keywords: List[str], tickers: List[str], limit: int = 25) -> List[Dict]:
        if not self._enabled():
            return []
        records: List[Dict] = []
        # Limit to first 3 tickers to avoid excessive calls
        for t in tickers[:3]:
            try:
                resp = requests.get(self.BASE_URL.format(t.upper()), timeout=8)
                if resp.status_code != 200:
                    logger.debug(f"Stocktwits returned {resp.status_code} for {t}")
                    continue
                data = resp.json()
                messages = data.get('messages', [])
                for msg in messages[:limit]:
                    body = msg.get('body', '')
                    if not body:
                        continue
                    # Keyword filter if provided
                    if keywords and not any(k.lower() in body.lower() for k in keywords):
                        continue
                    rec_tickers = self._filter_tickers(body, tickers)
                    records.append({
                        'source': self.source_name,
                        'timestamp': self._now_iso(),
                        'text': body,
                        'tickers': rec_tickers
                    })
            except Exception as e:
                logger.warning(f"⚠️  Stocktwits fetch error for {t}: {e}")
                continue
        
        if records:
            logger.info(f"✅ Fetched {len(records)} Stocktwits messages")
        
        return records[:limit]
