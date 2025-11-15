"""
Social Oracle - Using 100% FREE Data Sources
No paid APIs required - perfect for hackathon demo!
"""

import feedparser
import requests
from src.ai_analyzer import AIAnalyzer
from src.blockchain_connector import BlockchainConnector
from src.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_free_crypto_news(topic="bitcoin", limit=20):
    """
    Fetch crypto news from FREE RSS feeds.
    No API keys needed, completely free!
    """
    print(f"📰 Fetching free news about {topic}...")
    
    # Free crypto news RSS feeds
    feeds = [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cryptonews.com/news/feed/",
    ]
    
    all_articles = []
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:limit]:
                if topic.lower() in entry.title.lower() or topic.lower() in entry.get('summary', '').lower():
                    all_articles.append(
                        f"Title: {entry.title}\n"
                        f"Content: {entry.get('summary', 'No summary')}\n"
                    )
        except Exception as e:
            logger.warning(f"Could not fetch from {feed_url}: {e}")
            continue
    
    if all_articles:
        print(f"   ✅ Found {len(all_articles)} relevant articles")
        return "\n".join(all_articles)
    else:
        # Fallback to sample data if RSS fails
        return get_sample_crypto_data(topic)


def fetch_from_hacker_news(topic="bitcoin"):
    """
    Fetch from Hacker News API - 100% FREE
    No authentication required!
    """
    print(f"🔍 Searching Hacker News for {topic}...")
    
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={topic}&tags=story&hitsPerPage=15"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            hits = data.get('hits', [])
            
            articles = []
            for hit in hits:
                title = hit.get('title', '')
                text = hit.get('story_text', '') or ''
                if title:
                    articles.append(f"Title: {title}\nContent: {text}\n")
            
            if articles:
                print(f"   ✅ Found {len(articles)} discussions")
                return "\n".join(articles)
    
    except Exception as e:
        logger.warning(f"Hacker News error: {e}")
    
    return get_sample_crypto_data(topic)


def get_sample_crypto_data(topic="bitcoin"):
    """
    High-quality sample data for demo purposes.
    Always works, no API needed!
    """
    print(f"   ℹ️  Using curated sample data for {topic}")
    
    samples = {
        "bitcoin": """
Title: Bitcoin Price Analysis Shows Strong Bullish Momentum
Content: Technical analysts report Bitcoin showing resilience at key support levels around $42,000. 
On-chain metrics indicate growing institutional accumulation and decreased exchange reserves.

Comment: Very bullish on BTC long-term. Fundamentals are stronger than ever.
Comment: The institutional adoption narrative is playing out beautifully.
Comment: Hash rate at all-time highs shows network security improving.
Comment: Positive outlook based on multiple technical indicators.
Comment: Market sentiment shifting from fear to optimism.

Title: Bitcoin Network Fundamentals Reach New Heights
Content: Bitcoin's hash rate hits record levels while transaction fees remain low. 
Lightning Network capacity continues to grow, improving scalability.

Comment: These fundamentals support a positive price outlook.
Comment: Technology improvements making Bitcoin more practical.
Comment: Long-term holders continue to accumulate.
Comment: Market confidence returning after recent volatility.
Comment: Bullish trend confirmed by multiple metrics.

Title: Institutional Interest in Bitcoin Grows
Content: Major financial institutions announce expanded Bitcoin services.
Survey shows increased allocation to digital assets by wealth managers.

Comment: This institutional adoption is exactly what we needed.
Comment: Traditional finance finally embracing Bitcoin.
Comment: Positive regulatory clarity helping adoption.
Comment: Sentiment among institutional investors very positive.
Comment: Long-term bullish case strengthening.
""",
        "ethereum": """
Title: Ethereum Network Upgrade Exceeds Expectations
Content: Recent Ethereum upgrade successfully improves network efficiency and reduces gas costs.
Developer activity on Ethereum reaches new all-time highs.

Comment: Very optimistic about ETH's future prospects.
Comment: The technical improvements are game-changing.
Comment: DeFi activity on Ethereum accelerating rapidly.
Comment: Positive sentiment across developer community.
Comment: Bullish on ETH fundamentals and adoption.

Title: Ethereum DeFi Ecosystem Shows Strong Growth
Content: Total value locked in Ethereum DeFi protocols increases 25% this quarter.
New innovative projects launching exclusively on Ethereum.

Comment: DeFi growth is a major positive catalyst for ETH.
Comment: Network effects strengthening Ethereum's position.
Comment: Market sentiment very positive on ETH.
Comment: Technical analysis supports upward trend.
Comment: Long-term outlook remains bullish.

Title: Enterprise Adoption of Ethereum Increasing
Content: Fortune 500 companies exploring Ethereum for supply chain solutions.
Enterprise Ethereum Alliance membership grows to over 200 organizations.

Comment: Enterprise adoption validates Ethereum technology.
Comment: Positive developments for long-term value.
Comment: Market confidence in ETH growing.
Comment: Bullish outlook based on fundamentals.
Comment: Optimistic about Ethereum's future role.
""",
        "crypto": """
Title: Cryptocurrency Market Shows Signs of Recovery
Content: Market sentiment improves as regulatory clarity increases globally.
Multiple altcoins showing strong technical breakout patterns.

Comment: Overall crypto market sentiment improving significantly.
Comment: Positive developments across multiple projects.
Comment: Optimistic about the direction of the market.
Comment: Bullish technical indicators across the board.
Comment: Market confidence returning after consolidation.

Title: Blockchain Technology Adoption Accelerates
Content: Major corporations announce blockchain integration plans.
Government initiatives exploring blockchain for public services.

Comment: Technology validation driving positive sentiment.
Comment: Long-term outlook for crypto remains strong.
Comment: Market maturing and attracting serious investors.
Comment: Bullish on the future of blockchain technology.
Comment: Positive trends in adoption and development.

Title: Crypto Payment Adoption Growing Rapidly
Content: Major retailers announce cryptocurrency payment acceptance.
Crypto debit cards seeing increased usage and merchant acceptance.

Comment: Real-world utility driving positive sentiment.
Comment: Adoption metrics very encouraging.
Comment: Bullish on payments use case.
Comment: Market sentiment improving with utility growth.
Comment: Optimistic about mainstream adoption trends.
"""
    }
    
    return samples.get(topic.lower(), samples["bitcoin"])


def main():
    """
    Run Social Oracle with 100% FREE data sources.
    No Reddit, Twitter, or any paid API needed!
    """
    
    print("\n" + "="*70)
    print("🔮 SOCIAL ORACLE - 100% FREE VERSION")
    print("    No Paid APIs Required!")
    print("="*70 + "\n")
    
    try:
        # Configuration
        config = Config.get_api_config()
        topic = "bitcoin"
        market_question = f"Is the {topic} market sentiment positive?"
        
        # Step 1: Fetch data from FREE sources
        print("📱 Step 1: Collect Social Data (FREE Sources)")
        print("-" * 70)
        
        # Try free sources in order of preference
        data = None
        
        # Try RSS feeds first
        try:
            data = fetch_free_crypto_news(topic)
        except:
            pass
        
        # Try Hacker News as backup
        if not data or len(data) < 100:
            try:
                data = fetch_from_hacker_news(topic)
            except:
                pass
        
        # Use sample data as final fallback
        if not data or len(data) < 100:
            data = get_sample_crypto_data(topic)
        
        print(f"✅ Collected {len(data)} characters of data\n")
        
        # Step 2: AI Analysis
        print("🤖 Step 2: AI Sentiment Analysis")
        print("-" * 70)
        print(f"   Market Question: {market_question}")
        print("   Using Google Gemini Pro (FREE tier)...")
        
        analyzer = AIAnalyzer(config.gemini_api_key)
        sentiment = analyzer.get_sentiment_analysis(
            text_data=data,
            market_question=market_question
        )
        
        print(f"   ✅ AI Analysis Result: {sentiment}\n")
        
        # Step 3: Blockchain Recording
        print("⛓️  Step 3: Blockchain Recording")
        print("-" * 70)
        print("   Deploying smart contract to BNB Testnet (FREE)...")
        
        blockchain = BlockchainConnector(config)
        contract_address = blockchain.deploy_contract()
        
        print(f"   ✅ Contract deployed: {contract_address}")
        print("   Recording outcome on blockchain...")
        
        tx_hash = blockchain.record_outcome(contract_address, sentiment)
        
        print(f"   ✅ Transaction hash: {tx_hash}\n")
        
        # Step 4: Verification
        print("🔍 Step 4: Verification")
        print("-" * 70)
        explorer_url = f"https://testnet.bscscan.com/tx/{tx_hash}"
        print(f"   View transaction: {explorer_url}\n")
        
        # Final Summary
        print("="*70)
        print("✅ SOCIAL ORACLE COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 Results Summary:")
        print(f"   Topic: {topic}")
        print(f"   Market Question: {market_question}")
        print(f"   AI Sentiment: {sentiment}")
        print(f"   Smart Contract: {contract_address}")
        print(f"   Transaction: {tx_hash}")
        print(f"\n   🔗 Verify on BscScan: {explorer_url}")
        
        print("\n" + "="*70)
        print("💰 Total Cost: $0.00 - Everything is FREE!")
        print("="*70)
        print("\n✅ Data Source: Free RSS feeds / Sample data (no API key)")
        print("✅ AI Analysis: Google Gemini (free tier)")
        print("✅ Blockchain: BNB Testnet (free test BNB)")
        print("\n🎉 Perfect for hackathon demo - no paid APIs needed!\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error occurred: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check GEMINI_API_KEY in .env file")
        print("   2. Check PRIVATE_KEY in .env file")
        print("   3. Ensure you have test BNB in wallet")
        print("   4. Try: pip install feedparser requests")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
