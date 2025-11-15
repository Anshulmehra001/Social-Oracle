# API Configuration Guide

Complete guide for configuring all optional data sources in Social Oracle.

## Required APIs

### Google Gemini AI (Required)

**Purpose:** AI-powered sentiment analysis

**Setup:**
1. Go to https://aistudio.google.com/app/apikey
2. Click **"Create API key in new project"**
3. Copy your API key
4. Add to `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

**Limits:** Free tier provides 60 requests per minute

---

## Optional APIs (Social Media Sources)

All social media APIs are **OPTIONAL**. The system works with just RSS + Hacker News + yfinance if no social APIs are configured.

### X (Twitter) API - OPTIONAL

**Purpose:** Real-time tweets mentioning tickers

**Why add it:** Twitter has the most immediate market reactions and breaking news

**Setup:**
1. Go to https://developer.twitter.com/
2. Apply for API access (free tier available)
3. Create a new app in Developer Portal
4. Get credentials from app dashboard
5. Add to `.env`:

   **Option 1: Bearer Token (Recommended - API v2)**
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

   **Option 2: OAuth 1.0a (API v1.1)**
   ```
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   ```

6. Install dependencies:
   ```bash
   pip install tweepy
   ```

**Limits:** Free tier - 500k tweets/month

---

### Reddit API - OPTIONAL

**Purpose:** Discussions from r/stocks, r/wallstreetbets, etc.

**Why add it:** Detailed analysis and sentiment from retail investors

**Setup:**
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" type
4. Fill in name and redirect URI (use http://localhost:8080)
5. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=YourApp/1.0 by YourUsername
   ```

6. Install dependencies:
   ```bash
   pip install praw
   ```

**Limits:** 60 requests per minute

---

### Stocktwits API - OPTIONAL

**Purpose:** Financial social network focused on stocks

**Why add it:** Stock-specific community sentiment

**Setup:**
Stocktwits works without authentication using public endpoints. No setup required!

**Note:** For higher rate limits, you can register at https://stocktwits.com/developers

---

## Data Sources Summary

| Source | Required | Setup Difficulty | Update Frequency | Coverage |
|--------|----------|-----------------|------------------|----------|
| RSS News | ✅ Yes | None | Real-time | Global news |
| Hacker News | ✅ Yes | None | Real-time | Tech companies |
| yfinance | ✅ Yes | None | Real-time | Price data |
| Google Gemini | ✅ Yes | Easy | N/A | AI analysis |
| X (Twitter) | ⚪ Optional | Medium | Real-time | Social sentiment |
| Reddit | ⚪ Optional | Easy | Real-time | Community analysis |
| Stocktwits | ⚪ Optional | None | Real-time | Stock-focused |

---

## Testing Your Configuration

After adding API credentials, test them:

```bash
python validate_config.py
```

This will show which data sources are active and working.

---

## Environment Variables Template

Create or update your `.env` file with these variables:

```bash
# Required
GEMINI_API_KEY=your_gemini_key_here

# Optional - X/Twitter (choose one method)
TWITTER_BEARER_TOKEN=your_bearer_token
# OR
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Optional - Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=YourApp/1.0 by YourUsername

# Optional - Blockchain (for recording results on-chain)
BLOCKCHAIN_ENABLED=false
PRIVATE_KEY=your_private_key_if_using_blockchain
CONTRACT_ADDRESS=your_contract_address_if_deployed
```

---

## Recommended Minimum Setup

**For testing/demo:**
- Gemini API only
- Uses RSS + Hacker News + yfinance + sample data

**For production/hackathon:**
- Gemini API (required)
- Twitter API (recommended for real-time social sentiment)
- Reddit API (recommended for community analysis)

---

## Troubleshooting

### "No data found for ticker"
- Check if ticker symbol is correct (use Yahoo Finance format)
- Try increasing time window (e.g., 48 or 72 hours)
- Verify at least one data source is working

### "API rate limit exceeded"
- Wait for rate limit to reset (usually 1 minute)
- For Gemini: create new API key in new project
- For Twitter: upgrade to paid tier or reduce query frequency

### "Twitter adapter not enabled"
- Install tweepy: `pip install tweepy`
- Verify credentials in .env file
- Check credentials are valid at https://developer.twitter.com/

### "Reddit adapter not enabled"
- Install praw: `pip install praw`
- Verify credentials in .env file
- Ensure REDDIT_USER_AGENT follows format: "AppName/1.0 by username"

---

## Cost Analysis

| Service | Free Tier | Sufficient For |
|---------|-----------|----------------|
| Gemini AI | 60 req/min | ~3,600 analyses/hour |
| Twitter | 500k tweets/month | ~16k tweets/day |
| Reddit | 60 req/min | ~3,600 searches/hour |
| yfinance | Unlimited | ∞ |
| RSS/HN | Unlimited | ∞ |

**Conclusion:** Free tiers are sufficient for hackathon demos and moderate production use.

---

## Next Steps

1. Copy `.env.example` to `.env`
2. Add your Gemini API key (required)
3. Optionally add Twitter/Reddit credentials
4. Run `python validate_config.py` to test
5. Start the app: `python app.py`
6. Test with a ticker at http://localhost:5000
