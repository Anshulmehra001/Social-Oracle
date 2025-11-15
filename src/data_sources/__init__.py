"""Data source adapters for multi-source sentiment ingestion.

Each adapter implements a `fetch` method returning a list of standardized
records:
    {
        'source': str,
        'timestamp': datetime (ISO string),
        'text': str,
        'tickers': list[str]
    }

Adapters should NEVER raise fatal exceptions; they return an empty list
on failure to keep the pipeline resilient.
"""

from .rss_adapter import RSSAdapter
from .hacker_news_adapter import HackerNewsAdapter
from .reddit_adapter import RedditAdapter
from .stocktwits_adapter import StocktwitsAdapter
from .sample_adapter import SampleAdapter
from .aggregator import MultiSourceAggregator

__all__ = [
    'RSSAdapter',
    'HackerNewsAdapter',
    'RedditAdapter',
    'StocktwitsAdapter',
    'SampleAdapter',
    'MultiSourceAggregator'
]
