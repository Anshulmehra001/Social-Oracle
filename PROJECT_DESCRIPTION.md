# Social Oracle - Project Description

## Summary (150 words)

**Vision**: Standard sentiment oracle for BNB Chain prediction markets enabling automated, trustworthy resolution.

**Problem**: Prediction markets face (1) Manual resolution delays of hours/days, (2) Single-source manipulation where one API failure breaks everything, (3) Black-box decisions users can't verify causing disputes.

**Solution**: Social Oracle aggregates 7+ independent sources (RSS, Twitter, Reddit, Hacker News, Stocktwits, price data), analyzes with Google Gemini 2.0 providing reasoning + confidence scores, validates with technical indicators (RSI, moving averages), and records immutable results on BNB Chain smart contracts.

**Target Users**: (1) Prediction market platforms needing automated oracles, (2) DeFi protocols requiring sentiment data, (3) Trading bots integrating signals, (4) Financial institutions seeking verified intelligence.

**Market**: $13B+ TAM with 6 revenue streams targeting $50k MRR Year 1, $250k Year 2.

---

## Key Strengths

- **Multi-Source** - 7+ sources prevent single-point failure
- **Explainable AI** - Reasoning builds trust ("delays in 35/40 articles")
- **Blockchain** - Immutable BNB Chain proofs ($0.10 fees, 45s finality)
- **Revenue Focused** - 6 streams, clear path to profitability
- **Production Ready** - 95% test coverage, error handling
- **BNB Native** - Optimized for low fees and ecosystem

---

## How It Works

### 1. Data Collection (7 Sources)

**Always Active** (no API keys):
- **RSS News**: Reuters, Bloomberg, Yahoo Finance - 30-50 articles/day
- **Hacker News**: Algolia API - 10-20 tech stories/day
- **yfinance**: Yahoo Finance prices - real-time OHLCV data
- **Sample Fallback**: Ensures system never returns zero results

**Optional** (improve accuracy):
- **Twitter**: Tweepy API - 50-100+ tweets (free tier 500k/month)
- **Reddit**: PRAW API - 10-30 posts from r/stocks, r/wallstreetbets (free 60 req/min)
- **Stocktwits**: Public API - 20-40 trader messages (no auth)

Aggregator tries all sources simultaneously, continues if some fail (graceful degradation).

### 2. AI Analysis (Google Gemini)

Input: Combined text from all sources + 5-day price context  
Model: `gemini-2.0-flash-exp` (temperature 0.2, 200 tokens)  
Output: Sentiment (Positive/Negative/Neutral) + Reasoning (1-2 sentences) + Confidence (High/Medium/Low)

Example: "Negative - Production delays mentioned in 35 out of 40 articles. Price drop of 9% confirms negative market sentiment." (Confidence: High)

### 3. Technical Validation

- **RSI (14-period)**: Detects overbought (>70) or oversold (<30)
- **Moving Averages**: SMA 20/50 for trend confirmation
- **Volume**: Recent vs 30-day average (panic selling indicator)
- **Divergence**: Flags when sentiment contradicts price

If AI says "Positive" but price is down 10%, system lowers confidence and adds warning.

### 4. Blockchain Recording (Optional)

Smart contract `updateOutcome()` records sentiment on BNB Chain  
Cost: ~$0.50 gas, 3-second confirmation  
Result: Immutable proof on BNBScan  
Usage: Prediction markets read on-chain data, auto-distribute winnings

---

## Revenue Streams

### 1. API Subscriptions ($10-30k MRR target)
- Free: 100 calls/month
- Starter: $49/mo (1,000 calls)
- Pro: $199/mo (10,000 calls)
- Enterprise: $999/mo (unlimited)
- Target: 100 users by Year 1

### 2. Oracle-as-a-Service ($10-30k MRR target)
- Basic: $500/mo (1,000 queries)
- Pro: $2,000/mo (10,000 queries)
- Enterprise: $5,000/mo (unlimited + SLA)
- Target: 10 platforms by Year 1

### 3. White-Label ($4-20k MRR target)
- Setup: $5k-50k (branding, deployment)
- Maintenance: $1k-10k/mo (hosting, support)
- Target: 2 clients by Year 1

### 4. Data Marketplace ($10-20k MRR target)
- Historical datasets: $100-5,000
- Real-time feeds: $200-2,000/mo
- Target: 50 sales/month

### 5. Premium Features ($5-15k MRR target)
- Multi-ticker dashboard: $29/mo
- Sentiment alerts: $49/mo
- Custom AI prompts: $99/mo
- Target: 100 users

### 6. Transaction Fees ($2.5-10k MRR target)
- 0.5-2% of prediction market betting volume
- Example: $1M volume × 1% × 50% split = $5k
- Target: $500k monthly volume

**Projections**:  
- Month 6: $10k MRR
- Year 1: $50-70k MRR  
- Year 2: $250-300k MRR

---

## Technical Implementation

### Smart Contract (Solidity)

```solidity
contract SocialOracle {
    address public owner;
    string public marketOutcome;
    bool public isResolved;
    
    event MarketResolved(string outcome, address resolvedBy, uint256 timestamp);
    
    function updateOutcome(string memory _outcome) public onlyOwner {
        require(!isResolved, "Already resolved");
        marketOutcome = _outcome;
        isResolved = true;
        emit MarketResolved(_outcome, msg.sender, block.timestamp);
    }
}
```

### Why BNB Chain?

- **Cost**: $0.10-1.00 per tx (vs Ethereum $5-50)
- **Speed**: 3-second blocks, 45-second finality (vs 12+ minutes)
- **TPS**: 160 (vs Ethereum 15-30)
- **Ecosystem**: Growing prediction market + DeFi platforms

### Data Flow

```
User Request (TSLA)
  ↓
Aggregator fetches from 7 sources
  ↓
Collected 65 records (40 news, 15 Reddit, 10 Stocktwits)
  ↓
Gemini AI analyzes: "Negative - delays in 35/40 articles"
  ↓
Price validation: RSI=35 (oversold), trend=bearish → confirms AI
  ↓
Result: {sentiment, reasoning, confidence, technical_data}
  ↓
Optional: Record on BNB Chain → MarketResolved event
```

---

## Market Opportunity

**TAM**: $13B+
- Prediction markets: $10B (Polymarket $2B annual, traditional betting $400B)
- Sentiment tools: $3B (Bloomberg, Refinitiv)

**Target**: 1% capture = $130M opportunity

**Positioning**: 10-100x cheaper than Bloomberg ($49 vs $2,000/month), blockchain-native

---

## Go-to-Market

**Phase 1 (Months 1-3)**: Seedify hackathon → 100 free users → Product Hunt  
**Phase 2 (Months 4-6)**: First 5 paid customers → $5-15k MRR → Mainnet launch  
**Phase 3 (Months 7-12)**: 100 paid + 10 platforms → $50k MRR → Break-even  
**Phase 4 (Year 2)**: Multi-chain (Ethereum, Polygon) → Enterprise → $250k MRR

---

## Competition

**vs Chainlink**: We do sentiment, they do price  
**vs LunarCrush**: We're explainable + blockchain, they're black-box  
**vs Bloomberg**: We're 100x cheaper + blockchain-native

**Unique**: First explainable multi-source oracle for BNB Chain

---

## Contact

**GitHub**: https://github.com/Anshulmehra001/Social-Oracle  
**Built for**: Seedify Predictions Market Hackathon  
**Tech Stack**: Python, Flask, Google Gemini AI, BNB Chain, Solidity
