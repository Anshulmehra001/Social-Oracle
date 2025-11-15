#!/usr/bin/env python3
"""
Social Oracle Application Runner

This script runs the Social Oracle application with proper error handling
and environment validation.
"""

import os
import sys

def main():
    """Run the Social Oracle application."""
    print("🔮 Starting Social Oracle Application")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and fill in your values")
        return False
    
    # Import and run the application
    try:
        from main import main as run_main
        return run_main()
    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
