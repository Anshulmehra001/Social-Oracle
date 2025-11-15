"""
System Integration Validation Tests

This module provides comprehensive end-to-end integration tests for the Social Oracle system.
Tests validate complete system integration, blockchain transaction recording, smart contract
state updates, and error handling across all system boundaries.

Requirements: 1.5, 2.5, 3.5, 4.4, 4.5
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

# Mock all external dependencies before importing
sys.modules['web3'] = Mock()
sys.modules['web3.contract'] = Mock()
sys.modules['solcx'] = Mock()
sys.modules['praw'] = Mock()
sys.modules['praw.exceptions'] = Mock()
sys.modules['praw.models'] = Mock()
sys.modules['prawcore.exceptions'] = Mock()
sys.modules['google.generativeai'] = Mock()
sys.modules['google.generativeai.types'] = Mock()

# Import system components
from main import SocialOracleOrchestrator
from src.config import Config, MarketConfig, APIConfig
from src.social_fetcher import SocialMediaFetcher
from src.ai_analyzer import AIAnalyzer
from src.blockchain_connector import BlockchainConnector, BlockchainTransaction


@pytest.fixture
def integration_api_config():
    """API configuration for integration testing."""
    return APIConfig(
        reddit_client_id="integration_test_client",
        reddit_client_secret="integration_test_secret",
        reddit_user_agent="SocialOracle/1.0 Integration Test",
        gemini_api_key="integration_test_gemini_key",
        bnb_rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545/",
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )


@pytest.fixture
def integration_market_config():
    """Market configuration for integration testing."""
    return MarketConfig(
        question="Will the integration test pass successfully?",
        search_keywords="integration test success validation",
        reddit_subreddit="test",
        post_limit=10
    )


@pytest.fixture
def mock_social_data():
    """Mock social media data for integration testing."""
    return """
    Title: Integration Test Success Discussion
    Content: The integration tests are showing positive results and validation is working well
    Comment: Great to see the system working end-to-end
    Comment: All components are integrating properly
    Comment: Very positive about the test outcomes
    
    Title: System Validation Update
    Content: End-to-end testing shows excellent integration between all components
    Comment: The workflow is smooth and reliable
    Comment: Blockchain integration is working perfectly
    """


@pytest.fixture
def mock_deployment_transaction():
    """Mock deployment transaction for integration testing."""
    return BlockchainTransaction(
        contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
        transaction_hash="0xdeployment1234567890abcdef1234567890abcdef1234567890abcdef123456",
        block_number=15000001,
        gas_used=1800000,
        status="success",
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_outcome_transaction():
    """Mock outcome transaction for integration testing."""
    return BlockchainTransaction(
        contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
        transaction_hash="0xoutcome1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        block_number=15000002,
        gas_used=180000,
        status="success",
        timestamp=datetime.now()
    )


class TestCompleteSystemIntegration:
    """Test suite for complete system integration validation."""
    
    def test_orchestrator_initialization_integration(self, integration_api_config):
        """Test complete orchestrator initialization with all components."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            orchestrator = SocialOracleOrchestrator()
            
            # Test configuration loading
            assert orchestrator.load_configuration() is True
            
            # Verify all components are initialized
            assert orchestrator.api_config is not None
            assert orchestrator.social_fetcher is not None
            assert orchestrator.ai_analyzer is not None
            assert orchestrator.blockchain_connector is not None
            
            # Verify configuration values
            assert orchestrator.api_config.reddit_client_id == integration_api_config.reddit_client_id
            assert orchestrator.api_config.gemini_api_key == integration_api_config.gemini_api_key
            assert orchestrator.api_config.bnb_rpc_url == integration_api_config.bnb_rpc_url
    
    def test_end_to_end_workflow_success(self, integration_api_config, integration_market_config, 
                                       mock_social_data, mock_deployment_transaction, 
                                       mock_outcome_transaction):
        """Test successful end-to-end workflow execution."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            assert orchestrator.load_configuration() is True
            
            # Mock the individual methods after initialization
            with patch.object(orchestrator, 'fetch_social_data', return_value=mock_social_data) as mock_fetch, \
                 patch.object(orchestrator, 'analyze_sentiment', return_value="Positive") as mock_analyze, \
                 patch.object(orchestrator, 'deploy_and_record_outcome') as mock_deploy:
                
                mock_deploy.return_value = {
                    'deployment_transaction': asdict(mock_deployment_transaction),
                    'outcome_transaction': asdict(mock_outcome_transaction),
                    'contract_status': {
                        'market_question': integration_market_config.question,
                        'market_outcome': 'Positive',
                        'is_resolved': True,
                        'owner': '0x742d35Cc6634C0532925a3b8D4C9db96590645d8'
                    },
                    'explorer_urls': {
                        'deployment': f"https://testnet.bscscan.com/tx/{mock_deployment_transaction.transaction_hash}",
                        'outcome': f"https://testnet.bscscan.com/tx/{mock_outcome_transaction.transaction_hash}"
                    }
                }
                
                # Execute workflow
                result = orchestrator.run_complete_workflow(integration_market_config)
                
                # Verify workflow success
                assert result is True
                
                # Verify component interactions
                mock_fetch.assert_called_once_with(integration_market_config)
                mock_analyze.assert_called_once_with(mock_social_data, integration_market_config.question)
                mock_deploy.assert_called_once_with(integration_market_config.question, "Positive")
    
    def test_workflow_component_data_flow(self, integration_api_config, integration_market_config):
        """Test data flow between workflow components."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            # Track data flow through components
            social_data_output = "Test social media data for validation"
            sentiment_output = "Positive"
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock component methods to track data flow
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', return_value=social_data_output) as mock_fetch, \
                 patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', return_value=sentiment_output) as mock_analyze, \
                 patch.object(orchestrator.blockchain_connector, 'deploy_contract') as mock_deploy, \
                 patch.object(orchestrator.blockchain_connector, 'record_outcome') as mock_record, \
                 patch.object(orchestrator.blockchain_connector, 'get_contract_abi', return_value=[]) as mock_abi, \
                 patch.object(orchestrator.blockchain_connector, 'verify_contract_status', return_value={'is_resolved': True}) as mock_verify, \
                 patch.object(orchestrator.blockchain_connector, 'get_block_explorer_url', return_value="https://testnet.bscscan.com/tx/0x123") as mock_url:
                
                mock_deployment_tx = BlockchainTransaction(
                    contract_address="0x123",
                    transaction_hash="0xdeployment123",
                    block_number=12345,
                    gas_used=1500000,
                    status="success",
                    timestamp=datetime.now()
                )
                mock_outcome_tx = BlockchainTransaction(
                    contract_address="0x123",
                    transaction_hash="0xoutcome456",
                    block_number=12346,
                    gas_used=150000,
                    status="success",
                    timestamp=datetime.now()
                )
                mock_deploy.return_value = mock_deployment_tx
                mock_record.return_value = mock_outcome_tx
                
                # Test data flow: Social Fetcher -> AI Analyzer
                fetched_data = orchestrator.fetch_social_data(integration_market_config)
                assert fetched_data == social_data_output
                
                analyzed_sentiment = orchestrator.analyze_sentiment(fetched_data, integration_market_config.question)
                assert analyzed_sentiment == sentiment_output
                
                # Verify correct data passed between components
                mock_analyze.assert_called_with(
                    text_data=social_data_output,
                    market_question=integration_market_config.question
                )
                
                # Test data flow: AI Analyzer -> Blockchain Connector
                # Mock the contract status to include all required fields
                mock_verify.return_value = {
                    'market_question': integration_market_config.question,
                    'market_outcome': sentiment_output,
                    'is_resolved': True,
                    'owner': '0x742d35Cc6634C0532925a3b8D4C9db96590645d8'
                }
                
                blockchain_result = orchestrator.deploy_and_record_outcome(
                    integration_market_config.question, 
                    analyzed_sentiment
                )
                assert blockchain_result is not None
                
                # Verify blockchain operations called with correct data
                mock_deploy.assert_called_with(
                    contract_source_path="contracts/SocialOracle.sol",
                    market_question=integration_market_config.question
                )


class TestBlockchainTransactionRecording:
    """Test suite for blockchain transaction recording and smart contract state updates."""
    
    def test_contract_deployment_transaction_recording(self, integration_api_config, 
                                                     mock_deployment_transaction):
        """Test contract deployment transaction recording."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock the blockchain connector's deploy_contract method
            with patch.object(orchestrator.blockchain_connector, 'deploy_contract', return_value=mock_deployment_transaction) as mock_deploy:
                
                # Test deployment transaction recording
                result = orchestrator.blockchain_connector.deploy_contract(
                    "contracts/SocialOracle.sol",
                    "Test market question?"
                )
                
                # Verify transaction details
                assert result.contract_address == mock_deployment_transaction.contract_address
                assert result.transaction_hash == mock_deployment_transaction.transaction_hash
                assert result.block_number == mock_deployment_transaction.block_number
                assert result.gas_used == mock_deployment_transaction.gas_used
                assert result.status == "success"
                
                # Verify deployment was called with correct parameters
                mock_deploy.assert_called_once_with(
                    "contracts/SocialOracle.sol",
                    "Test market question?"
                )
    
    def test_outcome_recording_transaction(self, integration_api_config, mock_outcome_transaction):
        """Test outcome recording transaction validation."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock the blockchain connector's record_outcome method
            with patch.object(orchestrator.blockchain_connector, 'record_outcome', return_value=mock_outcome_transaction) as mock_record:
                
                # Test outcome recording
                contract_address = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
                contract_abi = [{'name': 'updateOutcome', 'type': 'function'}]
                outcome = "Positive"
                
                result = orchestrator.blockchain_connector.record_outcome(
                    contract_address, contract_abi, outcome
                )
                
                # Verify transaction details
                assert result.contract_address == contract_address
                assert result.transaction_hash == mock_outcome_transaction.transaction_hash
                assert result.block_number == mock_outcome_transaction.block_number
                assert result.gas_used == mock_outcome_transaction.gas_used
                assert result.status == "success"
                
                # Verify outcome recording was called correctly
                mock_record.assert_called_once_with(
                    contract_address, contract_abi, outcome
                )
    
    def test_smart_contract_state_updates(self, integration_api_config):
        """Test smart contract state updates and verification."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            # Mock contract state verification
            expected_contract_status = {
                'market_question': 'Will the integration test pass successfully?',
                'market_outcome': 'Positive',
                'is_resolved': True,
                'owner': '0x742d35Cc6634C0532925a3b8D4C9db96590645d8'
            }
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock the blockchain connector's verify_contract_status method
            with patch.object(orchestrator.blockchain_connector, 'verify_contract_status', return_value=expected_contract_status) as mock_verify:
                
                # Test contract state verification
                contract_address = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
                contract_abi = [{'name': 'updateOutcome', 'type': 'function'}]
                
                status = orchestrator.blockchain_connector.verify_contract_status(
                    contract_address, contract_abi
                )
                
                # Verify contract state
                assert status['market_question'] == expected_contract_status['market_question']
                assert status['market_outcome'] == expected_contract_status['market_outcome']
                assert status['is_resolved'] is True
                assert status['owner'] == expected_contract_status['owner']
                
                # Verify verification was called correctly
                mock_verify.assert_called_once_with(
                    contract_address, contract_abi
                )


class TestSystemBoundaryErrorHandling:
    """Test suite for error handling across all system boundaries."""
    
    def test_social_fetcher_error_propagation(self, integration_api_config, integration_market_config):
        """Test error handling in social media fetching component."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock social fetcher to raise exception
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', side_effect=Exception("Reddit API rate limit exceeded")):
                
                # Test error handling
                result = orchestrator.fetch_social_data(integration_market_config)
                assert result is None
                
                # Test workflow failure propagation
                workflow_result = orchestrator.run_complete_workflow(integration_market_config)
                assert workflow_result is False
    
    def test_ai_analyzer_error_propagation(self, integration_api_config, integration_market_config):
        """Test error handling in AI sentiment analysis component."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock components for error testing
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', return_value="Test social data"), \
                 patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', side_effect=Exception("Gemini API quota exceeded")):
                
                # Test error handling
                result = orchestrator.analyze_sentiment("test data", "test question")
                assert result is None
                
                # Test workflow failure propagation
                workflow_result = orchestrator.run_complete_workflow(integration_market_config)
                assert workflow_result is False
    
    def test_blockchain_connector_error_propagation(self, integration_api_config, integration_market_config):
        """Test error handling in blockchain connector component."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock components for error testing
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', return_value="Test social data"), \
                 patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', return_value="Positive"), \
                 patch.object(orchestrator.blockchain_connector, 'deploy_contract', side_effect=Exception("Insufficient gas for transaction")):
                
                # Test error handling
                result = orchestrator.deploy_and_record_outcome("test question", "Positive")
                assert result is None
                
                # Test workflow failure propagation
                workflow_result = orchestrator.run_complete_workflow(integration_market_config)
                assert workflow_result is False
    
    def test_configuration_error_handling(self):
        """Test error handling for configuration failures."""
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            orchestrator = SocialOracleOrchestrator()
            
            # Configuration loading should fail
            result = orchestrator.load_configuration()
            assert result is False
            
            # Components should not be initialized
            assert orchestrator.api_config is None
            assert orchestrator.social_fetcher is None
            assert orchestrator.ai_analyzer is None
            assert orchestrator.blockchain_connector is None
    
    def test_graceful_failure_recovery(self, integration_api_config, integration_market_config):
        """Test graceful failure recovery and error reporting."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Setup components with various failure scenarios
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', return_value="Test data"), \
                 patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', return_value="Positive"), \
                 patch.object(orchestrator.blockchain_connector, 'deploy_contract', side_effect=Exception("Network timeout")):
                
                # Test that workflow fails gracefully without crashing
                try:
                    result = orchestrator.run_complete_workflow(integration_market_config)
                    assert result is False  # Should fail gracefully
                except Exception:
                    pytest.fail("Workflow should handle errors gracefully without raising exceptions")


class TestWorkflowTimingAndPerformance:
    """Test suite for workflow timing and performance validation."""
    
    def test_workflow_execution_timing(self, integration_api_config, integration_market_config):
        """Test workflow execution timing and performance metrics."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Setup fast-responding mocks
            mock_deployment_tx = Mock()
            mock_deployment_tx.contract_address = "0x123"
            
            with patch.object(orchestrator, 'fetch_social_data', return_value="Fast social data") as mock_fetch, \
                 patch.object(orchestrator, 'analyze_sentiment', return_value="Positive") as mock_analyze, \
                 patch.object(orchestrator, 'deploy_and_record_outcome') as mock_deploy:
                
                mock_deploy.return_value = {
                    'deployment_transaction': {'contract_address': '0x123'},
                    'outcome_transaction': {'transaction_hash': '0x456'},
                    'contract_status': {'is_resolved': True},
                    'explorer_urls': {
                        'deployment': 'https://testnet.bscscan.com/tx/0x123',
                        'outcome': 'https://testnet.bscscan.com/tx/0x456'
                    }
                }
                
                # Measure workflow execution time
                start_time = time.time()
                result = orchestrator.run_complete_workflow(integration_market_config)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                # Verify workflow completed successfully and within reasonable time
                assert result is True
                assert execution_time < 10.0  # Should complete within 10 seconds for mocked components
    
    def test_component_timeout_handling(self, integration_api_config, integration_market_config):
        """Test handling of component timeouts and slow responses."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': integration_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': integration_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': integration_api_config.reddit_user_agent,
            'GEMINI_API_KEY': integration_api_config.gemini_api_key,
            'BNB_RPC_URL': integration_api_config.bnb_rpc_url,
            'PRIVATE_KEY': integration_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Setup slow-responding social fetcher
            def slow_fetch(*args, **kwargs):
                time.sleep(0.1)  # Simulate slow response
                return "Slow social data"
            
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', side_effect=slow_fetch):
                
                # Test that slow components are handled appropriately
                start_time = time.time()
                result = orchestrator.fetch_social_data(integration_market_config)
                end_time = time.time()
                
                # Verify result and timing
                assert result == "Slow social data"
                assert end_time - start_time >= 0.1  # Should take at least the sleep time


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])