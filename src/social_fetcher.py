"""
Social Media Fetcher Component for Social Oracle System.
Handles Reddit data collection using PRAW library with error handling and rate limiting.
"""

import time
import logging
from typing import Optional, List
import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import RequestException
from praw.models import Submission, Comment

from .config import Config, APIConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialMediaFetcher:
    """Handles fetching and processing social media data from Reddit."""
    
    def __init__(self, api_config: APIConfig):
        """Initialize the Reddit API client with credentials."""
        self.api_config = api_config
        self.reddit = None
        self._initialize_reddit_client()
    
    def _initialize_reddit_client(self) -> None:
        """Initialize PRAW Reddit client with error handling."""
        try:
            self.reddit = praw.Reddit(
                client_id=self.api_config.reddit_client_id,
                client_secret=self.api_config.reddit_client_secret,
                user_agent=self.api_config.reddit_user_agent,
                timeout=Config.REDDIT_API_TIMEOUT
            )
            # Test the connection
            self.reddit.user.me()
            logger.info("Reddit API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            raise ConnectionError(f"Reddit API initialization failed: {e}")
    
    def _extract_post_content(self, submission: Submission) -> str:
        """Extract title and self-text from a Reddit post."""
        content_parts = []
        
        # Add post title
        if submission.title:
            content_parts.append(f"Title: {submission.title}")
        
        # Add post content (self-text)
        if hasattr(submission, 'selftext') and submission.selftext:
            content_parts.append(f"Content: {submission.selftext}")
        
        return "\n".join(content_parts)
    
    def _extract_comments(self, submission: Submission, limit: int = Config.MAX_COMMENTS_PER_POST) -> List[str]:
        """Extract top comments from a Reddit post with error handling."""
        comments = []
        
        try:
            # Replace MoreComments objects to get actual comments
            submission.comments.replace_more(limit=0)
            
            # Get top-level comments up to the limit
            for comment in submission.comments[:limit]:
                if isinstance(comment, Comment) and comment.body and comment.body != "[deleted]":
                    comments.append(f"Comment: {comment.body}")
            
        except Exception as e:
            logger.warning(f"Error extracting comments from post {submission.id}: {e}")
        
        return comments
    
    def _handle_rate_limit(self, retry_count: int) -> None:
        """Handle Reddit API rate limiting with exponential backoff."""
        if retry_count > 3:
            raise Exception("Maximum retry attempts exceeded for Reddit API")
        
        wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
        logger.warning(f"Rate limit encountered. Waiting {wait_time} seconds before retry {retry_count + 1}")
        time.sleep(wait_time)
    
    def fetch_reddit_sentiment_data(self, keywords: str, subreddit: str, limit: int = 50) -> str:
        """
        Fetch Reddit posts and comments for sentiment analysis.
        
        Args:
            keywords: Search terms for finding relevant posts
            subreddit: Target subreddit name (without 'r/')
            limit: Maximum number of posts to fetch (default: 50)
        
        Returns:
            Concatenated string of all collected text data
        
        Raises:
            ValueError: If invalid parameters are provided
            ConnectionError: If Reddit API is unavailable
            Exception: If data fetching fails after retries
        """
        if not keywords or not subreddit:
            raise ValueError("Keywords and subreddit are required")
        
        if limit <= 0 or limit > Config.MAX_REDDIT_POSTS:
            raise ValueError(f"Limit must be between 1 and {Config.MAX_REDDIT_POSTS}")
        
        logger.info(f"Fetching Reddit data: keywords='{keywords}', subreddit='{subreddit}', limit={limit}")
        
        all_text_data = []
        posts_processed = 0
        retry_count = 0
        
        while posts_processed < limit and retry_count <= 3:
            try:
                # Search for posts in the specified subreddit
                subreddit_obj = self.reddit.subreddit(subreddit)
                search_results = subreddit_obj.search(
                    keywords, 
                    sort='relevance', 
                    time_filter='month',
                    limit=limit
                )
                
                for submission in search_results:
                    if posts_processed >= limit:
                        break
                    
                    try:
                        # Extract post content
                        post_content = self._extract_post_content(submission)
                        if post_content:
                            all_text_data.append(post_content)
                        
                        # Extract comments
                        comments = self._extract_comments(submission)
                        all_text_data.extend(comments)
                        
                        posts_processed += 1
                        logger.debug(f"Processed post {posts_processed}/{limit}: {submission.title[:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"Error processing post {submission.id}: {e}")
                        continue
                
                # If we successfully processed posts, break the retry loop
                if posts_processed > 0:
                    break
                    
            except RedditAPIException as e:
                if "RATELIMIT" in str(e):
                    self._handle_rate_limit(retry_count)
                    retry_count += 1
                    continue
                else:
                    logger.error(f"Reddit API error: {e}")
                    raise ConnectionError(f"Reddit API error: {e}")
                    
            except RequestException as e:
                logger.error(f"Network error while fetching Reddit data: {e}")
                if retry_count < 3:
                    self._handle_rate_limit(retry_count)
                    retry_count += 1
                    continue
                else:
                    raise ConnectionError(f"Network error after retries: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected error while fetching Reddit data: {e}")
                raise Exception(f"Data fetching failed: {e}")
        
        if not all_text_data:
            logger.warning(f"No data found for keywords '{keywords}' in subreddit '{subreddit}'")
            return ""
        
        # Concatenate all text data
        concatenated_text = "\n\n".join(all_text_data)
        
        logger.info(f"Successfully fetched {posts_processed} posts with {len(all_text_data)} total text segments")
        logger.info(f"Total text length: {len(concatenated_text)} characters")
        
        return concatenated_text


def fetch_reddit_sentiment_data(keywords: str, subreddit: str, limit: int = 50) -> str:
    """
    Convenience function to fetch Reddit sentiment data.
    
    Args:
        keywords: Search terms for finding relevant posts
        subreddit: Target subreddit name (without 'r/')
        limit: Maximum number of posts to fetch (default: 50)
    
    Returns:
        Concatenated string of all collected text data
    """
    try:
        api_config = Config.get_api_config()
        fetcher = SocialMediaFetcher(api_config)
        return fetcher.fetch_reddit_sentiment_data(keywords, subreddit, limit)
    except Exception as e:
        logger.error(f"Failed to fetch Reddit sentiment data: {e}")
        raise