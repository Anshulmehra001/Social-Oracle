"""
Configuration management for Social Oracle System.
Handles environment variables, market definitions, and system constants.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class MarketConfig:
    """Configuration for a prediction market."""
    question: str
    search_keywords: str
    reddit_subreddit: str
    post_limit: int = 50

@dataclass
class APIConfig:
    """API configuration and credentials."""
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    gemini_api_key: str
    bnb_rpc_url: str
    private_key: str

class Config:
    """Main configuration class for the Social Oracle System."""
    
    # System Constants
    MAX_REDDIT_POSTS = 50
    MAX_COMMENTS_PER_POST = 10
    REDDIT_API_TIMEOUT = 60  # seconds
    GEMINI_API_TIMEOUT = 30  # seconds
    BLOCKCHAIN_TIMEOUT = 120  # seconds
    
    # Sentiment Analysis Constants
    VALID_SENTIMENTS = ["Positive", "Negative", "Neutral"]
    
    # BNB Smart Chain Testnet Configuration
    BNB_TESTNET_RPC = "https://data-seed-prebsc-1-s1.binance.org:8545/"
    BNB_TESTNET_CHAIN_ID = 97
    BNB_EXPLORER_URL = "https://testnet.bscscan.com"
    
    # Gas Configuration
    DEFAULT_GAS_LIMIT = 3000000
    GAS_PRICE_GWEI = 10
    
    @classmethod
    def get_api_config(cls) -> APIConfig:
        """Load API configuration from environment variables."""
        required_vars = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET", 
            "REDDIT_USER_AGENT",
            "GEMINI_API_KEY",
            "BNB_RPC_URL",
            "PRIVATE_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please check your .env file and ensure all variables are set."
            )
        
        return APIConfig(
            reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
            reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            reddit_user_agent=os.getenv("REDDIT_USER_AGENT"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            bnb_rpc_url=os.getenv("BNB_RPC_URL", cls.BNB_TESTNET_RPC),
            private_key=os.getenv("PRIVATE_KEY")
        )
    
    @classmethod
    def create_market_config(cls, question: str, keywords: str, subreddit: str, 
                           post_limit: int = None) -> MarketConfig:
        """Create a market configuration with validation."""
        if not question or not keywords or not subreddit:
            raise ValueError("Market question, keywords, and subreddit are required")
        
        if post_limit is None:
            post_limit = cls.MAX_REDDIT_POSTS
        
        if post_limit > cls.MAX_REDDIT_POSTS:
            raise ValueError(f"Post limit cannot exceed {cls.MAX_REDDIT_POSTS}")
        
        return MarketConfig(
            question=question,
            search_keywords=keywords,
            reddit_subreddit=subreddit,
            post_limit=post_limit
        )
    
    @classmethod
    def validate_environment(cls) -> bool:
        """Validate that all required environment variables are present."""
        try:
            cls.get_api_config()
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_blockchain_explorer_url(cls, tx_hash: str) -> str:
        """Generate block explorer URL for transaction verification."""
        return f"{cls.BNB_EXPLORER_URL}/tx/{tx_hash}"