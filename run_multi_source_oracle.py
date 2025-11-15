"""Run multi-source stock sentiment prediction workflow.

Usage (PowerShell):
    python run_multi_source_oracle.py --tickers AAPL MSFT NVDA --keywords AI chips growth

Optional environment variables for Reddit (already supported). Stocktwits is best-effort.
Falls back to sample + news sources if APIs unavailable.
"""

import argparse
import sys
from typing import List
from src.config import Config
from src.ai_analyzer import AIAnalyzer
from src.data_sources import MultiSourceAggregator
import yfinance as yf


def fetch_price_context(ticker: str) -> str:
    try:
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df.empty:
            return ""
        change = (df['Adj Close'].iloc[-1] / df['Adj Close'].iloc[0]) - 1
        return f"Recent 5d move for {ticker}: {change:.2%}"
    except Exception:
        return ""


def analyze_tickers(tickers: List[str], keywords: List[str], enable_optional: bool) -> None:
    api_config = Config.get_api_config()  # ensures env is loaded
    analyzer = AIAnalyzer(api_key=api_config.gemini_api_key)

    aggregator = MultiSourceAggregator(enable_optional=enable_optional)
    records = aggregator.collect(keywords=keywords, tickers=tickers, per_adapter_limit=40)
    concatenated = aggregator.concatenate_text(records, tickers)

    print("\n=== Multi-Source Sentiment Analysis ===")
    for t in tickers:
        text_blob = concatenated.get(t, "")
        if not text_blob or len(text_blob.strip()) < 50:
            print(f"\n[Ticker: {t}] Insufficient aggregated text; skipping sentiment.")
            continue
        market_question = f"What is the near-term sentiment for {t} based on recent social media and news?"
        try:
            result = analyzer.get_sentiment_analysis(text_blob, market_question)
        except Exception as e:
            print(f"\n[Ticker: {t}] Sentiment analysis failed: {e}")
            continue
        
        # Get price context
        price_ctx = fetch_price_context(t)
        
        # Get source stats
        sources = aggregator.get_source_stats(t)
        
        print(f"\n{'='*60}")
        print(f"Ticker: {t}")
        print(f"{'='*60}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"\nSources:")
        for source, count in sources.items():
            print(f"  • {source}: {count} records")
        print(f"Total Records: {len(text_blob)} characters")
        if price_ctx:
            print(f"\n{price_ctx}")
        
        # Simple naive directional hint
        direction_hint = {
            "Positive": "📈 UP", 
            "Negative": "📉 DOWN", 
            "Neutral": "➡️ SIDEWAYS"
        }.get(result['sentiment'], "❓ UNKNOWN")
        print(f"\nDirectional Hint: {direction_hint}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Multi-source stock sentiment oracle")
    parser.add_argument('--tickers', nargs='+', required=True, help='List of stock tickers, e.g. AAPL MSFT NVDA')
    parser.add_argument('--keywords', nargs='*', default=[], help='Optional filter keywords')
    parser.add_argument('--no-optional', action='store_true', help='Disable optional sources (Stocktwits)')
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers]
    keywords = args.keywords
    analyze_tickers(tickers, keywords, enable_optional=not args.no_optional)
    return 0


if __name__ == '__main__':
    sys.exit(main())
