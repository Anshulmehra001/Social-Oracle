import os
import logging
from typing import List, Dict
from .base import BaseAdapter
from src.social_fetcher import SocialMediaFetcher  # reuse existing logic
from src.config import Config

logger = logging.getLogger(__name__)


class RedditAdapter(BaseAdapter):
    source_name = "reddit"

    def _enabled(self) -> bool:
        # Determine if credentials exist
        credentials_exist = all([
            os.getenv('REDDIT_CLIENT_ID'),
            os.getenv('REDDIT_CLIENT_SECRET'),
            os.getenv('REDDIT_USER_AGENT')
        ])
        
        if not credentials_exist:
            logger.info("ℹ️  Reddit API credentials not configured")
        
        return credentials_exist
    
    def is_available(self) -> bool:
        """Check if Reddit adapter is available."""
        return self._enabled()

    def fetch(self, keywords: List[str], tickers: List[str], limit: int = 30) -> List[Dict]:
        if not keywords:
            return []
        if not self._enabled():
            # Gracefully skip Reddit if not configured
            return []
        try:
            api_config = Config.get_api_config()
            fetcher = SocialMediaFetcher(api_config)
            # Use first keyword set and a general subreddit selection; could iterate more
            subreddit = 'stocks'
            text = fetcher.fetch_reddit_sentiment_data(" ".join(keywords), subreddit, limit=limit)
            if not text:
                return []
            # Split into segments (basic) by double newline
            segments = [s.strip() for s in text.split('\n\n') if s.strip()]
            records: List[Dict] = []
            for seg in segments[:limit]:
                rec_tickers = self._filter_tickers(seg, tickers)
                records.append({
                    'source': self.source_name,
                    'timestamp': self._now_iso(),
                    'text': seg,
                    'tickers': rec_tickers
                })
            logger.info(f"✅ Fetched {len(records)} Reddit posts")
            return records
        except Exception as e:
            logger.warning(f"⚠️  Reddit fetch failed: {e}")
            return []
