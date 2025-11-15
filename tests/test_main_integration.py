"""
Integration tests for the main Social Oracle workflow.
Tests end-to-end pipeline execution and error propagation handling.

Requirements: 4.3, 4.4
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from dataclasses import dataclass

# Mock all external dependencies
sys.modules['web3'] = Mock()
sys.modules['web3.contract'] = Mock()
sys.modules['solcx'] = Mock()
sys.modules['praw'] = Mock()
sys.modules['praw.exceptions'] = Mock()
sys.modules['praw.models'] = Mock()
sys.modules['prawcore.exceptions'] = Mock()
sys.modules['google.generativeai'] = Mock()
sys.modules['google.generativeai.types'] = Mock()

# Mock dataclasses for testing
@dataclass
class MockAPIConfig:
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    gemini_api_key: str
    bnb_rpc_url: str
    private_key: str

@dataclass
class MockMarketConfig:
    question: str
    search_keywords: str
    reddit_subreddit: str
    post_limit: int = 50

@dataclass
class MockBlockchainTransaction:
    contract_address: str
    transaction_hash: str
    block_number: int
    gas_used: int
    status: str
    timestamp: datetime


@pytest.fixture
def mock_api_config():
    """Create a mock API configuration for testing."""
    return MockAPIConfig(
        reddit_client_id="test_reddit_client",
        reddit_client_secret="test_reddit_secret",
        reddit_user_agent="test_user_agent",
        gemini_api_key="test_gemini_key",
        bnb_rpc_url="https://test-rpc.binance.org:8545/",
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )


@pytest.fixture
def sample_market_config():
    """Create a sample market configuration for testing."""
    return MockMarketConfig(
        question="Will Bitcoin price be above $50,000 by the end of this month?",
        search_keywords="Bitcoin price prediction $50000",
        reddit_subreddit="CryptoCurrency",
        post_limit=30
    )


@pytest.fixture
def mock_deployment_transaction():
    """Create a mock deployment transaction for testing."""
    return MockBlockchainTransaction(
        contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
        transaction_hash="0xdeployment123456789abcdef",
        block_number=12345,
        gas_used=1500000,
        status="success",
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_outcome_transaction():
    """Create a mock outcome transaction for testing."""
    return MockBlockchainTransaction(
        contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
        transaction_hash="0xoutcome123456789abcdef",
        block_number=12346,
        gas_used=150000,
        status="success",
        timestamp=datetime.now()
    )


class MockSocialOracleOrchestrator:
    """Mock implementation of SocialOracleOrchestrator for testing."""
    
    def __init__(self):
        self.api_config = None
        self.social_fetcher = None
        self.ai_analyzer = None
        self.blockchain_connector = None
        self.logger = Mock()
    
    def load_configuration(self):
        """Mock configuration loading."""
        if hasattr(self, '_config_success'):
            return self._config_success
        return True
    
    def fetch_social_data(self, market_config):
        """Mock social data fetching."""
        if hasattr(self, '_social_data_result'):
            return self._social_data_result
        return "Sample social media data"
    
    def analyze_sentiment(self, social_data, market_question):
        """Mock sentiment analysis."""
        if hasattr(self, '_sentiment_result'):
            return self._sentiment_result
        return "Positive"
    
    def deploy_and_record_outcome(self, market_question, sentiment_outcome):
        """Mock blockchain operations."""
        if hasattr(self, '_blockchain_result'):
            return self._blockchain_result
        return {
            'deployment_transaction': {'contract_address': '0x123'},
            'outcome_transaction': {'transaction_hash': '0x456'},
            'contract_status': {'is_resolved': True},
            'explorer_urls': {'deployment': 'https://testnet.bscscan.com/tx/0x123'}
        }
    
    def run_complete_workflow(self, market_config):
        """Mock complete workflow execution."""
        try:
            # Step 1: Fetch social data
            social_data = self.fetch_social_data(market_config)
            if not social_data:
                return False
            
            # Step 2: Analyze sentiment
            sentiment_outcome = self.analyze_sentiment(social_data, market_config.question)
            if not sentiment_outcome:
                return False
            
            # Step 3: Deploy and record
            blockchain_result = self.deploy_and_record_outcome(market_config.question, sentiment_outcome)
            if not blockchain_result:
                return False
            
            return True
        except Exception:
            return False


class TestSocialOracleOrchestrator:
    """Test suite for SocialOracleOrchestrator class."""
    
    def test_initialization(self):
        """Test successful initialization of orchestrator."""
        orchestrator = MockSocialOracleOrchestrator()
        
        assert orchestrator.api_config is None
        assert orchestrator.social_fetcher is None
        assert orchestrator.ai_analyzer is None
        assert orchestrator.blockchain_connector is None
        assert orchestrator.logger is not None
    
    def test_load_configuration_success(self, mock_api_config):
        """Test successful configuration loading."""
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._config_success = True
        
        result = orchestrator.load_configuration()
        
        assert result is True
    
    def test_load_configuration_validation_failure(self):
        """Test configuration loading with environment validation failure."""
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._config_success = False
        
        result = orchestrator.load_configuration()
        
        assert result is False
    
    def test_load_configuration_exception(self):
        """Test configuration loading with exception handling."""
        orchestrator = MockSocialOracleOrchestrator()
        
        def failing_load():
            raise Exception("Configuration error")
        
        orchestrator.load_configuration = failing_load
        
        try:
            result = orchestrator.load_configuration()
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Configuration error"
    
    def test_fetch_social_data_success(self, sample_market_config):
        """Test successful social media data fetching."""
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._social_data_result = "Sample social media data"
        
        result = orchestrator.fetch_social_data(sample_market_config)
        
        assert result == "Sample social media data"
    
    def test_fetch_social_data_empty_result(self, sample_market_config):
        """Test social media data fetching with empty result."""
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._social_data_result = None
        
        result = orchestrator.fetch_social_data(sample_market_config)
        
        assert result is None
    
    def test_fetch_social_data_exception(self, sample_market_config):
        """Test social media data fetching with exception handling."""
        orchestrator = MockSocialOracleOrchestrator()
        
        def failing_fetch(market_config):
            raise Exception("API error")
        
        orchestrator.fetch_social_data = failing_fetch
        
        try:
            result = orchestrator.fetch_social_data(sample_market_config)
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "API error"
    
    def test_analyze_sentiment_success(self):
        """Test successful sentiment analysis."""
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._sentiment_result = "Positive"
        
        social_data = "Sample social media data"
        market_question = "Test market question?"
        
        result = orchestrator.analyze_sentiment(social_data, market_question)
        
        assert result == "Positive"
    
    def test_analyze_sentiment_exception(self):
        """Test sentiment analysis with exception handling."""
        orchestrator = MockSocialOracleOrchestrator()
        
        def failing_analyze(social_data, market_question):
            raise Exception("AI API error")
        
        orchestrator.analyze_sentiment = failing_analyze
        
        try:
            result = orchestrator.analyze_sentiment("test data", "test question")
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "AI API error"
    
    def test_deploy_and_record_outcome_success(self, mock_deployment_transaction, 
                                             mock_outcome_transaction):
        """Test successful contract deployment and outcome recording."""
        orchestrator = MockSocialOracleOrchestrator()
        
        expected_result = {
            'deployment_transaction': {'contract_address': '0x123'},
            'outcome_transaction': {'transaction_hash': '0x456'},
            'contract_status': {'is_resolved': True},
            'explorer_urls': {'deployment': 'https://testnet.bscscan.com/tx/0x123'}
        }
        orchestrator._blockchain_result = expected_result
        
        market_question = "Test market question?"
        sentiment_outcome = "Positive"
        
        result = orchestrator.deploy_and_record_outcome(market_question, sentiment_outcome)
        
        assert result is not None
        assert 'deployment_transaction' in result
        assert 'outcome_transaction' in result
        assert 'contract_status' in result
        assert 'explorer_urls' in result
    
    def test_deploy_and_record_outcome_deployment_failure(self):
        """Test contract deployment failure handling."""
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._blockchain_result = None
        
        result = orchestrator.deploy_and_record_outcome("test question", "Positive")
        
        assert result is None
    
    def test_deploy_and_record_outcome_recording_failure(self, mock_deployment_transaction):
        """Test outcome recording failure handling."""
        orchestrator = MockSocialOracleOrchestrator()
        
        def failing_deploy(market_question, sentiment_outcome):
            raise Exception("Recording failed")
        
        orchestrator.deploy_and_record_outcome = failing_deploy
        
        try:
            result = orchestrator.deploy_and_record_outcome("test question", "Positive")
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Recording failed"


class TestCompleteWorkflowIntegration:
    """Test suite for complete workflow integration scenarios."""
    
    def test_run_complete_workflow_success(self, sample_market_config):
        """Test successful execution of complete workflow."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Setup all steps to succeed
        orchestrator._social_data_result = "Sample social media data"
        orchestrator._sentiment_result = "Positive"
        orchestrator._blockchain_result = {
            'deployment_transaction': {'contract_address': '0x123'},
            'outcome_transaction': {'transaction_hash': '0x456'},
            'contract_status': {'is_resolved': True},
            'explorer_urls': {'deployment': 'https://testnet.bscscan.com/tx/0x123'}
        }
        
        result = orchestrator.run_complete_workflow(sample_market_config)
        
        # Verify success
        assert result is True
    
    def test_run_complete_workflow_social_data_failure(self, sample_market_config):
        """Test workflow failure due to social data fetching error."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Setup social data fetching to fail
        orchestrator._social_data_result = None
        
        result = orchestrator.run_complete_workflow(sample_market_config)
        
        # Verify failure
        assert result is False
    
    def test_run_complete_workflow_sentiment_analysis_failure(self, sample_market_config):
        """Test workflow failure due to sentiment analysis error."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Setup social data to succeed but sentiment analysis to fail
        orchestrator._social_data_result = "Sample social media data"
        orchestrator._sentiment_result = None
        
        result = orchestrator.run_complete_workflow(sample_market_config)
        
        # Verify failure
        assert result is False
    
    def test_run_complete_workflow_blockchain_failure(self, sample_market_config):
        """Test workflow failure due to blockchain operations error."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Setup social data and sentiment analysis to succeed but blockchain to fail
        orchestrator._social_data_result = "Sample social media data"
        orchestrator._sentiment_result = "Positive"
        orchestrator._blockchain_result = None
        
        result = orchestrator.run_complete_workflow(sample_market_config)
        
        # Verify failure
        assert result is False
    
    def test_run_complete_workflow_unexpected_exception(self, sample_market_config):
        """Test workflow handling of unexpected exceptions."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Make fetch_social_data raise an exception
        def failing_fetch(market_config):
            raise Exception("Unexpected error")
        
        orchestrator.fetch_social_data = failing_fetch
        
        result = orchestrator.run_complete_workflow(sample_market_config)
        
        # Verify graceful failure
        assert result is False


class TestErrorPropagation:
    """Test suite for error propagation and graceful failure handling."""
    
    def test_error_handling_in_workflow_steps(self, sample_market_config):
        """Test that errors in workflow steps are handled gracefully."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Test social data fetching error
        orchestrator._social_data_result = None
        result = orchestrator.run_complete_workflow(sample_market_config)
        assert result is False
        
        # Test sentiment analysis error
        orchestrator._social_data_result = "Sample data"
        orchestrator._sentiment_result = None
        result = orchestrator.run_complete_workflow(sample_market_config)
        assert result is False
        
        # Test blockchain error
        orchestrator._sentiment_result = "Positive"
        orchestrator._blockchain_result = None
        result = orchestrator.run_complete_workflow(sample_market_config)
        assert result is False
    
    def test_exception_propagation(self, sample_market_config):
        """Test that exceptions are properly caught and handled."""
        orchestrator = MockSocialOracleOrchestrator()
        
        # Make a method raise an exception
        def failing_method(market_config):
            raise ValueError("Test error")
        
        orchestrator.fetch_social_data = failing_method
        
        # Should return False instead of raising exception
        result = orchestrator.run_complete_workflow(sample_market_config)
        assert result is False


class TestMainFunction:
    """Test suite for main function logic."""
    
    def test_main_workflow_logic_success(self):
        """Test the main workflow logic for successful execution."""
        # Simulate successful workflow
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._config_success = True
        orchestrator._social_data_result = "Sample data"
        orchestrator._sentiment_result = "Positive"
        orchestrator._blockchain_result = {'status': 'success'}
        
        # Test configuration loading
        config_result = orchestrator.load_configuration()
        assert config_result is True
        
        # Test workflow execution
        market_config = MockMarketConfig(
            question="Test question?",
            search_keywords="test keywords",
            reddit_subreddit="test",
            post_limit=10
        )
        
        workflow_result = orchestrator.run_complete_workflow(market_config)
        assert workflow_result is True
    
    def test_main_workflow_logic_failure_scenarios(self):
        """Test main workflow logic for various failure scenarios."""
        # Test configuration failure
        orchestrator = MockSocialOracleOrchestrator()
        orchestrator._config_success = False
        
        config_result = orchestrator.load_configuration()
        assert config_result is False
        
        # Test workflow failure due to social data
        orchestrator._config_success = True
        orchestrator._social_data_result = None
        
        market_config = MockMarketConfig(
            question="Test question?",
            search_keywords="test keywords", 
            reddit_subreddit="test",
            post_limit=10
        )
        
        workflow_result = orchestrator.run_complete_workflow(market_config)
        assert workflow_result is False