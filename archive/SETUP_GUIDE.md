# Social Oracle Setup Guide

## 🚀 Quick Start Guide

Social Oracle is a decentralized prediction market oracle that uses AI to analyze social media sentiment and records outcomes on the BNB Chain blockchain.

---

## 📋 Prerequisites

- **Python 3.8+** installed
- **BNB Chain testnet** account with test BNB
- **API Keys** (detailed below)
- **Git** (optional, for cloning)

---

## 🔧 Installation

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd social-oracle
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration

### 1. Get Required API Keys

#### **Reddit API** (for social media data)
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - Name: Your app name
   - App type: Select "script"
   - Redirect URI: http://localhost:8080
4. Save `client_id` and `client_secret`

#### **Google Gemini API** (for AI analysis)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Save the API key

#### **BNB Chain Setup** (for blockchain)
1. Install MetaMask or another Web3 wallet
2. Add BNB Testnet network:
   - Network Name: BNB Smart Chain Testnet
   - RPC URL: https://data-seed-prebsc-1-s1.binance.org:8545/
   - Chain ID: 97
   - Currency Symbol: tBNB
   - Block Explorer: https://testnet.bscscan.com
3. Get test BNB from: https://testnet.bnbchain.org/faucet-smart
4. Export your private key from MetaMask

### 2. Create Environment File

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=SocialOracle/1.0

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# BNB Chain Configuration
BNB_RPC_URL=https://data-seed-prebsc-1-s1.binance.org:8545/
PRIVATE_KEY=your_private_key_here_without_0x_prefix
```

⚠️ **IMPORTANT**: Never commit your `.env` file or share your private keys!

---

## 🎯 Usage

### Basic Usage

Run the main application:

```bash
python main.py
```

The system will:
1. Fetch social media data from Reddit
2. Analyze sentiment using AI
3. Deploy a smart contract to BNB Chain
4. Record the outcome on blockchain

### Advanced Usage

#### Custom Query

```python
from src.social_fetcher import SocialMediaFetcher
from src.ai_analyzer import AIAnalyzer
from src.blockchain_connector import BlockchainConnector
from src.config import Config

# Load configuration
config = Config.get_api_config()

# 1. Fetch social data
fetcher = SocialMediaFetcher(config)
data = fetcher.fetch_reddit_sentiment_data(
    keywords="cryptocurrency market",
    subreddit="cryptocurrency",
    limit=50
)

# 2. Analyze sentiment
analyzer = AIAnalyzer(config.gemini_api_key)
sentiment = analyzer.get_sentiment_analysis(
    text_data=data,
    market_question="Is the cryptocurrency market sentiment positive?"
)

print(f"Sentiment: {sentiment}")

# 3. Record on blockchain
blockchain = BlockchainConnector(config)
contract_address = blockchain.deploy_contract()
tx_hash = blockchain.record_outcome(contract_address, sentiment)
print(f"Transaction: {tx_hash}")
```

#### Quick Run Script

Use the convenience script:

```bash
python run_oracle.py
```

---

## 🧪 Testing

Run all tests:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ai_analyzer.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📁 Project Structure

```
social-oracle/
├── src/                          # Core source code
│   ├── __init__.py
│   ├── ai_analyzer.py           # AI sentiment analysis
│   ├── blockchain_connector.py  # Blockchain integration
│   ├── config.py                # Configuration management
│   └── social_fetcher.py        # Social media data fetching
├── contracts/                    # Smart contracts
│   ├── SocialOracle.sol         # Main oracle contract
│   └── test/                    # Contract tests
├── tests/                        # Python tests
│   ├── test_ai_analyzer.py
│   ├── test_blockchain_connector.py
│   ├── test_social_fetcher.py
│   └── test_main_integration.py
├── main.py                       # Main application entry
├── run_oracle.py                 # Quick run script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── README.md                     # Project documentation
├── SETUP_GUIDE.md               # This file
└── USAGE_GUIDE.md               # Detailed usage guide
```

---

## 🔍 How It Works

### 1. Social Media Data Collection
- Fetches posts and comments from Reddit using PRAW library
- Searches specific subreddits with keywords
- Handles rate limiting and errors gracefully

### 2. AI Sentiment Analysis
- Uses Google Gemini Pro AI model
- Analyzes collected text data
- Returns: Positive, Negative, or Neutral sentiment

### 3. Blockchain Recording
- Deploys smart contract to BNB Chain
- Records sentiment outcome immutably
- Provides transaction hash for verification

---

## 🛠️ Troubleshooting

### Common Issues

#### "Module not found" error
```bash
pip install -r requirements.txt --upgrade
```

#### "Invalid API key" error
- Double-check your `.env` file
- Ensure no extra spaces or quotes
- Verify keys are active

#### "Insufficient funds" error
- Get test BNB from faucet
- Check wallet balance on testnet explorer

#### "Connection timeout" error
- Check internet connection
- Verify RPC URL is correct
- Try alternative RPC endpoint

### Getting Help

1. Check the [USAGE_GUIDE.md](USAGE_GUIDE.md)
2. Review test files for examples
3. Check logs for detailed error messages

---

## 🎓 API Rate Limits

- **Reddit API**: 60 requests/minute
- **Gemini API**: Varies by tier (free tier: 60 requests/minute)
- **BNB Chain**: No strict limit on testnet

The application handles rate limiting automatically with retry logic.

---

## 🔐 Security Best Practices

1. **Never commit** `.env` file
2. **Never share** private keys
3. **Use testnet** for development
4. **Rotate keys** regularly
5. **Keep dependencies** updated

---

## 📊 Example Output

```
[INFO] Starting Social Oracle System...
[INFO] Fetching Reddit data for 'ethereum price prediction'...
[INFO] Successfully fetched 50 posts with 342 comments
[INFO] Analyzing sentiment with AI...
[INFO] AI Analysis Result: Positive
[INFO] Deploying smart contract to BNB Chain...
[INFO] Contract deployed at: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
[INFO] Recording outcome on blockchain...
[INFO] Transaction successful: 0xabc123...
[INFO] View on Explorer: https://testnet.bscscan.com/tx/0xabc123...
```

---

## 🚀 Production Deployment

For production use:

1. Use mainnet RPC URL
2. Secure environment variables
3. Implement proper logging
4. Add monitoring and alerts
5. Consider using API key rotation
6. Implement caching for API calls

---

## 📝 License

This project is for educational and hackathon purposes.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

## 📧 Support

For issues or questions:
- Check documentation
- Review test cases
- Check error logs

---

**Happy Building! 🎉**
