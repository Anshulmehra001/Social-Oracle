"""
Demo: Social Oracle Without Reddit API

This script demonstrates the Social Oracle sentiment analysis system
using sample data instead of live Reddit API calls. Perfect for testing
when you don't have Reddit API credentials or want a quick demo.
"""

import os
from src.ai_analyzer import AIAnalyzer
from src.blockchain_connector import BlockchainConnector
from src.config import Config


def main():
    print("=" * 60)
    print("🔮 Social Oracle - Demo Mode (No Reddit Required)")
    print("=" * 60)
    print()
    
    # Sample social media data simulating sentiment discussions
    sample_data = """
Title: Bitcoin price looking bullish
Content: The charts are showing strong support at $40k level. 
Technical indicators suggest an upward trend is forming.

Comment by user1: I'm very optimistic about BTC's future prospects
Comment by user2: Technical indicators are showing positive momentum
Comment by user3: Market sentiment is improving across the board
Comment by user4: Bullish trend confirmed by multiple analysts
Comment by user5: Strong accumulation phase visible in data

Post: Institutional investors increasing positions
Content: Major firms are adding BTC to their portfolios this quarter.
Recent data shows significant inflow into Bitcoin ETFs.

Comment by analyst1: This is a strong signal for long-term growth
Comment by trader2: Best entry point we've seen in months
Comment by hodler3: Diamond hands! The fundamentals are solid
    """
    
    print("📊 Sample Data Loaded")
    print(f"   Length: {len(sample_data)} characters")
    print(f"   Simulating social media discussions about Bitcoin")
    print()
    
    # Load configuration
    try:
        config = Config.get_api_config()
        print("✅ Configuration loaded successfully")
        
        # Check if Gemini API key is available
        if not config.gemini_api_key:
            print("❌ ERROR: GEMINI_API_KEY not set in environment")
            print("   Please set it with: $env:GEMINI_API_KEY='your_key'")
            print("   Get a free key at: https://ai.google.dev")
            return
        
        print(f"   Gemini API Key: {config.gemini_api_key[:10]}...")
        print()
        
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return
    
    # Step 1: Analyze sentiment with AI
    print("🤖 Step 1: AI Sentiment Analysis")
    print("-" * 60)
    
    try:
        analyzer = AIAnalyzer(config.gemini_api_key)
        market_question = "Is the sentiment about Bitcoin positive?"
        
        print(f"   Question: {market_question}")
        print(f"   Analyzing with Google Gemini Pro...")
        
        result = analyzer.get_sentiment_analysis(
            text_data=sample_data,
            market_question=market_question
        )
        
        print(f"\n   ✅ Analysis Complete!")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Reasoning: {result['reasoning']}")
        print()
        
    except Exception as e:
        print(f"   ❌ Analysis Error: {e}")
        return
    
    # Step 2: Record on blockchain (if configured)
    print("⛓️  Step 2: Blockchain Recording")
    print("-" * 60)
    
    try:
        if not config.web3_provider_url or not config.private_key:
            print("   ⚠️  Blockchain credentials not configured")
            print("   Skipping blockchain recording (optional)")
            print("   To enable, set WEB3_PROVIDER_URL and PRIVATE_KEY")
            print()
        else:
            blockchain = BlockchainConnector(config)
            print("   Deploying smart contract...")
            
            contract_address = blockchain.deploy_contract()
            print(f"   ✅ Contract deployed: {contract_address[:10]}...{contract_address[-8:]}")
            
            print(f"   Recording outcome: {result['sentiment']}")
            tx_hash = blockchain.record_outcome(contract_address, result['sentiment'])
            print(f"   ✅ Transaction: {tx_hash}")
            print()
            
    except Exception as e:
        print(f"   ⚠️  Blockchain Error: {e}")
        print(f"   (This is optional - sentiment analysis still works!)")
        print()
    
    # Summary
    print("=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Final Result:")
    print(f"   Market Question: Is Bitcoin sentiment positive?")
    print(f"   Sentiment: {result['sentiment']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Reasoning: {result['reasoning']}")
    print()
    print("💡 Next Steps:")
    print("   • Get Reddit API credentials to use real-time data")
    print("   • Try: python run_multi_source_oracle.py --tickers BTC AAPL")
    print("   • Launch web interface: python app.py")
    print()


if __name__ == "__main__":
    main()
