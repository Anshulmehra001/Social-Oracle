from typing import List, Dict, Sequence
from collections import defaultdict
import logging
from .rss_adapter import RSSAdapter
from .hacker_news_adapter import HackerNewsAdapter
from .reddit_adapter import RedditAdapter
from .stocktwits_adapter import StocktwitsAdapter
from .twitter_adapter import TwitterAdapter
from .sample_adapter import SampleAdapter

logger = logging.getLogger(__name__)


class MultiSourceAggregator:
    """Collects text records from multiple adapters with fallback.

    Order matters: higher precision sources first. All failures are silent.
    Tracks source contributions per ticker for transparency.
    """

    def __init__(self, enable_optional: bool = True):
        self.adapters = [
            RSSAdapter(),
            HackerNewsAdapter(),
        ]
        
        # Add optional social media sources
        if enable_optional:
            # Twitter/X - optional, gracefully disabled if not configured
            twitter = TwitterAdapter()
            if twitter.is_available():
                self.adapters.append(twitter)
                logger.info("✅ Twitter/X enabled as data source")
            else:
                logger.info("ℹ️  Twitter/X not configured - continuing without it")
            
            # Reddit - optional
            reddit = RedditAdapter()
            if reddit.is_available():
                self.adapters.append(reddit)
                logger.info("✅ Reddit enabled as data source")
            else:
                logger.info("ℹ️  Reddit not configured - continuing without it")
            
            # Stocktwits - optional
            stocktwits = StocktwitsAdapter()
            if stocktwits.is_available():
                self.adapters.append(stocktwits)
                logger.info("✅ Stocktwits enabled as data source")
            else:
                logger.info("ℹ️  Stocktwits not configured - continuing without it")
        
        # Always keep sample fallback last
        self.adapters.append(SampleAdapter())
        logger.info(f"📊 Initialized aggregator with {len(self.adapters)} data sources")
        
        # Track collected records and their sources
        self._last_records: List[Dict] = []
        self._source_stats: Dict[str, Dict[str, int]] = {}

    def collect(self, keywords: Sequence[str], tickers: Sequence[str], per_adapter_limit: int = 40) -> List[Dict]:
        """Collect records from all adapters and track sources."""
        all_records: List[Dict] = []
        kw_list = list(keywords)
        tk_list = list(tickers)
        
        for adapter in self.adapters:
            try:
                recs = adapter.fetch(kw_list, tk_list, limit=per_adapter_limit)
                all_records.extend(recs)
            except Exception:
                continue
        
        self._last_records = all_records
        self._build_source_stats(all_records, tickers)
        return all_records

    def aggregate(self, tickers: Sequence[str], hours_back: int = 24, keywords: Sequence[str] = None) -> Dict[str, List[str]]:
        """
        Main aggregation method that returns text segments grouped by ticker.
        Compatible with web app interface.
        """
        if keywords is None:
            keywords = []
        
        records = self.collect(keywords, tickers, per_adapter_limit=40)
        
        # Group text by ticker
        by_ticker = {t: [] for t in tickers}
        general_segments = []
        
        for r in records:
            if r.get('tickers'):
                for t in r['tickers']:
                    if t in by_ticker:
                        by_ticker[t].append(r['text'])
            else:
                general_segments.append(r['text'])
        
        # Add general segments to all tickers
        result = {}
        for t, segs in by_ticker.items():
            all_segs = segs + general_segments
            if all_segs:
                result[t] = all_segs
            else:
                result[t] = []
        
        return result

    def _build_source_stats(self, records: List[Dict], tickers: Sequence[str]):
        """Build statistics about which sources contributed to each ticker."""
        self._source_stats = {t: defaultdict(int) for t in tickers}
        
        for r in records:
            source = r.get('source', 'Unknown')
            if r.get('tickers'):
                for t in r['tickers']:
                    if t in self._source_stats:
                        self._source_stats[t][source] += 1
            else:
                # General record counts for all tickers
                for t in self._source_stats:
                    self._source_stats[t][source] += 1

    def get_source_stats(self, ticker: str) -> Dict[str, int]:
        """Get source contribution stats for a specific ticker."""
        return dict(self._source_stats.get(ticker, {}))

    @staticmethod
    def concatenate_text(records: List[Dict], tickers: Sequence[str]) -> Dict[str, str]:
        """Legacy method: concatenate all text by ticker into single strings."""
        by_ticker = {t: [] for t in tickers}
        general_segments = []
        for r in records:
            if r.get('tickers'):
                for t in r['tickers']:
                    if t in by_ticker:
                        by_ticker[t].append(r['text'])
            else:
                general_segments.append(r['text'])
        concatenated = {}
        general_blob = '\n\n'.join(general_segments)
        for t, segs in by_ticker.items():
            text_parts = segs + ([general_blob] if general_blob else [])
            concatenated[t] = '\n\n'.join(text_parts)
        return concatenated
