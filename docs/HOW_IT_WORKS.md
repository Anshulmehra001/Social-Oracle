# How It Works

## Overview

Social Oracle collects data from 7+ sources → analyzes with AI → validates with price data → records on blockchain.

---

## Step 1: Multi-Source Data Collection

**Always Active** (no API keys needed):

1. **RSS News Feeds**
   - Sources: Reuters, Bloomberg, Yahoo Finance
   - Volume: 30-50 articles per ticker per day
   - Library: `feedparser` (Python)
   - Example: "Tesla announces Q4 earnings miss" from Reuters

2. **Hacker News**
   - Source: Algolia public API
   - Volume: 10-20 tech stories per day
   - No authentication required
   - Example: "Why Tesla's FSD is fundamentally flawed" (150+ comments)

3. **yfinance**
   - Source: Yahoo Finance data
   - Data: Real-time price, OHLCV, historical trends
   - Used for technical analysis validation

4. **Sample Fallback**
   - Provides 5-10 generic records if all APIs fail
   - Ensures system never returns empty results

**Optional** (improve accuracy if configured):

5. **Twitter/X API**
   - Volume: 50-100+ tweets per popular ticker
   - Search: `$TSLA OR #TSLA OR @tesla`
   - Free tier: 500,000 tweets/month

6. **Reddit API**
   - Subreddits: r/stocks, r/wallstreetbets, r/investing
   - Volume: 10-30 posts with discussions
   - Free tier: 60 requests/minute

7. **Stocktwits**
   - Trader-focused sentiment
   - Volume: 20-40 messages per ticker
   - No authentication needed

**Aggregation Logic**:
```python
for source in [rss, hacker_news, twitter, reddit, stocktwits]:
    try:
        records = source.fetch(ticker, hours_back=24)
        all_data.extend(records)
    except:
        continue  # If one fails, others still work
```

**Result**: 50-200+ text records depending on ticker popularity

---

## Step 2: AI Sentiment Analysis

**Google Gemini 2.0 Flash** analyzes all collected text:

**Input**:
```
Analyze sentiment for TSLA:

[65 combined records from RSS, Reddit, Stocktwits]

Recent 5-day price change: $445 → $404 (-9.18%)

Respond with:
- Sentiment: Positive/Negative/Neutral
- Confidence: High/Medium/Low  
- Reasoning: 1-2 sentence explanation
```

**AI Processing**:
- Model: `gemini-2.0-flash-exp`
- Temperature: 0.2 (consistent results)
- Max tokens: 200 (detailed reasoning)
- Retry: 2 attempts if first fails

**Output Example**:
```json
{
  "sentiment": "Negative",
  "confidence": "High",
  "reasoning": "Production delays mentioned in 35 out of 40 news articles. 
                Reddit discussions focus on supply chain issues. 
                Price drop of 9% confirms market agrees with negative sentiment."
}
```

**Confidence Scoring**:
- **High**: 50+ records, 3+ sources, sentiment matches price trend
- **Medium**: 20-50 records, 2+ sources, or sentiment-price divergence
- **Low**: <20 records, 1 source only, or contradictory data

---

## Step 3: Technical Price Validation

AI sentiment is validated against actual price action:

**Indicators Calculated**:

1. **RSI (Relative Strength Index)**
   - 14-period RSI calculation
   - >70 = overbought (potential reversal down)
   - <30 = oversold (potential reversal up)
   - Confirms momentum direction

2. **Moving Averages**
   - SMA 20 (short-term trend)
   - SMA 50 (medium-term trend)
   - Price above both = bullish, below = bearish

3. **Volume Analysis**
   - Compare recent 3-day volume to 30-day average
   - High volume + negative sentiment = strong conviction
   - Low volume = weak signal

4. **Price Momentum**
   - 1-day, 5-day, 30-day percentage changes
   - Determines if trend is accelerating or decelerating

**Integration**:
```python
if sentiment == "Positive" and price_trend == "bearish":
    confidence = "Medium"  # Divergence detected
    reasoning += " (Warning: Price contradicts sentiment)"
```

**Purpose**: Catches manipulation (e.g., coordinated positive posts but price dropping)

---

## Step 4: Result Synthesis

Combined output returned to user:

```json
{
  "ticker": "TSLA",
  "sentiment": "Negative",
  "reasoning": "Production delays in 35/40 articles. Price confirms.",
  "confidence": "High",
  "price_data": {
    "current_price": 404.35,
    "change_5d": -9.18,
    "rsi": 35.2,
    "trend": "bearish",
    "volume_trend": "increasing"
  },
  "sources": {
    "rss_news": 40,
    "reddit": 15,
    "stocktwits": 10,
    "total": 65
  },
  "timestamp": "2025-11-16T12:34:56Z"
}
```

---

## Step 5: Blockchain Recording (Optional)

**Smart Contract** records sentiment on BNB Chain:

```python
# Connect to BNB Chain
web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

# Call smart contract
contract.functions.updateOutcome("Negative").transact({
    'from': operator_address,
    'gas': 100000
})

# Wait for confirmation (3 seconds)
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
```

**On-Chain Storage**:
- Outcome: "Positive", "Negative", or "Neutral"
- Timestamp: Block timestamp (immutable)
- Event: `MarketResolved(outcome, operator, timestamp)`

**Prediction Market Integration**:
```solidity
// Market reads oracle
string memory outcome = SocialOracle(oracle).marketOutcome();

// Auto-distribute winnings
if (outcome == "Positive") {
    payWinners(positiveBettors);
}
```

**Cost**: ~$0.50 gas fee, 3-second confirmation, 45-second finality

---

## Complete Example Flow

**User Request**: Analyze TSLA sentiment (last 24 hours)

**Step 1**: Collect data
- RSS: 40 articles about production delays
- Reddit: 15 posts discussing supply chain
- Stocktwits: 10 bearish messages
- Price: $445 → $404 (-9.18% in 5 days)
- **Total: 65 records**

**Step 2**: AI analyzes
- Input: 65 records + price context
- Output: "Negative - delays in 35/40 articles, price confirms" (Confidence: High)

**Step 3**: Technical validation
- RSI: 35.2 (oversold)
- SMA 20: $420 (below current)
- Trend: Bearish
- Volume: Increasing (panic selling)
- **Validation**: Confirms negative sentiment

**Step 4**: Return result
- Sentiment: Negative
- Confidence: High
- Technical data included
- Source breakdown shown

**Step 5**: Optional blockchain
- Record "Negative" on BNB Chain
- Gas: $0.50
- Confirmation: 3 seconds
- Event emitted for prediction markets

---

## Why This Approach Works

✅ **Multi-source prevents manipulation** (can't fake 40 news articles + Reddit + price drop)  
✅ **AI provides reasoning** (not just "Negative" - explains why)  
✅ **Price validates AI** (catches coordinated fake sentiment)  
✅ **Blockchain proves it** (immutable record on-chain)  
✅ **Graceful degradation** (if Twitter fails, others continue)
