"""
X (Twitter) Data Source Adapter

Optional adapter for fetching tweets using Tweepy library.
Provides sentiment data from Twitter/X for prediction markets.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List
from .base import BaseAdapter

logger = logging.getLogger(__name__)


class TwitterAdapter(BaseAdapter):
    """
    Adapter for fetching data from X (Twitter) using Tweepy.
    
    This is an OPTIONAL data source. If Twitter API credentials are not configured,
    the system will gracefully skip this source and continue with others.
    
    Setup Instructions:
    1. Get API access at https://developer.twitter.com/
    2. Create a new app and get your credentials
    3. Add to your .env file:
       TWITTER_API_KEY=your_api_key
       TWITTER_API_SECRET=your_api_secret
       TWITTER_ACCESS_TOKEN=your_access_token
       TWITTER_ACCESS_SECRET=your_access_secret
       TWITTER_BEARER_TOKEN=your_bearer_token  (recommended for API v2)
    """
    
    def __init__(self):
        """Initialize Twitter adapter with optional credentials."""
        super().__init__()
        self.source_id = "twitter"
        self.enabled = False
        self.client = None
        
        try:
            import tweepy
            self._tweepy = tweepy
            
            # Try Bearer Token first (simpler, API v2)
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token:
                self.client = tweepy.Client(bearer_token=bearer_token)
                self.enabled = True
                logger.info("✅ Twitter adapter initialized with Bearer Token (API v2)")
            else:
                # Fall back to OAuth 1.0a (API v1.1)
                api_key = os.getenv('TWITTER_API_KEY')
                api_secret = os.getenv('TWITTER_API_SECRET')
                access_token = os.getenv('TWITTER_ACCESS_TOKEN')
                access_secret = os.getenv('TWITTER_ACCESS_SECRET')
                
                if all([api_key, api_secret, access_token, access_secret]):
                    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
                    self.client = tweepy.API(auth)
                    self.enabled = True
                    logger.info("✅ Twitter adapter initialized with OAuth 1.0a (API v1.1)")
                else:
                    logger.info("ℹ️  Twitter API credentials not found - skipping Twitter as data source")
                    
        except ImportError:
            logger.info("ℹ️  Tweepy not installed - Twitter adapter disabled. Install with: pip install tweepy")
        except Exception as e:
            logger.warning(f"⚠️  Twitter adapter initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Twitter API is configured and available."""
        return self.enabled and self.client is not None
    
    def fetch_data(self, ticker: str, hours_back: int = 24) -> List[str]:
        """
        Fetch recent tweets mentioning the ticker symbol.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")
            hours_back: How many hours of historical data to fetch
            
        Returns:
            List of tweet texts
        """
        if not self.is_available():
            logger.debug(f"Twitter adapter not available for {ticker}")
            return []
        
        try:
            tweets = []
            query = f"${ticker} OR #{ticker}"
            
            # Calculate time window
            start_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Use API v2 if available (with Bearer Token)
            if hasattr(self.client, 'search_recent_tweets'):
                response = self.client.search_recent_tweets(
                    query=query,
                    max_results=100,  # Max allowed by free tier
                    start_time=start_time,
                    tweet_fields=['created_at', 'public_metrics', 'lang']
                )
                
                if response.data:
                    for tweet in response.data:
                        # Filter English tweets only
                        if hasattr(tweet, 'lang') and tweet.lang == 'en':
                            tweets.append(tweet.text)
                    
                    logger.info(f"✅ Fetched {len(tweets)} tweets for {ticker} from Twitter")
                else:
                    logger.info(f"No tweets found for {ticker}")
            
            # Fall back to API v1.1 if using OAuth
            elif hasattr(self.client, 'search_tweets'):
                response = self.client.search_tweets(
                    q=query,
                    count=100,
                    lang='en',
                    result_type='recent'
                )
                
                for tweet in response:
                    tweets.append(tweet.text)
                
                logger.info(f"✅ Fetched {len(tweets)} tweets for {ticker} from Twitter")
            
            return tweets
            
        except Exception as e:
            logger.error(f"❌ Error fetching Twitter data for {ticker}: {e}")
            return []
    
    def get_config_instructions(self) -> str:
        """Return instructions for configuring this adapter."""
        return """
Twitter/X API Setup:
1. Go to https://developer.twitter.com/
2. Apply for API access (free tier available)
3. Create a new app in the Developer Portal
4. Get your credentials from the app dashboard
5. Add to your .env file:

   # Option 1: Bearer Token (Recommended - API v2)
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   
   # Option 2: OAuth 1.0a (API v1.1)
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret

6. Install tweepy: pip install tweepy
7. Restart the application

Note: Twitter API has rate limits. Free tier allows 500k tweets/month.
"""
