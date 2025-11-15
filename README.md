# 🔮 Social Oracle

**Multi-source AI sentiment oracle for BNB Chain prediction markets**

[![GitHub](https://img.shields.io/badge/GitHub-Anshulmehra001/Social--Oracle-blue)](https://github.com/Anshulmehra001/Social-Oracle)
[![BNB Chain](https://img.shields.io/badge/BNB-Chain-yellow)](https://www.bnbchain.org/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

## 🎯 Overview

Automated sentiment oracle that aggregates 7+ data sources (RSS, Twitter, Reddit, Hacker News, Stocktwits, price data), analyzes with explainable AI (Google Gemini 2.0), and records results on BNB Chain for trustless prediction market resolution.

**Problem**: Manual resolution delays, single-source manipulation, no transparency  
**Solution**: Multi-source aggregation + AI reasoning + technical validation + blockchain verification  
**Market**: $13B+ TAM, targeting $50k MRR by Year 1

## 🏆 Key Strengths

- **🌐 Multi-Source Intelligence** - 7+ sources prevent manipulation
- **🧠 Explainable AI** - Provides reasoning, not just classification
- **⛓️ Blockchain Verified** - Immutable on-chain proofs
- **💰 Revenue Focused** - 6 streams, clear projections
- **✅ Production Ready** - 95% test coverage, error handling
- **🟡 BNB Chain Native** - Low fees ($0.10 vs $5-50), 45s finality

## 🚀 Quick Start

```bash
# 1. Clone & Install
git clone https://github.com/Anshulmehra001/Social-Oracle.git
cd Social-Oracle
pip install -r requirements.txt

# 2. Configure (get key at https://aistudio.google.com/app/apikey)
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Run
python app.py
# Open http://localhost:5000
```

## ✨ Features

**Multi-Source Aggregation**
- RSS news feeds (financial outlets)
- Reddit (r/stocks, r/wallstreetbets)
- Twitter/X (real-time social sentiment)
- Hacker News (tech discussions)
- Stocktwits (trader sentiment)
- yfinance (price data)
- Graceful degradation if sources fail

**AI Analysis**
- Google Gemini 2.0 Flash
- Sentiment + reasoning + confidence
- Explainable decisions (builds trust)

**Technical Analysis**
- RSI (14-period)
- Moving averages (SMA 20/50)
- Volume trends
- Price validation

**Blockchain Integration**
- BNB Chain smart contract
- Immutable sentiment records
- Auto-resolves prediction markets
- Transparent audit trail

## 💰 Revenue Model

| Stream | Price | Target |
|--------|-------|--------|
| API Subscriptions | $49-999/mo | $10-30k MRR |
| Oracle-as-a-Service | $500-5k/mo | $10-30k MRR |
| White-Label | $5k-50k setup | $4-20k MRR |
| Data Marketplace | $100-5k/product | $10-20k MRR |
| Premium Features | $29-199/mo | $5-15k MRR |
| Transaction Fees | 0.5-2% volume | $2.5-10k MRR |

**Total Target**: $50k MRR by Year 1, $250k by Year 2

## 🏗️ Architecture

```
User Request → Multi-Source Aggregation → AI Analysis → Technical Validation → Blockchain Recording

Data Sources:      AI Processing:        Price Context:       Smart Contract:
- RSS News         Gemini 2.0           - RSI calculation    - updateOutcome()
- Reddit           Sentiment            - Moving averages    - MarketResolved
- Twitter          Reasoning            - Volume trends      - BNBScan proof
- Hacker News      Confidence           - Trend analysis
- Stocktwits
- yfinance
```

## ⛓️ Blockchain Integration

**Smart Contract**: `contracts/SocialOracle.sol`

```solidity
function updateOutcome(string memory _outcome) public onlyOwner {
    require(!isResolved, "Already resolved");
    marketOutcome = _outcome;
    isResolved = true;
    emit MarketResolved(_outcome, msg.sender);
}
```

**Why BNB Chain?**
- Low fees: $0.10-1.00 (vs Ethereum $5-50)
- Fast finality: 45 seconds (vs 12+ minutes)
- High throughput: 160 TPS
- Growing prediction market ecosystem

**Deploy**: `python deploy_bnb.py`

## 🔧 API Configuration

**Required**:
- Gemini API (free): https://aistudio.google.com/app/apikey

**Optional** (improves accuracy):
- Twitter Bearer Token: https://developer.twitter.com/
- Reddit API: https://www.reddit.com/prefs/apps

Add to `.env`:
```bash
GEMINI_API_KEY=your_key
TWITTER_BEARER_TOKEN=optional
REDDIT_CLIENT_ID=optional
REDDIT_CLIENT_SECRET=optional
```

## 📊 Usage

**Web Interface**:
```bash
python app.py
# Visit http://localhost:5000
# Enter ticker (TSLA, AAPL, BTC-USD)
```

**Python API**:
```python
from src.data_sources.aggregator import MultiSourceAggregator
from src.ai_analyzer import AIAnalyzer

# Fetch data
aggregator = MultiSourceAggregator()
data = aggregator.aggregate_all_sources("TSLA", hours_back=24)

# Analyze sentiment
analyzer = AIAnalyzer()
result = analyzer.get_sentiment_analysis(data)

print(result['sentiment'])    # Positive/Negative/Neutral
print(result['reasoning'])    # AI explanation
print(result['confidence'])   # High/Medium/Low
```

## 🧪 Testing

```bash
# Run all tests (95% coverage)
pytest

# Validate configuration
python validate_config.py

# Integration test
python tests/test_main_integration.py
```

## 🚢 Deployment

**Local Development**:
```bash
python app.py
```

**Production** (Gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Docker**:
```bash
docker build -t social-oracle .
docker run -p 5000:5000 --env-file .env social-oracle
```

**BNB Chain**:
```bash
python deploy_bnb.py
# Follow prompts for testnet/mainnet
```

## 📁 Project Structure

```
Social-Oracle/
├── README.md                    # This file
├── PROJECT_DESCRIPTION.md       # Detailed business doc
├── app.py                       # Flask web server
├── deploy_bnb.py               # Blockchain deployment
├── requirements.txt
├── contracts/
│   └── SocialOracle.sol        # Smart contract
├── src/
│   ├── ai_analyzer.py          # Gemini integration
│   ├── price_analyzer.py       # Technical analysis
│   └── data_sources/
│       ├── aggregator.py       # Multi-source coordinator
│       ├── twitter_adapter.py
│       ├── reddit_adapter.py
│       └── ... (7 adapters)
├── tests/                      # 95% coverage
└── templates/
    └── index.html              # Web UI
```

## 🎯 Target Users

1. **Prediction Market Platforms** - Automated oracle for market resolution
2. **DeFi Protocols** - Sentiment data for derivatives/options
3. **Trading Bots** - Real-time sentiment signals
4. **Financial Institutions** - Verified market intelligence

## 🔒 Security & Performance

- ✅ Input validation and sanitization
- ✅ Rate limiting on APIs
- ✅ Error handling with graceful degradation
- ✅ Secure environment variable management
- ✅ Smart contract access control
- ✅ 95% test coverage
- ✅ Logging for audit trails

**Performance**:
- Response time: <2 seconds
- Handles 100+ concurrent requests
- 99.9% uptime target

## 📝 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📞 Contact

**GitHub**: https://github.com/Anshulmehra001/Social-Oracle  
**Issues**: https://github.com/Anshulmehra001/Social-Oracle/issues

---

**Built for Seedify Predictions Market Hackathon** | **Powered by BNB Chain** | **AI by Google Gemini**
