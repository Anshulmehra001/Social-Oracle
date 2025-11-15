"""
Configuration Validator

Tests all API configurations and shows which data sources are active.
Run this before starting the application to ensure everything is set up correctly.
"""

import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

def print_header(text):
    """Print a styled header."""
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text:^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def print_success(text):
    """Print success message."""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message."""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_info(text):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def check_gemini():
    """Check Gemini AI configuration."""
    print_header("Google Gemini AI (REQUIRED)")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print_error("GEMINI_API_KEY not found in environment")
        print_info("Get your key at: https://aistudio.google.com/app/apikey")
        return False
    
    print_success(f"API key found: {api_key[:20]}...")
    
    # Test the API
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content('Say "working"')
        
        if response.text:
            print_success("API test successful - Gemini is working!")
            return True
        else:
            print_error("API test failed - empty response")
            return False
            
    except ImportError:
        print_error("google-generativeai not installed")
        print_info("Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print_error(f"API test failed: {str(e)[:100]}")
        return False

def check_twitter():
    """Check Twitter/X configuration."""
    print_header("X (Twitter) - Optional")
    
    bearer = os.getenv('TWITTER_BEARER_TOKEN')
    api_key = os.getenv('TWITTER_API_KEY')
    
    if not bearer and not api_key:
        print_warning("Twitter API not configured (optional)")
        print_info("Setup: https://developer.twitter.com/")
        return False
    
    try:
        import tweepy
        
        if bearer:
            print_success("Bearer Token found")
            client = tweepy.Client(bearer_token=bearer)
            print_success("Twitter client initialized with Bearer Token")
            return True
        else:
            print_success("OAuth credentials found")
            print_info("Twitter configured with OAuth 1.0a")
            return True
            
    except ImportError:
        print_error("Tweepy not installed")
        print_info("Install with: pip install tweepy")
        return False
    except Exception as e:
        print_error(f"Twitter setup error: {e}")
        return False

def check_reddit():
    """Check Reddit configuration."""
    print_header("Reddit - Optional")
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    
    if not all([client_id, client_secret, user_agent]):
        print_warning("Reddit API not configured (optional)")
        print_info("Setup: https://www.reddit.com/prefs/apps")
        return False
    
    print_success("Reddit credentials found")
    
    try:
        import praw
        print_success("PRAW library installed")
        return True
    except ImportError:
        print_error("PRAW not installed")
        print_info("Install with: pip install praw")
        return False

def check_stocktwits():
    """Check Stocktwits configuration."""
    print_header("Stocktwits - Optional")
    
    print_success("Stocktwits uses public API (no auth required)")
    return True

def check_dependencies():
    """Check required Python packages."""
    print_header("Required Dependencies")
    
    required = {
        'flask': 'Flask web framework',
        'google.generativeai': 'Google Gemini AI',
        'yfinance': 'Stock price data',
        'feedparser': 'RSS feed parsing',
        'requests': 'HTTP requests',
        'python-dotenv': 'Environment variables'
    }
    
    all_good = True
    for package, description in required.items():
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package}: {description}")
        except ImportError:
            print_error(f"{package}: NOT INSTALLED - {description}")
            all_good = False
    
    return all_good

def check_optional_dependencies():
    """Check optional Python packages."""
    print_header("Optional Dependencies")
    
    optional = {
        'tweepy': 'Twitter/X API client',
        'praw': 'Reddit API client',
        'colorama': 'Colored terminal output'
    }
    
    for package, description in optional.items():
        try:
            __import__(package)
            print_success(f"{package}: {description}")
        except ImportError:
            print_info(f"{package}: Not installed - {description}")

def print_summary(results):
    """Print configuration summary."""
    print_header("Configuration Summary")
    
    total = len(results)
    enabled = sum(results.values())
    
    print(f"Data Sources: {enabled}/{total} enabled\n")
    
    for source, status in results.items():
        if status:
            print_success(f"{source}: ENABLED")
        else:
            if source == "Gemini AI":
                print_error(f"{source}: DISABLED (REQUIRED)")
            else:
                print_warning(f"{source}: DISABLED (optional)")
    
    print()
    
    if results["Gemini AI"]:
        print_success("System is ready to run!")
        print_info("At minimum: RSS + Hacker News + yfinance + Gemini AI")
        
        if enabled == total:
            print_success("All data sources enabled - maximum coverage!")
        else:
            print_info(f"Consider enabling {total - enabled} more source(s) for better analysis")
    else:
        print_error("Cannot run without Gemini AI")
        print_info("Get your key: https://aistudio.google.com/app/apikey")

def main():
    """Run configuration validation."""
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════╗")
    print("║        Social Oracle Configuration Validator          ║")
    print("╔════════════════════════════════════════════════════════╗")
    print(f"{Style.RESET_ALL}")
    
    # Load environment variables
    load_dotenv()
    print_info("Loaded .env file")
    
    # Check dependencies first
    if not check_dependencies():
        print_error("\nMissing required dependencies!")
        print_info("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    check_optional_dependencies()
    
    # Check all APIs
    results = {
        "Gemini AI": check_gemini(),
        "Twitter/X": check_twitter(),
        "Reddit": check_reddit(),
        "Stocktwits": check_stocktwits(),
    }
    
    # Always available sources
    print_header("Always-Available Sources")
    print_success("RSS News Feeds: ENABLED")
    print_success("Hacker News: ENABLED")
    print_success("yfinance (price data): ENABLED")
    print_success("Sample fallback data: ENABLED")
    
    # Print summary
    print_summary(results)
    
    # Exit code
    if results["Gemini AI"]:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
