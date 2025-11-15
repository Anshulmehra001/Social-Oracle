"""
Unit tests for Social Media Fetcher component.
Tests Reddit API integration with mocked responses and error handling scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from praw.exceptions import RedditAPIException
from prawcore.exceptions import RequestException
from praw.models import Submission, Comment

from src.social_fetcher import SocialMediaFetcher, fetch_reddit_sentiment_data
from src.config import APIConfig


@pytest.fixture
def mock_api_config():
    """Create a mock API configuration for testing."""
    return APIConfig(
        reddit_client_id="test_client_id",
        reddit_client_secret="test_client_secret",
        reddit_user_agent="test_user_agent",
        gemini_api_key="test_gemini_key",
        bnb_rpc_url="test_rpc_url",
        private_key="test_private_key"
    )


@pytest.fixture
def mock_submission():
    """Create a mock Reddit submission for testing."""
    submission = Mock(spec=Submission)
    submission.id = "test_post_id"
    submission.title = "Test Post Title"
    submission.selftext = "This is test post content"
    
    # Mock comments
    comment1 = Mock(spec=Comment)
    comment1.body = "This is a test comment"
    comment2 = Mock(spec=Comment)
    comment2.body = "Another test comment"
    
    # Create mock comments list with replace_more method
    mock_comments = Mock()
    mock_comments.__iter__ = Mock(return_value=iter([comment1, comment2]))
    mock_comments.__getitem__ = Mock(side_effect=lambda i: [comment1, comment2][i])
    mock_comments.replace_more = Mock()
    
    submission.comments = mock_comments
    
    return submission


@pytest.fixture
def mock_reddit_client():
    """Create a mock Reddit client for testing."""
    with patch('src.social_fetcher.praw.Reddit') as mock_reddit_class:
        client = Mock()
        client.user.me.return_value = None  # Successful auth test
        mock_reddit_class.return_value = client
        yield client


class TestSocialMediaFetcher:
    """Test cases for SocialMediaFetcher class."""
    
    def test_initialization_success(self, mock_api_config, mock_reddit_client):
        """Test successful initialization of SocialMediaFetcher."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        assert fetcher.api_config == mock_api_config
        assert fetcher.reddit is not None
        mock_reddit_client.user.me.assert_called_once()
    
    def test_initialization_failure(self, mock_api_config):
        """Test initialization failure when Reddit API is unavailable."""
        with patch('src.social_fetcher.praw.Reddit') as mock_reddit:
            mock_reddit.side_effect = Exception("API connection failed")
            
            with pytest.raises(ConnectionError, match="Reddit API initialization failed"):
                SocialMediaFetcher(mock_api_config)
    
    def test_extract_post_content(self, mock_api_config, mock_reddit_client, mock_submission):
        """Test extraction of post title and content."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        content = fetcher._extract_post_content(mock_submission)
        
        assert "Title: Test Post Title" in content
        assert "Content: This is test post content" in content
    
    def test_extract_post_content_no_selftext(self, mock_api_config, mock_reddit_client):
        """Test extraction when post has no self-text content."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        submission = Mock(spec=Submission)
        submission.title = "Title Only Post"
        submission.selftext = ""
        
        content = fetcher._extract_post_content(submission)
        
        assert "Title: Title Only Post" in content
        assert "Content:" not in content
    
    def test_extract_comments(self, mock_api_config, mock_reddit_client, mock_submission):
        """Test extraction of comments from a post."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        comments = fetcher._extract_comments(mock_submission, limit=2)
        
        assert len(comments) == 2
        assert "Comment: This is a test comment" in comments
        assert "Comment: Another test comment" in comments
        mock_submission.comments.replace_more.assert_called_once_with(limit=0)
    
    def test_extract_comments_with_deleted(self, mock_api_config, mock_reddit_client):
        """Test comment extraction filtering out deleted comments."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        submission = Mock(spec=Submission)
        
        # Mock comments with one deleted
        comment1 = Mock(spec=Comment)
        comment1.body = "Valid comment"
        comment2 = Mock(spec=Comment)
        comment2.body = "[deleted]"
        
        # Create mock comments list with replace_more method
        mock_comments = Mock()
        mock_comments.__iter__ = Mock(return_value=iter([comment1, comment2]))
        mock_comments.__getitem__ = Mock(side_effect=lambda i: [comment1, comment2][i])
        mock_comments.replace_more = Mock()
        
        submission.comments = mock_comments
        
        comments = fetcher._extract_comments(submission)
        
        assert len(comments) == 1
        assert "Comment: Valid comment" in comments
        assert "[deleted]" not in str(comments)
    
    def test_fetch_reddit_sentiment_data_success(self, mock_api_config, mock_reddit_client, mock_submission):
        """Test successful fetching of Reddit sentiment data."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        # Mock subreddit and search results
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = [mock_submission]
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        result = fetcher.fetch_reddit_sentiment_data("test keywords", "test_subreddit", limit=1)
        
        assert "Title: Test Post Title" in result
        assert "Content: This is test post content" in result
        assert "Comment: This is a test comment" in result
        mock_reddit_client.subreddit.assert_called_once_with("test_subreddit")
        mock_subreddit.search.assert_called_once_with(
            "test keywords", 
            sort='relevance', 
            time_filter='month',
            limit=1
        )
    
    def test_fetch_reddit_sentiment_data_invalid_params(self, mock_api_config, mock_reddit_client):
        """Test validation of input parameters."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        # Test empty keywords
        with pytest.raises(ValueError, match="Keywords and subreddit are required"):
            fetcher.fetch_reddit_sentiment_data("", "test_subreddit")
        
        # Test empty subreddit
        with pytest.raises(ValueError, match="Keywords and subreddit are required"):
            fetcher.fetch_reddit_sentiment_data("test", "")
        
        # Test invalid limit
        with pytest.raises(ValueError, match="Limit must be between 1 and"):
            fetcher.fetch_reddit_sentiment_data("test", "test_subreddit", limit=0)
        
        with pytest.raises(ValueError, match="Limit must be between 1 and"):
            fetcher.fetch_reddit_sentiment_data("test", "test_subreddit", limit=100)
    
    def test_fetch_reddit_sentiment_data_no_results(self, mock_api_config, mock_reddit_client):
        """Test handling when no posts are found."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        # Mock empty search results
        mock_subreddit = Mock()
        mock_subreddit.search.return_value = []
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        result = fetcher.fetch_reddit_sentiment_data("test keywords", "test_subreddit")
        
        assert result == ""
    
    def test_handle_rate_limit_error(self, mock_api_config, mock_reddit_client):
        """Test handling of Reddit API rate limiting."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        # Mock rate limit exception
        rate_limit_exception = RedditAPIException([{"error_type": "RATELIMIT"}])
        mock_subreddit = Mock()
        mock_subreddit.search.side_effect = [rate_limit_exception, []]
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        with patch('src.social_fetcher.time.sleep') as mock_sleep:
            result = fetcher.fetch_reddit_sentiment_data("test", "test_subreddit")
            
            assert result == ""
            mock_sleep.assert_called()  # Should have slept due to rate limit
    
    def test_handle_network_error(self, mock_api_config, mock_reddit_client):
        """Test handling of network errors with retry logic."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        # Mock network exception
        network_exception = RequestException("Network error")
        mock_subreddit = Mock()
        mock_subreddit.search.side_effect = [network_exception, []]
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        with patch('src.social_fetcher.time.sleep') as mock_sleep:
            result = fetcher.fetch_reddit_sentiment_data("test", "test_subreddit")
            
            assert result == ""
            mock_sleep.assert_called()  # Should have slept due to retry
    
    def test_handle_max_retries_exceeded(self, mock_api_config, mock_reddit_client):
        """Test behavior when maximum retry attempts are exceeded."""
        fetcher = SocialMediaFetcher(mock_api_config)
        
        # Mock persistent network exception
        network_exception = RequestException("Persistent network error")
        mock_subreddit = Mock()
        mock_subreddit.search.side_effect = network_exception
        mock_reddit_client.subreddit.return_value = mock_subreddit
        
        with patch('src.social_fetcher.time.sleep'):
            with pytest.raises(ConnectionError, match="Network error after retries"):
                fetcher.fetch_reddit_sentiment_data("test", "test_subreddit")


class TestConvenienceFunction:
    """Test cases for the convenience function."""
    
    @patch('src.social_fetcher.Config.get_api_config')
    @patch('src.social_fetcher.SocialMediaFetcher')
    def test_fetch_reddit_sentiment_data_function(self, mock_fetcher_class, mock_get_config):
        """Test the convenience function for fetching Reddit data."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock fetcher instance
        mock_fetcher = Mock()
        mock_fetcher.fetch_reddit_sentiment_data.return_value = "test result"
        mock_fetcher_class.return_value = mock_fetcher
        
        result = fetch_reddit_sentiment_data("test", "test_subreddit", limit=10)
        
        assert result == "test result"
        mock_get_config.assert_called_once()
        mock_fetcher_class.assert_called_once_with(mock_config)
        mock_fetcher.fetch_reddit_sentiment_data.assert_called_once_with("test", "test_subreddit", 10)
    
    @patch('src.social_fetcher.Config.get_api_config')
    def test_fetch_reddit_sentiment_data_function_error(self, mock_get_config):
        """Test error handling in the convenience function."""
        mock_get_config.side_effect = Exception("Config error")
        
        with pytest.raises(Exception, match="Config error"):
            fetch_reddit_sentiment_data("test", "test_subreddit")