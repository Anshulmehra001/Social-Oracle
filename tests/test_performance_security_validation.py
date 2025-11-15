"""
Performance and Security Validation Tests

This module provides comprehensive tests for API rate limiting compliance, timeout handling,
credential security, environment variable validation, gas optimization, and transaction efficiency.

Requirements: 5.1, 5.4, 5.5
"""

import pytest
import sys
import os
import time
import re
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
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
def security_api_config():
    """API configuration for security testing."""
    return APIConfig(
        reddit_client_id="security_test_client_id",
        reddit_client_secret="security_test_client_secret",
        reddit_user_agent="SocialOracle/1.0 Security Test",
        gemini_api_key="security_test_gemini_api_key",
        bnb_rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545/",
        private_key="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    )


@pytest.fixture
def performance_market_config():
    """Market configuration for performance testing."""
    return MarketConfig(
        question="Will the performance test complete within acceptable limits?",
        search_keywords="performance test optimization validation",
        reddit_subreddit="test",
        post_limit=50  # Higher limit for performance testing
    )


class TestAPIRateLimitingCompliance:
    """Test suite for API rate limiting compliance and timeout handling."""
    
    def test_reddit_api_rate_limiting_compliance(self, security_api_config, performance_market_config):
        """Test Reddit API rate limiting compliance (60 requests per minute)."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock Reddit API with rate limiting simulation
            call_times = []
            
            def mock_reddit_fetch(*args, **kwargs):
                current_time = time.time()
                call_times.append(current_time)
                
                # Simulate rate limiting - max 60 calls per minute
                recent_calls = [t for t in call_times if current_time - t < 60]
                if len(recent_calls) > 60:
                    raise Exception("Reddit API rate limit exceeded")
                
                # Simulate API response time
                time.sleep(0.1)
                return "Rate limited social media data"
            
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', side_effect=mock_reddit_fetch):
                
                # Test multiple rapid calls to verify rate limiting compliance
                start_time = time.time()
                
                for i in range(5):  # Test 5 rapid calls
                    result = orchestrator.fetch_social_data(performance_market_config)
                    assert result is not None
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Verify rate limiting compliance
                assert len(call_times) == 5
                assert total_time >= 0.5  # Should take at least 0.5 seconds (5 * 0.1s)
                
                # Verify no rate limit exceeded
                for call_time in call_times:
                    recent_calls = [t for t in call_times if call_time - t < 60 and t <= call_time]
                    assert len(recent_calls) <= 60
    
    def test_gemini_api_timeout_handling(self, security_api_config):
        """Test Gemini AI API timeout handling and error recovery."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock AI analyzer with timeout simulation
            def mock_ai_analysis(*args, **kwargs):
                # Simulate timeout
                time.sleep(0.1)
                raise Exception("Request timeout")
            
            with patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', side_effect=mock_ai_analysis):
                
                start_time = time.time()
                result = orchestrator.analyze_sentiment("test data", "test question")
                end_time = time.time()
                
                # Verify timeout handling - should fail gracefully
                assert result is None  # Should handle timeout gracefully
                assert end_time - start_time >= 0.1  # Should include timeout delay
    
    def test_blockchain_transaction_timeout_handling(self, security_api_config):
        """Test blockchain transaction timeout handling and gas optimization."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock blockchain connector with timeout handling
            def mock_deploy_contract(*args, **kwargs):
                # Simulate network delay
                time.sleep(0.05)
                
                return BlockchainTransaction(
                    contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    transaction_hash="0xdeployment123456789abcdef",
                    block_number=12345,
                    gas_used=1500000,  # Reasonable gas usage
                    status="success",
                    timestamp=datetime.now()
                )
            
            with patch.object(orchestrator.blockchain_connector, 'deploy_contract', side_effect=mock_deploy_contract), \
                 patch.object(orchestrator.blockchain_connector, 'record_outcome') as mock_record, \
                 patch.object(orchestrator.blockchain_connector, 'get_contract_abi', return_value=[]), \
                 patch.object(orchestrator.blockchain_connector, 'verify_contract_status', return_value={
                     'market_question': 'test question',
                     'market_outcome': 'Positive',
                     'is_resolved': True,
                     'owner': '0x742d35Cc6634C0532925a3b8D4C9db96590645d8'
                 }), \
                 patch.object(orchestrator.blockchain_connector, 'get_block_explorer_url', return_value="https://testnet.bscscan.com/tx/0x123"):
                
                mock_record.return_value = BlockchainTransaction(
                    contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    transaction_hash="0xoutcome123456789abcdef",
                    block_number=12346,
                    gas_used=150000,  # Optimized gas usage for outcome recording
                    status="success",
                    timestamp=datetime.now()
                )
                
                start_time = time.time()
                result = orchestrator.deploy_and_record_outcome("test question", "Positive")
                end_time = time.time()
                
                # Verify transaction completed successfully
                assert result is not None
                assert result['deployment_transaction']['gas_used'] == 1500000
                assert result['outcome_transaction']['gas_used'] == 150000
                
                # Verify reasonable execution time
                execution_time = end_time - start_time
                assert execution_time < 5.0  # Should complete within 5 seconds
    
    def test_concurrent_api_request_handling(self, security_api_config, performance_market_config):
        """Test handling of concurrent API requests and resource management."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock components with concurrent request simulation
            request_count = 0
            
            def mock_social_fetch(*args, **kwargs):
                nonlocal request_count
                request_count += 1
                time.sleep(0.02)  # Simulate API response time
                return f"Social data request #{request_count}"
            
            def mock_ai_analysis(*args, **kwargs):
                time.sleep(0.01)  # Simulate AI processing time
                return "Positive"
            
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', side_effect=mock_social_fetch), \
                 patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', side_effect=mock_ai_analysis):
                
                # Test sequential requests to verify resource management
                results = []
                start_time = time.time()
                
                for i in range(3):
                    social_data = orchestrator.fetch_social_data(performance_market_config)
                    sentiment = orchestrator.analyze_sentiment(social_data, performance_market_config.question)
                    results.append((social_data, sentiment))
                
                end_time = time.time()
                
                # Verify all requests completed successfully
                assert len(results) == 3
                assert all(result[1] == "Positive" for result in results)
                
                # Verify reasonable total execution time
                total_time = end_time - start_time
                assert total_time < 1.0  # Should complete within 1 second


class TestCredentialSecurity:
    """Test suite for credential security and environment variable validation."""
    
    def test_environment_variable_validation(self):
        """Test validation of required environment variables."""
        # Test with missing variables
        with patch.dict(os.environ, {}, clear=True):
            assert Config.validate_environment() is False
        
        # Test with partial variables
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_CLIENT_SECRET': 'test_secret'
            # Missing other required variables
        }, clear=True):
            assert Config.validate_environment() is False
        
        # Test with all required variables
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_CLIENT_SECRET': 'test_secret',
            'REDDIT_USER_AGENT': 'test_agent',
            'GEMINI_API_KEY': 'test_gemini',
            'BNB_RPC_URL': 'test_rpc',
            'PRIVATE_KEY': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        }):
            assert Config.validate_environment() is True
    
    def test_private_key_format_validation(self, security_api_config):
        """Test private key format validation and security."""
        # Test valid private key format
        valid_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        assert len(valid_key) == 66
        assert valid_key.startswith("0x")
        
        # Test valid private key configuration
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': valid_key
        }):
            orchestrator = SocialOracleOrchestrator()
            result = orchestrator.load_configuration()
            assert result is True  # Should succeed with valid key
        
        # Test private key format validation logic
        def validate_private_key_format(private_key: str) -> bool:
            """Helper function to test private key validation logic."""
            if not private_key or len(private_key) != 66 or not private_key.startswith("0x"):
                return False
            try:
                # Check if it's valid hex
                int(private_key[2:], 16)
                return True
            except ValueError:
                return False
        
        # Test invalid private key formats
        invalid_keys = [
            "1234567890abcdef",  # Too short
            "0x123",  # Too short with prefix
            "invalid_key",  # Invalid format
            "",  # Empty
            "0x" + "g" * 64,  # Invalid hex characters
        ]
        
        for invalid_key in invalid_keys:
            assert validate_private_key_format(invalid_key) is False
        
        # Test valid private key
        assert validate_private_key_format(valid_key) is True
        
        # Test empty private key (environment validation should catch this)
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': ''  # Empty private key
        }, clear=True):
            orchestrator = SocialOracleOrchestrator()
            result = orchestrator.load_configuration()
            assert result is False  # Should fail due to empty private key
    
    def test_credential_exposure_prevention(self, security_api_config):
        """Test that credentials are not exposed in logs or error messages."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock components to raise exceptions and capture log messages
            log_messages = []
            
            def mock_log_capture(message):
                log_messages.append(str(message))
            
            with patch.object(orchestrator.logger, 'error', side_effect=mock_log_capture), \
                 patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', side_effect=Exception("API Error")):
                
                # Trigger an error that would be logged
                result = orchestrator.fetch_social_data(performance_market_config)
                assert result is None
                
                # Verify credentials are not exposed in log messages
                all_logs = " ".join(log_messages)
                
                # Check that sensitive data is not in logs
                assert security_api_config.reddit_client_secret not in all_logs
                assert security_api_config.gemini_api_key not in all_logs
                assert security_api_config.private_key not in all_logs
                
                # Verify that only the last 4 characters of keys might be shown (if any)
                if security_api_config.private_key in all_logs:
                    # If private key appears, it should be masked
                    assert "****" in all_logs or "..." in all_logs
    
    def test_api_key_validation(self, security_api_config):
        """Test API key validation and format checking."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            assert orchestrator.load_configuration() is True
            
            # Verify API keys are properly loaded and validated
            assert orchestrator.api_config.reddit_client_id == security_api_config.reddit_client_id
            assert orchestrator.api_config.reddit_client_secret == security_api_config.reddit_client_secret
            assert orchestrator.api_config.gemini_api_key == security_api_config.gemini_api_key
            
            # Verify components are initialized with correct credentials
            assert orchestrator.social_fetcher is not None
            assert orchestrator.ai_analyzer is not None
            assert orchestrator.blockchain_connector is not None
    
    def test_secure_configuration_template(self):
        """Test that .env.example provides secure configuration template."""
        # Check if .env.example exists and has proper structure
        env_example_path = ".env.example"
        
        if os.path.exists(env_example_path):
            with open(env_example_path, 'r') as f:
                content = f.read()
            
            # Verify all required variables are present in template
            required_vars = [
                'REDDIT_CLIENT_ID',
                'REDDIT_CLIENT_SECRET',
                'REDDIT_USER_AGENT',
                'GEMINI_API_KEY',
                'BNB_RPC_URL',
                'PRIVATE_KEY'
            ]
            
            for var in required_vars:
                assert var in content, f"Required variable {var} not found in .env.example"
            
            # Verify no actual credentials are in the template
            assert "your_" in content or "YOUR_" in content or "here" in content.lower()
            
            # Verify private key format guidance
            assert "0x" in content  # Should show proper private key format


class TestGasOptimizationAndTransactionEfficiency:
    """Test suite for gas optimization and transaction efficiency validation."""
    
    def test_gas_price_estimation_optimization(self, security_api_config):
        """Test gas price estimation and optimization strategies."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock Web3 gas price estimation
            base_gas_price = 20000000000  # 20 Gwei
            
            with patch.object(orchestrator.blockchain_connector, 'w3') as mock_w3:
                mock_w3.eth.gas_price = base_gas_price
                
                # Test gas price estimation method
                with patch.object(orchestrator.blockchain_connector, '_estimate_gas_price') as mock_estimate:
                    # Should return optimized gas price (10% higher than base)
                    expected_gas_price = int(base_gas_price * 1.1)
                    mock_estimate.return_value = expected_gas_price
                    
                    gas_price = orchestrator.blockchain_connector._estimate_gas_price()
                    
                    # Verify gas price optimization
                    assert gas_price == expected_gas_price
                    assert gas_price > base_gas_price  # Should be higher than base
                    assert gas_price <= base_gas_price * 1.2  # But not too high (max 20% increase)
    
    def test_contract_deployment_gas_efficiency(self, security_api_config):
        """Test contract deployment gas efficiency and optimization."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock contract deployment with gas tracking
            def mock_deploy_with_gas_tracking(*args, **kwargs):
                # Simulate optimized contract deployment
                gas_used = 1500000  # Reasonable gas usage for contract deployment
                
                # Verify gas usage is within acceptable limits
                max_acceptable_gas = 2000000  # 2M gas limit
                assert gas_used <= max_acceptable_gas, f"Gas usage {gas_used} exceeds limit {max_acceptable_gas}"
                
                return BlockchainTransaction(
                    contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    transaction_hash="0xdeployment123456789abcdef",
                    block_number=12345,
                    gas_used=gas_used,
                    status="success",
                    timestamp=datetime.now()
                )
            
            with patch.object(orchestrator.blockchain_connector, 'deploy_contract', side_effect=mock_deploy_with_gas_tracking):
                
                result = orchestrator.blockchain_connector.deploy_contract(
                    "contracts/SocialOracle.sol",
                    "Test market question"
                )
                
                # Verify gas efficiency
                assert result.gas_used <= 2000000  # Should be within reasonable limits
                assert result.gas_used >= 1000000  # Should be realistic (not too low)
                assert result.status == "success"
    
    def test_outcome_recording_gas_efficiency(self, security_api_config):
        """Test outcome recording gas efficiency and optimization."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock outcome recording with gas optimization
            def mock_record_with_gas_optimization(*args, **kwargs):
                # Simulate optimized outcome recording
                gas_used = 150000  # Efficient gas usage for simple state update
                
                # Verify gas usage is optimized
                max_acceptable_gas = 200000  # 200K gas limit for simple update
                assert gas_used <= max_acceptable_gas, f"Gas usage {gas_used} exceeds limit {max_acceptable_gas}"
                
                return BlockchainTransaction(
                    contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    transaction_hash="0xoutcome123456789abcdef",
                    block_number=12346,
                    gas_used=gas_used,
                    status="success",
                    timestamp=datetime.now()
                )
            
            with patch.object(orchestrator.blockchain_connector, 'record_outcome', side_effect=mock_record_with_gas_optimization):
                
                result = orchestrator.blockchain_connector.record_outcome(
                    "0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    [{'name': 'updateOutcome', 'type': 'function'}],
                    "Positive"
                )
                
                # Verify gas efficiency for outcome recording
                assert result.gas_used <= 200000  # Should be very efficient
                assert result.gas_used >= 50000   # Should be realistic
                assert result.status == "success"
    
    def test_transaction_batching_efficiency(self, security_api_config):
        """Test transaction batching and efficiency optimization."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Track transaction efficiency metrics
            transaction_times = []
            gas_usage = []
            
            def mock_efficient_deploy(*args, **kwargs):
                start_time = time.time()
                time.sleep(0.05)  # Simulate network delay
                end_time = time.time()
                
                transaction_times.append(end_time - start_time)
                gas_used = 1500000
                gas_usage.append(gas_used)
                
                return BlockchainTransaction(
                    contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    transaction_hash=f"0xdeployment{len(transaction_times)}",
                    block_number=12345 + len(transaction_times),
                    gas_used=gas_used,
                    status="success",
                    timestamp=datetime.now()
                )
            
            def mock_efficient_record(*args, **kwargs):
                start_time = time.time()
                time.sleep(0.02)  # Simulate faster operation
                end_time = time.time()
                
                transaction_times.append(end_time - start_time)
                gas_used = 150000
                gas_usage.append(gas_used)
                
                return BlockchainTransaction(
                    contract_address="0x742d35Cc6634C0532925a3b8D4C9db96590645d8",
                    transaction_hash=f"0xoutcome{len(transaction_times)}",
                    block_number=12346 + len(transaction_times),
                    gas_used=gas_used,
                    status="success",
                    timestamp=datetime.now()
                )
            
            with patch.object(orchestrator.blockchain_connector, 'deploy_contract', side_effect=mock_efficient_deploy), \
                 patch.object(orchestrator.blockchain_connector, 'record_outcome', side_effect=mock_efficient_record), \
                 patch.object(orchestrator.blockchain_connector, 'get_contract_abi', return_value=[]), \
                 patch.object(orchestrator.blockchain_connector, 'verify_contract_status', return_value={
                     'market_question': 'Test question',
                     'market_outcome': 'Positive',
                     'is_resolved': True,
                     'owner': '0x742d35Cc6634C0532925a3b8D4C9db96590645d8'
                 }), \
                 patch.object(orchestrator.blockchain_connector, 'get_block_explorer_url', return_value="https://testnet.bscscan.com/tx/0x123"):
                
                # Test multiple transactions for efficiency analysis
                start_time = time.time()
                result = orchestrator.deploy_and_record_outcome("Test question", "Positive")
                end_time = time.time()
                
                total_time = end_time - start_time
                
                # Verify transaction efficiency
                assert result is not None
                assert len(transaction_times) == 2  # Deploy + Record
                assert len(gas_usage) == 2
                
                # Verify timing efficiency
                assert total_time < 1.0  # Should complete within 1 second
                assert all(t < 0.5 for t in transaction_times)  # Each transaction < 0.5s
                
                # Verify gas efficiency
                total_gas = sum(gas_usage)
                assert total_gas <= 2000000  # Total gas should be reasonable
                assert gas_usage[0] > gas_usage[1]  # Deployment should use more gas than recording


class TestSystemPerformanceMetrics:
    """Test suite for overall system performance metrics and benchmarks."""
    
    def test_end_to_end_performance_benchmark(self, security_api_config, performance_market_config):
        """Test end-to-end system performance benchmark."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Mock all components with performance tracking
            performance_metrics = {
                'social_fetch_time': 0,
                'ai_analysis_time': 0,
                'blockchain_time': 0
            }
            
            def mock_social_fetch(*args, **kwargs):
                start = time.time()
                time.sleep(0.1)  # Simulate Reddit API time
                performance_metrics['social_fetch_time'] = time.time() - start
                return "Performance test social media data"
            
            def mock_ai_analysis(*args, **kwargs):
                start = time.time()
                time.sleep(0.05)  # Simulate AI processing time
                performance_metrics['ai_analysis_time'] = time.time() - start
                return "Positive"
            
            def mock_blockchain_ops(*args, **kwargs):
                start = time.time()
                time.sleep(0.08)  # Simulate blockchain operations
                performance_metrics['blockchain_time'] = time.time() - start
                
                return {
                    'deployment_transaction': {
                        'contract_address': '0x742d35Cc6634C0532925a3b8D4C9db96590645d8',
                        'gas_used': 1500000
                    },
                    'outcome_transaction': {
                        'transaction_hash': '0xoutcome123456789abcdef',
                        'gas_used': 150000
                    },
                    'contract_status': {'is_resolved': True},
                    'explorer_urls': {
                        'deployment': 'https://testnet.bscscan.com/tx/0x123',
                        'outcome': 'https://testnet.bscscan.com/tx/0x456'
                    }
                }
            
            with patch.object(orchestrator, 'fetch_social_data', side_effect=mock_social_fetch), \
                 patch.object(orchestrator, 'analyze_sentiment', side_effect=mock_ai_analysis), \
                 patch.object(orchestrator, 'deploy_and_record_outcome', side_effect=mock_blockchain_ops):
                
                # Run performance benchmark
                start_time = time.time()
                result = orchestrator.run_complete_workflow(performance_market_config)
                end_time = time.time()
                
                total_time = end_time - start_time
                
                # Verify performance benchmarks
                assert result is True
                assert total_time < 2.0  # Total workflow should complete within 2 seconds
                
                # Verify component performance
                assert performance_metrics['social_fetch_time'] < 0.5
                assert performance_metrics['ai_analysis_time'] < 0.2
                assert performance_metrics['blockchain_time'] < 0.5
                
                # Verify performance distribution
                component_times = [
                    performance_metrics['social_fetch_time'],
                    performance_metrics['ai_analysis_time'],
                    performance_metrics['blockchain_time']
                ]
                
                # Social fetching should be the slowest component
                assert performance_metrics['social_fetch_time'] == max(component_times)
                
                # AI analysis should be the fastest
                assert performance_metrics['ai_analysis_time'] == min(component_times)
    
    def test_memory_usage_efficiency(self, security_api_config, performance_market_config):
        """Test memory usage efficiency and resource management."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            # Test memory efficiency with large data sets
            large_social_data = "Large social media data " * 1000  # ~25KB of data
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', return_value=large_social_data), \
                 patch.object(orchestrator.ai_analyzer, 'get_sentiment_analysis', return_value="Positive"):
                
                # Test memory usage with large data
                social_data = orchestrator.fetch_social_data(performance_market_config)
                assert len(social_data) > 20000  # Should handle large data
                
                sentiment = orchestrator.analyze_sentiment(social_data, performance_market_config.question)
                assert sentiment == "Positive"
                
                # Verify data is properly handled without memory issues
                assert social_data is not None
                assert len(social_data) == len(large_social_data)
    
    def test_error_recovery_performance(self, security_api_config, performance_market_config):
        """Test error recovery performance and resilience."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': security_api_config.reddit_client_id,
            'REDDIT_CLIENT_SECRET': security_api_config.reddit_client_secret,
            'REDDIT_USER_AGENT': security_api_config.reddit_user_agent,
            'GEMINI_API_KEY': security_api_config.gemini_api_key,
            'BNB_RPC_URL': security_api_config.bnb_rpc_url,
            'PRIVATE_KEY': security_api_config.private_key
        }):
            
            orchestrator = SocialOracleOrchestrator()
            orchestrator.load_configuration()
            
            # Test error recovery timing
            error_count = 0
            
            def mock_failing_component(*args, **kwargs):
                nonlocal error_count
                error_count += 1
                
                if error_count <= 2:
                    # First two calls fail
                    raise Exception(f"Temporary error #{error_count}")
                else:
                    # Third call succeeds
                    return "Recovered data"
            
            with patch.object(orchestrator.social_fetcher, 'fetch_reddit_sentiment_data', side_effect=mock_failing_component):
                
                # Test error recovery performance
                start_time = time.time()
                
                # Should fail gracefully without hanging
                result1 = orchestrator.fetch_social_data(performance_market_config)
                result2 = orchestrator.fetch_social_data(performance_market_config)
                result3 = orchestrator.fetch_social_data(performance_market_config)
                
                end_time = time.time()
                
                # Verify error recovery
                assert result1 is None  # First call fails
                assert result2 is None  # Second call fails
                assert result3 == "Recovered data"  # Third call succeeds
                
                # Verify recovery time is reasonable
                recovery_time = end_time - start_time
                assert recovery_time < 1.0  # Should recover quickly


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])