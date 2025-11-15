# 🔮 Social Oracle

**Multi-source AI sentiment oracle for BNB Chain prediction markets**

[![GitHub](https://img.shields.io/badge/GitHub-Social--Oracle-blue)](https://github.com/Anshulmehra001/Social-Oracle) [![BNB Chain](https://img.shields.io/badge/BNB-Chain-yellow)](https://www.bnbchain.org/)

## Overview

Automates prediction market resolution by aggregating sentiment from multiple sources, analyzing with Google Gemini AI, and recording results on BNB Chain.

**Problem**: Manual resolution delays, single-source risks, no transparency  
**Solution**: 7+ sources → AI analysis → Blockchain verification

## Quick Start

```bash
git clone https://github.com/Anshulmehra001/Social-Oracle.git
cd Social-Oracle
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env  # Get at https://aistudio.google.com/app/apikey
python app.py  # Visit http://localhost:5000
```

## Key Features

**Multi-Source Aggregation**
- RSS news (30-50 articles/day)
- Reddit (10-30 posts)
- Twitter (50-100+ tweets, optional)
- Hacker News (10-20 stories)
- Stocktwits (20-40 messages)
- yfinance (real-time prices)
- Graceful degradation if sources fail

**Explainable AI**
- Google Gemini 2.0 Flash
- Sentiment + reasoning + confidence
- Example: "Negative - delays in 35/40 articles" (Confidence: High)

**Technical Validation**
- RSI (overbought/oversold detection)
- Moving averages (trend analysis)
- Volume analysis
- Price-sentiment consistency check

**Blockchain**
- BNB Chain smart contract
- Immutable sentiment proofs
- $0.10-1.00 fees, 45s finality
- Auto-resolves prediction markets

## How It Works

```
1. Data Collection  → 2. AI Analysis    → 3. Technical Check → 4. Blockchain
   (7 sources)         (Gemini 2.0)        (RSI, volume)       (BNB Chain)
   65 records          Sentiment+reason    Validates AI        Immutable proof
```

**Example Flow**:
1. User enters "TSLA"
2. System fetches 65 records (40 news, 15 Reddit, 10 Stocktwits)
3. AI: "Negative - production delays in 35/40 articles, price down 9%" (High confidence)
4. Tech: RSI=35 (oversold), trend=bearish → confirms negative sentiment
5. Result displayed in web UI + optional blockchain recording

## Revenue Model

| Stream | Price | Target |
|--------|-------|--------|
| API Subscriptions | $49-999/mo | $10-30k MRR |
| Oracle-as-a-Service | $500-5k/mo | $10-30k MRR |
| White-Label | $5k setup + $1-10k/mo | $4-20k MRR |
| Data Sales | $100-5k | $10-20k MRR |
| Premium Features | $29-199/mo | $5-15k MRR |
| Transaction Fees | 0.5-2% volume | $2.5-10k MRR |

**Total**: $50k MRR Year 1 → $250k Year 2 | Market: $13B+ TAM

## Smart Contract

```solidity
// contracts/SocialOracle.sol
function updateOutcome(string memory _outcome) public onlyOwner {
    marketOutcome = _outcome;
    isResolved = true;
    emit MarketResolved(_outcome, msg.sender, block.timestamp);
}
```

Deploy: `python deploy_bnb.py`

## API Configuration

**Required**:
- Gemini API (free): https://aistudio.google.com/app/apikey

**Optional** (improves accuracy):
- Twitter: https://developer.twitter.com/ (500k tweets/month free)
- Reddit: https://www.reddit.com/prefs/apps (60 req/min free)

```bash
# .env file
GEMINI_API_KEY=required
TWITTER_BEARER_TOKEN=optional
REDDIT_CLIENT_ID=optional
REDDIT_CLIENT_SECRET=optional
```

## Usage

**Web**: http://localhost:5000 → Enter ticker → View analysis

**Python**:
```python
from src.data_sources.aggregator import MultiSourceAggregator
from src.ai_analyzer import AIAnalyzer

data = MultiSourceAggregator().aggregate_all_sources("TSLA", 24)
result = AIAnalyzer().get_sentiment_analysis(data)
# result = {sentiment, reasoning, confidence, price_data, sources}
```

## Testing

```bash
pytest                    # 95% coverage
python validate_config.py # Validate APIs
```

## Architecture

```
Social-Oracle/
├── app.py                 # Flask web server
├── deploy_bnb.py          # Blockchain deployment
├── contracts/
│   └── SocialOracle.sol   # Solidity contract
├── src/
│   ├── ai_analyzer.py     # Gemini integration
│   ├── price_analyzer.py  # RSI, SMA, volume
│   └── data_sources/
│       ├── aggregator.py  # Coordinator
│       ├── rss_adapter.py
│       ├── reddit_adapter.py
│       ├── twitter_adapter.py
│       └── ...
└── tests/                 # 95% coverage
```

## Why Social Oracle?

✅ Multi-source (prevents manipulation)  
✅ Explainable AI (builds trust)  
✅ BNB Chain native (10-100x cheaper)  
✅ Production ready (95% tests)  
✅ Blockchain verified (immutable)

## Target Users

- Prediction market platforms
- DeFi protocols (sentiment data)
- Trading bots
- Financial institutions

## License

MIT

---

**Seedify Hackathon** | **BNB Chain** | **Google Gemini AI**
