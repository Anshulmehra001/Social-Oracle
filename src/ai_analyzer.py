"""
AI Sentiment Analyzer Module

This module provides sentiment analysis functionality using Google Gemini AI
to determine sentiment classification for social media data in prediction markets.
"""

import os
import time
import logging
from typing import Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI-powered sentiment analyzer using Google Gemini API.
    
    This class handles sentiment analysis of social media text data
    for prediction market resolution.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI analyzer with Google Gemini API.
        
        Args:
            api_key: Google AI API key. If None, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Google AI API key is required. Set GEMINI_API_KEY environment variable.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model - use gemini-2.0-flash (faster and available)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Valid sentiment outcomes
        self.valid_outcomes = {"Positive", "Negative", "Neutral"}
    
    def get_sentiment_analysis(self, text_data: str, market_question: str = None, return_dict: bool = True):
        """
        Analyze sentiment of social media text data for a given market question.
        
        Args:
            text_data: Concatenated social media text to analyze
            market_question: The prediction market question being resolved (optional)
            return_dict: If True returns dict, if False returns just sentiment string
            
        Returns:
            dict or str: If return_dict=True, returns {
                'sentiment': str ("Positive", "Negative", or "Neutral"),
                'reasoning': str (explanation of the sentiment),
                'confidence': str ("High", "Medium", "Low")
            }
            If return_dict=False, returns just the sentiment string for backward compatibility.
            
        Raises:
            ValueError: If inputs are invalid or API response is malformed
            RuntimeError: If API call fails after retry
        """
        if not text_data or not text_data.strip():
            raise ValueError("Text data cannot be empty")
        
        if not market_question:
            market_question = "What is the overall sentiment of this content?"
        
        logger.info(f"Starting sentiment analysis for: {market_question[:100]}...")
        logger.info(f"Analyzing {len(text_data)} characters of social media data")
        
        # Construct the structured prompt
        prompt = self._construct_enhanced_prompt(text_data, market_question)
        
        # Attempt analysis with retry logic
        for attempt in range(2):  # Try twice as per requirements
            try:
                logger.info(f"Attempting sentiment analysis (attempt {attempt + 1}/2)")
                
                # Configure safety settings to be less restrictive for social media content
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }
                
                # Generate response with timeout handling
                response = self.model.generate_content(
                    prompt,
                    safety_settings=safety_settings,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,  # Slightly higher for reasoning
                        max_output_tokens=200,  # Allow for explanation
                    )
                )
                
                # Validate and extract sentiment with reasoning
                result = self._validate_enhanced_response(response)
                logger.info(f"Sentiment analysis completed: {result['sentiment']} ({result['confidence']})")
                
                # Return based on flag - backward compatibility for tests
                if return_dict:
                    return result
                else:
                    return result['sentiment']
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == 0:  # First attempt failed, wait before retry
                    time.sleep(2)
                    continue
                else:  # Second attempt failed, raise error
                    logger.error(f"Sentiment analysis failed after 2 attempts: {str(e)}")
                    raise RuntimeError(f"AI sentiment analysis failed: {str(e)}")
        
        # This should never be reached due to the loop logic above
        raise RuntimeError("Unexpected error in sentiment analysis")
    
    def _construct_enhanced_prompt(self, text_data: str, market_question: str) -> str:
        """
        Construct an enhanced prompt that requests reasoning and confidence.
        
        Args:
            text_data: Social media text to analyze
            market_question: Market question for context
            
        Returns:
            str: Formatted prompt for the AI model
        """
        prompt = f"""As a neutral and unbiased social sentiment analyst for prediction markets, analyze the following data.

Question: "{market_question}"

Analyze the sentiment in the data below and provide your response in exactly this format:
Sentiment: [Positive/Negative/Neutral]
Confidence: [High/Medium/Low]
Reasoning: [Brief explanation in 1-2 sentences]

Consider:
- Volume and consistency of opinions
- Recency and relevance
- Quality of sources

--- DATA:
{text_data[:8000]}

Your response:"""
        return prompt
    
    def _construct_prompt(self, text_data: str, market_question: str) -> str:
        """
        Construct a structured prompt for sentiment analysis.
        
        Args:
            text_data: Social media text to analyze
            market_question: Market question for context
            
        Returns:
            str: Formatted prompt for the AI model
        """
        prompt = f"""As a neutral and unbiased social sentiment analyst, your task is to resolve a prediction market.

Market Question: "{market_question}"

Based *only* on the following raw text data compiled from social media, determine the dominant sentiment. The possible outcomes are "Positive", "Negative", or "Neutral". You must respond with ONLY ONE of these three words and nothing else.

--- DATA:
{text_data}"""
        
        return prompt
    
    def _validate_enhanced_response(self, response) -> dict:
        """
        Validate and extract structured sentiment response.
        
        Args:
            response: Raw response from Gemini API
            
        Returns:
            dict: Parsed sentiment data with reasoning and confidence
            
        Raises:
            ValueError: If response format is invalid
        """
        if not response or not response.text:
            raise ValueError("Empty response from AI model")
        
        text = response.text.strip()
        
        # Parse the structured response
        result = {
            'sentiment': 'Neutral',
            'confidence': 'Medium',
            'reasoning': 'Unable to parse AI response'
        }
        
        # Extract sentiment
        for line in text.split('\n'):
            line = line.strip()
            if line.lower().startswith('sentiment:'):
                sentiment = line.split(':', 1)[1].strip()
                # Clean and validate
                sentiment = sentiment.replace('.', '').replace(',', '').strip()
                for valid in self.valid_outcomes:
                    if valid.lower() in sentiment.lower():
                        result['sentiment'] = valid
                        break
            elif line.lower().startswith('confidence:'):
                confidence = line.split(':', 1)[1].strip()
                confidence = confidence.replace('.', '').replace(',', '').strip().title()
                if confidence in ['High', 'Medium', 'Low']:
                    result['confidence'] = confidence
            elif line.lower().startswith('reasoning:'):
                reasoning = line.split(':', 1)[1].strip()
                if reasoning:
                    result['reasoning'] = reasoning
        
        # Fallback: try to find sentiment anywhere in response
        if result['sentiment'] == 'Neutral' and result['reasoning'] == 'Unable to parse AI response':
            for valid in self.valid_outcomes:
                if valid.lower() in text.lower():
                    result['sentiment'] = valid
                    result['reasoning'] = text[:200]
                    break
        
        return result
    
    def _validate_response(self, response) -> str:
        """
        Validate and extract sentiment from AI response.
        
        Args:
            response: Raw response from Gemini API
            
        Returns:
            str: Validated sentiment classification
            
        Raises:
            ValueError: If response format is invalid
        """
        if not response or not response.text:
            raise ValueError("Empty response from AI model")
        
        # Extract and clean the response text
        sentiment = response.text.strip()
        
        # Remove any extra whitespace or punctuation
        sentiment = sentiment.replace('.', '').replace(',', '').replace('!', '').replace('?', '')
        
        # Check if response is a valid sentiment
        if sentiment not in self.valid_outcomes:
            # Try to find a valid sentiment in the response
            for valid_sentiment in self.valid_outcomes:
                if valid_sentiment.lower() in sentiment.lower():
                    logger.warning(f"Response '{sentiment}' contained valid sentiment '{valid_sentiment}', using it")
                    return valid_sentiment
            
            raise ValueError(f"Invalid sentiment response: '{sentiment}'. Expected one of: {self.valid_outcomes}")
        
        return sentiment


def get_sentiment_analysis(text_data: str, market_question: str) -> str:
    """
    Convenience function for sentiment analysis.
    
    This function creates an AIAnalyzer instance and performs sentiment analysis.
    
    Args:
        text_data: Concatenated social media text to analyze
        market_question: The prediction market question being resolved
        
    Returns:
        str: Sentiment classification ("Positive", "Negative", or "Neutral")
    """
    analyzer = AIAnalyzer()
    return analyzer.get_sentiment_analysis(text_data, market_question)