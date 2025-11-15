"""
Web interface for Social Oracle - Sentiment Analysis Platform
"""
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from src.data_sources.aggregator import MultiSourceAggregator
from src.ai_analyzer import AIAnalyzer
from src.price_analyzer import PriceAnalyzer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize components with explicit API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment!")
else:
    print(f"✅ Loaded API key: {api_key[:20]}...")

aggregator = MultiSourceAggregator()
analyzer = AIAnalyzer(api_key=api_key)
price_analyzer = PriceAnalyzer()

def _get_chain_info():
    """Infer chain name and explorer from BNB_RPC_URL."""
    rpc = (os.getenv('BNB_RPC_URL') or '').lower()
    # Default
    name = 'BNB Chain'
    explorer = None
    if 'prebsc' in rpc or 'testnet' in rpc:
        name = 'BNB Chain Testnet'
        explorer = 'https://testnet.bscscan.com'
    elif 'bsc-dataseed' in rpc or 'binance.org' in rpc or 'bsc' in rpc:
        name = 'BNB Chain Mainnet'
        explorer = 'https://bscscan.com'
    return {'name': name, 'explorer': explorer}

@app.route('/')
def index():
    """Main page with input form"""
    chain = _get_chain_info()
    return render_template('index.html', chain_name=chain['name'], explorer=chain['explorer'])

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process sentiment analysis request"""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        hours = int(data.get('hours', 24))
        
        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400
        
        # Fetch multi-source data
        print(f"Fetching data for {ticker}...")
        records = aggregator.aggregate([ticker], hours_back=hours)
        
        if ticker not in records or not records[ticker]:
            return jsonify({
                'error': f'No data found for {ticker}',
                'ticker': ticker
            }), 404
        
        # Get enhanced price analysis
        price_context = ""
        price_data = {}
        try:
            price_data = price_analyzer.get_comprehensive_analysis(ticker, days=30)
            price_context = price_analyzer.get_simple_context(ticker, days=5)
        except Exception as e:
            print(f"Price analysis error: {e}")
        
        # Combine all text with price context
        combined_text = "\n\n".join(records[ticker])
        full_text = f"Analyze sentiment for {ticker}:\n\n{combined_text}{price_context}"
        
        # Get AI sentiment
        print(f"Analyzing sentiment...")
        sentiment = analyzer.get_sentiment_analysis(full_text)
        
        # Count sources
        source_counts = aggregator.get_source_stats(ticker)
        
        return jsonify({
            'ticker': ticker,
            'sentiment': sentiment.get('sentiment', 'Unknown'),
            'reasoning': sentiment.get('reasoning', 'No reasoning provided'),
            'confidence': sentiment.get('confidence', 'Unknown'),
            'sources': source_counts,
            'total_records': len(records[ticker]),
            'price_data': {
                'current_price': price_data.get('current_price'),
                'change_5d': price_data.get('price_change_5d'),
                'trend': price_data.get('price_trend'),
                'rsi': price_data.get('rsi_14'),
                'interpretation': price_data.get('interpretation')
            },
            'price_context': price_context.strip(),
            'reasoning': sentiment.get('reasoning', 'No reasoning provided'),
            'sources': source_counts,
            'total_records': len(records[ticker]),
            'price_context': price_context.strip(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Check for required API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY not set. AI analysis will fail.")
    
    print("🚀 Starting Social Oracle Web Interface...")
    print("📊 Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
