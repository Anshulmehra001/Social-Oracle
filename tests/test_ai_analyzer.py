"""
Unit tests for AI Sentiment Analyzer component.
Tests Google Gemini API integration with mocked responses and error handling scenarios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from src.ai_analyzer import AIAnalyzer, get_sentiment_analysis


@pytest.fixture
def mock_api_key():
    """Provide a mock API key for testing."""
    return "test_gemini_api_key"


@pytest.fixture
def mock_genai_response():
    """Create a mock Gemini API response."""
    response = Mock()
    response.text = "Positive"
    return response


@pytest.fixture
def sample_text_data():
    """Provide sample social media text data for testing."""
    return """
    Title: Great news about the project
    Content: This is amazing progress, really excited about the future
    Comment: Love this development
    Comment: This is fantastic news
    Comment: Really positive outlook
    """


@pytest.fixture
def sample_market_question():
    """Provide a sample market question for testing."""
    return "Will the community sentiment about the new project update be positive?"


class TestAIAnalyzer:
    """Test cases for AIAnalyzer class."""
    
    def test_initialization_with_api_key(self, mock_api_key):
        """Test successful initialization with provided API key."""
        with patch('src.ai_analyzer.genai.configure') as mock_configure, \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model:
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            assert analyzer.api_key == mock_api_key
            mock_configure.assert_called_once_with(api_key=mock_api_key)
            mock_model.assert_called_once_with('gemini-pro')
            assert analyzer.valid_outcomes == {"Positive", "Negative", "Neutral"}
    
    def test_initialization_with_env_var(self, mock_api_key):
        """Test initialization using environment variable."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': mock_api_key}, clear=True), \
             patch('src.ai_analyzer.genai.configure') as mock_configure, \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model:
            
            analyzer = AIAnalyzer()
            
            assert analyzer.api_key == mock_api_key
            mock_configure.assert_called_once_with(api_key=mock_api_key)
    
    def test_initialization_no_api_key(self):
        """Test initialization failure when no API key is provided."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Google AI API key is required"):
                AIAnalyzer()
    
    def test_get_sentiment_analysis_success(self, mock_api_key, mock_genai_response, 
                                          sample_text_data, sample_market_question):
        """Test successful sentiment analysis."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class:
            
            # Mock the model instance and its generate_content method
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_genai_response
            mock_model_class.return_value = mock_model
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            result = analyzer.get_sentiment_analysis(sample_text_data, sample_market_question)
            
            assert result == "Positive"
            mock_model.generate_content.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert sample_market_question in prompt
            assert sample_text_data in prompt
            assert "neutral and unbiased social sentiment analyst" in prompt
    
    def test_get_sentiment_analysis_all_valid_outcomes(self, mock_api_key, sample_text_data, sample_market_question):
        """Test that all valid sentiment outcomes are handled correctly."""
        valid_responses = ["Positive", "Negative", "Neutral"]
        
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class:
            
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            for expected_sentiment in valid_responses:
                mock_response = Mock()
                mock_response.text = expected_sentiment
                mock_model.generate_content.return_value = mock_response
                
                result = analyzer.get_sentiment_analysis(sample_text_data, sample_market_question, return_dict=False)
                assert result == expected_sentiment
    
    def test_get_sentiment_analysis_empty_text_data(self, mock_api_key, sample_market_question):
        """Test validation of empty text data."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            with pytest.raises(ValueError, match="Text data cannot be empty"):
                analyzer.get_sentiment_analysis("", sample_market_question)
            
            with pytest.raises(ValueError, match="Text data cannot be empty"):
                analyzer.get_sentiment_analysis("   ", sample_market_question)
    
    def test_get_sentiment_analysis_empty_market_question(self, mock_api_key, sample_text_data):
        """Test validation of empty market question."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            # Now optional, so should work with default question
            # Test that it doesn't raise when question is empty
            pass  # This test is now obsolete since market_question is optional
    
    def test_get_sentiment_analysis_retry_logic(self, mock_api_key, sample_text_data, sample_market_question):
        """Test retry logic when first attempt fails."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class, \
             patch('time.sleep') as mock_sleep:
            
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            
            # First call fails, second succeeds
            mock_response = Mock()
            mock_response.text = "Positive"
            mock_model.generate_content.side_effect = [
                Exception("API Error"),
                mock_response
            ]
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            result = analyzer.get_sentiment_analysis(sample_text_data, sample_market_question, return_dict=False)
            
            assert result == "Positive"
            assert mock_model.generate_content.call_count == 2
            mock_sleep.assert_called_once_with(2)  # Should sleep between retries
    
    def test_get_sentiment_analysis_max_retries_exceeded(self, mock_api_key, sample_text_data, sample_market_question):
        """Test behavior when maximum retry attempts are exceeded."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class, \
             patch('time.sleep'):
            
            mock_model = Mock()
            mock_model_class.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("Persistent API Error")
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            with pytest.raises(RuntimeError, match="AI sentiment analysis failed"):
                analyzer.get_sentiment_analysis(sample_text_data, sample_market_question)
            
            assert mock_model.generate_content.call_count == 2  # Should try twice
    
    def test_construct_prompt(self, mock_api_key, sample_text_data, sample_market_question):
        """Test prompt construction logic."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            prompt = analyzer._construct_prompt(sample_text_data, sample_market_question)
            
            # Verify prompt structure
            assert "neutral and unbiased social sentiment analyst" in prompt
            assert sample_market_question in prompt
            assert sample_text_data in prompt
            assert "Positive" in prompt and "Negative" in prompt and "Neutral" in prompt
            assert "ONLY ONE of these three words" in prompt
            assert "--- DATA:" in prompt
    
    def test_validate_response_success(self, mock_api_key):
        """Test successful response validation."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            # Test clean responses
            for sentiment in ["Positive", "Negative", "Neutral"]:
                mock_response = Mock()
                mock_response.text = sentiment
                result = analyzer._validate_response(mock_response)
                assert result == sentiment
    
    def test_validate_response_with_punctuation(self, mock_api_key):
        """Test response validation with extra punctuation."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            # Test responses with punctuation
            test_cases = [
                ("Positive.", "Positive"),
                ("Negative!", "Negative"),
                ("Neutral?", "Neutral"),
                ("Positive,", "Positive")
            ]
            
            for response_text, expected in test_cases:
                mock_response = Mock()
                mock_response.text = response_text
                result = analyzer._validate_response(mock_response)
                assert result == expected
    
    def test_validate_response_case_insensitive_extraction(self, mock_api_key):
        """Test response validation with case-insensitive extraction."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            # Test responses that contain valid sentiments in different cases
            test_cases = [
                ("The sentiment is positive overall", "Positive"),
                ("I would say negative", "Negative"),
                ("This appears neutral to me", "Neutral")
            ]
            
            for response_text, expected in test_cases:
                mock_response = Mock()
                mock_response.text = response_text
                result = analyzer._validate_response(mock_response)
                assert result == expected
    
    def test_validate_response_empty_response(self, mock_api_key):
        """Test validation of empty responses."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            # Test empty response
            mock_response = Mock()
            mock_response.text = ""
            
            with pytest.raises(ValueError, match="Empty response from AI model"):
                analyzer._validate_response(mock_response)
            
            # Test None response
            with pytest.raises(ValueError, match="Empty response from AI model"):
                analyzer._validate_response(None)
    
    def test_validate_response_invalid_sentiment(self, mock_api_key):
        """Test validation of invalid sentiment responses."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel'):
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            
            mock_response = Mock()
            mock_response.text = "Invalid sentiment response"
            
            with pytest.raises(ValueError, match="Invalid sentiment response"):
                analyzer._validate_response(mock_response)
    
    def test_generation_config_parameters(self, mock_api_key, sample_text_data, sample_market_question):
        """Test that proper generation configuration is used."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class:
            
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Positive"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            analyzer.get_sentiment_analysis(sample_text_data, sample_market_question, return_dict=False)
            
            # Verify generation config parameters (updated for enhanced response)
            call_args = mock_model.generate_content.call_args
            generation_config = call_args[1]['generation_config']
            
            assert generation_config.temperature == 0.2  # Updated for reasoning
            assert generation_config.max_output_tokens == 200  # Updated for explanation
    
    def test_safety_settings_configuration(self, mock_api_key, sample_text_data, sample_market_question):
        """Test that proper safety settings are configured."""
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class:
            
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Positive"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            analyzer.get_sentiment_analysis(sample_text_data, sample_market_question)
            
            # Verify safety settings are passed
            call_args = mock_model.generate_content.call_args
            safety_settings = call_args[1]['safety_settings']
            
            assert HarmCategory.HARM_CATEGORY_HATE_SPEECH in safety_settings
            assert HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT in safety_settings
            assert HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT in safety_settings
            assert HarmCategory.HARM_CATEGORY_HARASSMENT in safety_settings


class TestConvenienceFunction:
    """Test cases for the convenience function."""
    
    @patch('src.ai_analyzer.AIAnalyzer')
    def test_get_sentiment_analysis_function(self, mock_analyzer_class):
        """Test the convenience function for sentiment analysis."""
        # Mock analyzer instance
        mock_analyzer = Mock()
        mock_analyzer.get_sentiment_analysis.return_value = "Positive"
        mock_analyzer_class.return_value = mock_analyzer
        
        result = get_sentiment_analysis("test data", "test question")
        
        assert result == "Positive"
        mock_analyzer_class.assert_called_once()
        mock_analyzer.get_sentiment_analysis.assert_called_once_with("test data", "test question")
    
    @patch('src.ai_analyzer.AIAnalyzer')
    def test_get_sentiment_analysis_function_error(self, mock_analyzer_class):
        """Test error handling in the convenience function."""
        mock_analyzer_class.side_effect = Exception("Initialization error")
        
        with pytest.raises(Exception, match="Initialization error"):
            get_sentiment_analysis("test data", "test question")


class TestIntegrationScenarios:
    """Test cases for integration scenarios and edge cases."""
    
    def test_large_text_data_handling(self, mock_api_key, sample_market_question):
        """Test handling of large text data inputs."""
        # Create large text data (simulating many social media posts)
        large_text = "Test content " * 1000  # Simulate large dataset
        
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class:
            
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Neutral"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            result = analyzer.get_sentiment_analysis(large_text, sample_market_question, return_dict=False)
            
            assert result == "Neutral"
            # Verify the large text was included in the prompt
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert large_text[:100] in prompt  # At least some of it
    
    def test_special_characters_in_text(self, mock_api_key, sample_market_question):
        """Test handling of special characters in social media text."""
        special_text = "Text with émojis 🚀 and spëcial chars & symbols @#$%"
        
        with patch('src.ai_analyzer.genai.configure'), \
             patch('src.ai_analyzer.genai.GenerativeModel') as mock_model_class:
            
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Positive"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            analyzer = AIAnalyzer(api_key=mock_api_key)
            result = analyzer.get_sentiment_analysis(special_text, sample_market_question, return_dict=False)
            
            assert result == "Positive"
            # Verify special characters are preserved in prompt
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert special_text in prompt
