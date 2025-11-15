"""
Price Analysis Module

Enhanced technical analysis using yfinance with indicators like:
- Moving averages (SMA, EMA)
- RSI (Relative Strength Index)
- Volume analysis
- Price momentum
- Volatility metrics
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """
    Analyzes stock price data to provide technical indicators and trends.
    Complements sentiment analysis with quantitative price metrics.
    """
    
    def __init__(self):
        """Initialize price analyzer."""
        pass
    
    def get_comprehensive_analysis(self, ticker: str, days: int = 30) -> Dict:
        """
        Get comprehensive price analysis with technical indicators.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of historical data to analyze
            
        Returns:
            Dictionary with price metrics and indicators
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Fetch historical data
            hist = stock.history(period=f"{days}d")
            
            if hist.empty:
                logger.warning(f"No price data available for {ticker}")
                return self._empty_analysis(ticker)
            
            # Calculate metrics
            analysis = {
                'ticker': ticker,
                'current_price': float(hist['Close'].iloc[-1]),
                'price_change_1d': self._calculate_change(hist, 1),
                'price_change_5d': self._calculate_change(hist, 5),
                'price_change_30d': self._calculate_change(hist, min(30, len(hist))),
                'volume_avg_30d': float(hist['Volume'].mean()),
                'volume_current': float(hist['Volume'].iloc[-1]),
                'volume_trend': self._analyze_volume_trend(hist),
                'sma_20': self._calculate_sma(hist, 20),
                'sma_50': self._calculate_sma(hist, 50),
                'rsi_14': self._calculate_rsi(hist, 14),
                'volatility': self._calculate_volatility(hist),
                'price_trend': self._determine_trend(hist),
                'support_level': float(hist['Low'].tail(20).min()),
                'resistance_level': float(hist['High'].tail(20).max()),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add interpretation
            analysis['interpretation'] = self._interpret_signals(analysis)
            
            logger.info(f"✅ Completed price analysis for {ticker}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {ticker}: {e}")
            return self._empty_analysis(ticker, error=str(e))
    
    def get_simple_context(self, ticker: str, days: int = 5) -> str:
        """
        Get simple price context string for AI analysis.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to analyze
            
        Returns:
            Formatted string with price context
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{days}d")
            
            if hist.empty:
                return f"Price data unavailable for {ticker}"
            
            recent_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[0]
            change_pct = ((recent_close - prev_close) / prev_close) * 100
            
            high = hist['High'].max()
            low = hist['Low'].min()
            
            return (
                f"\n\nRecent {days}-day price: ${prev_close:.2f} → ${recent_close:.2f} "
                f"({change_pct:+.2f}%)\n"
                f"Range: ${low:.2f} - ${high:.2f}"
            )
            
        except Exception as e:
            logger.warning(f"Could not fetch price context for {ticker}: {e}")
            return ""
    
    def _calculate_change(self, hist, days: int) -> Optional[float]:
        """Calculate percentage change over specified days."""
        try:
            if len(hist) < days + 1:
                return None
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-days-1]
            return float(((current - previous) / previous) * 100)
        except:
            return None
    
    def _calculate_sma(self, hist, period: int) -> Optional[float]:
        """Calculate Simple Moving Average."""
        try:
            if len(hist) < period:
                return None
            return float(hist['Close'].tail(period).mean())
        except:
            return None
    
    def _calculate_rsi(self, hist, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index."""
        try:
            if len(hist) < period + 1:
                return None
            
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1])
        except:
            return None
    
    def _calculate_volatility(self, hist) -> Optional[float]:
        """Calculate price volatility (standard deviation of returns)."""
        try:
            returns = hist['Close'].pct_change()
            return float(returns.std() * 100)
        except:
            return None
    
    def _analyze_volume_trend(self, hist) -> str:
        """Analyze volume trend."""
        try:
            recent_vol = hist['Volume'].tail(5).mean()
            overall_vol = hist['Volume'].mean()
            
            if recent_vol > overall_vol * 1.2:
                return "increasing"
            elif recent_vol < overall_vol * 0.8:
                return "decreasing"
            else:
                return "stable"
        except:
            return "unknown"
    
    def _determine_trend(self, hist) -> str:
        """Determine overall price trend."""
        try:
            sma_20 = self._calculate_sma(hist, 20)
            sma_50 = self._calculate_sma(hist, 50)
            current = hist['Close'].iloc[-1]
            
            if sma_20 is None:
                # Use simple trend if not enough data
                change = self._calculate_change(hist, min(5, len(hist) - 1))
                if change and change > 2:
                    return "bullish"
                elif change and change < -2:
                    return "bearish"
                else:
                    return "neutral"
            
            # Use moving average crossover
            if current > sma_20 and (sma_50 is None or sma_20 > sma_50):
                return "bullish"
            elif current < sma_20 and (sma_50 is None or sma_20 < sma_50):
                return "bearish"
            else:
                return "neutral"
        except:
            return "unknown"
    
    def _interpret_signals(self, analysis: Dict) -> str:
        """Interpret the technical signals into readable text."""
        signals = []
        
        # RSI interpretation
        rsi = analysis.get('rsi_14')
        if rsi:
            if rsi > 70:
                signals.append("RSI indicates overbought conditions")
            elif rsi < 30:
                signals.append("RSI indicates oversold conditions")
        
        # Trend interpretation
        trend = analysis.get('price_trend', 'unknown')
        if trend == 'bullish':
            signals.append("Price trend is bullish")
        elif trend == 'bearish':
            signals.append("Price trend is bearish")
        
        # Volume interpretation
        vol_trend = analysis.get('volume_trend', 'unknown')
        if vol_trend == 'increasing':
            signals.append("Trading volume is increasing")
        elif vol_trend == 'decreasing':
            signals.append("Trading volume is decreasing")
        
        # Recent price action
        change_5d = analysis.get('price_change_5d')
        if change_5d:
            if change_5d > 5:
                signals.append(f"Strong upward movement (+{change_5d:.1f}% in 5 days)")
            elif change_5d < -5:
                signals.append(f"Strong downward movement ({change_5d:.1f}% in 5 days)")
        
        return "; ".join(signals) if signals else "No strong technical signals"
    
    def _empty_analysis(self, ticker: str, error: str = None) -> Dict:
        """Return empty analysis structure."""
        return {
            'ticker': ticker,
            'error': error or "No data available",
            'current_price': None,
            'interpretation': "Price data unavailable",
            'timestamp': datetime.now().isoformat()
        }
