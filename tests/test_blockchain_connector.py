"""
Unit tests for blockchain connector component.
Tests contract deployment and outcome recording with mocked Web3 interactions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import datetime
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the web3 and solcx modules before importing blockchain_connector
sys.modules['web3'] = Mock()
sys.modules['web3.contract'] = Mock()
sys.modules['solcx'] = Mock()

from blockchain_connector import BlockchainConnector, BlockchainTransaction


class TestBlockchainConnector:
    """Test suite for BlockchainConnector class."""
    
    @pytest.fixture
    def mock_web3(self):
        """Mock Web3 instance for testing."""
        with patch('blockchain_connector.Web3') as mock_w3_class:
            mock_w3 = Mock()
            mock_w3_class.return_value = mock_w3
            mock_w3.is_connected.return_value = True
            mock_w3.eth.get_transaction_count.return_value = 1
            mock_w3.eth.gas_price = 20000000000  # 20 Gwei
            mock_w3.to_wei.return_value = 5000000000  # 5 Gwei
            mock_w3.is_address.return_value = True
            mock_w3.to_checksum_address.return_value = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
            
            # Mock account
            mock_account = Mock()
            mock_account.address = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
            mock_w3.eth.account.from_key.return_value = mock_account
            
            yield mock_w3
    
    @pytest.fixture
    def mock_solc(self):
        """Mock Solidity compiler for testing."""
        with patch('blockchain_connector.compile_source') as mock_compile, \
             patch('blockchain_connector.install_solc') as mock_install:
            
            mock_compile.return_value = {
                '<stdin>:SocialOracle': {
                    'abi': [
                        {
                            'inputs': [{'name': '_marketQuestion', 'type': 'string'}],
                            'name': 'constructor',
                            'type': 'constructor'
                        },
                        {
                            'inputs': [{'name': '_newOutcome', 'type': 'string'}],
                            'name': 'updateOutcome',
                            'type': 'function'
                        }
                    ],
                    'bin': '0x608060405234801561001057600080fd5b50...'
                }
            }
            yield mock_compile
    
    @pytest.fixture
    def connector(self, mock_web3, mock_solc):
        """Create BlockchainConnector instance for testing."""
        rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
        private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        return BlockchainConnector(rpc_url, private_key)
    
    def test_init_success(self, mock_web3, mock_solc):
        """Test successful initialization of BlockchainConnector."""
        rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
        private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        connector = BlockchainConnector(rpc_url, private_key)
        
        assert connector.private_key == private_key
        assert connector.address == "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
        mock_web3.is_connected.assert_called_once()
    
    def test_init_invalid_private_key(self, mock_web3, mock_solc):
        """Test initialization with invalid private key format."""
        rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
        invalid_key = "invalid_key"
        
        with pytest.raises(ValueError, match="Private key must be 66 characters long"):
            BlockchainConnector(rpc_url, invalid_key)
    
    def test_init_connection_failure(self, mock_solc):
        """Test initialization with connection failure."""
        with patch('blockchain_connector.Web3') as mock_w3_class:
            mock_w3 = Mock()
            mock_w3_class.return_value = mock_w3
            mock_w3.is_connected.return_value = False
            
            rpc_url = "https://invalid-rpc-url.com"
            private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            
            with pytest.raises(ConnectionError, match="Unable to connect to blockchain"):
                BlockchainConnector(rpc_url, private_key)
    
    def test_deploy_contract_success(self, connector, mock_web3, mock_solc):
        """Test successful contract deployment."""
        # Mock file reading
        contract_source = "pragma solidity ^0.8.0; contract SocialOracle {}"
        
        with patch('builtins.open', mock_open_read_data(contract_source)), \
             patch('os.path.exists', return_value=True):
            
            # Mock contract and transaction
            mock_contract = Mock()
            mock_constructor = Mock()
            mock_constructor.build_transaction.return_value = {
                'from': connector.address,
                'nonce': 1,
                'gas': 2000000,
                'gasPrice': 22000000000
            }
            mock_contract.constructor.return_value = mock_constructor
            mock_web3.eth.contract.return_value = mock_contract
            
            # Mock transaction signing and sending
            mock_signed_txn = Mock()
            mock_signed_txn.rawTransaction = b'signed_transaction_data'
            mock_web3.eth.account.sign_transaction.return_value = mock_signed_txn
            
            tx_hash = b'\x12\x34\x56\x78' * 8  # 32 bytes
            mock_web3.eth.send_raw_transaction.return_value = tx_hash
            
            # Mock transaction receipt
            mock_receipt = Mock()
            mock_receipt.status = 1
            mock_receipt.contractAddress = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
            mock_receipt.blockNumber = 12345
            mock_receipt.gasUsed = 1500000
            mock_web3.eth.wait_for_transaction_receipt.return_value = mock_receipt
            
            # Execute deployment
            result = connector.deploy_contract("contracts/SocialOracle.sol", "Test market question?")
            
            # Verify result
            assert isinstance(result, BlockchainTransaction)
            assert result.contract_address == "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
            assert result.status == "success"
            assert result.block_number == 12345
            assert result.gas_used == 1500000
    
    def test_deploy_contract_file_not_found(self, connector):
        """Test contract deployment with missing source file."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Contract source not found"):
                connector.deploy_contract("nonexistent.sol", "Test question?")
    
    def test_deploy_contract_compilation_failure(self, connector, mock_solc):
        """Test contract deployment with compilation failure."""
        mock_solc.side_effect = Exception("Compilation error")
        
        with patch('builtins.open', mock_open_read_data("invalid solidity")), \
             patch('os.path.exists', return_value=True):
            
            with pytest.raises(ValueError, match="Contract compilation failed"):
                connector.deploy_contract("contracts/SocialOracle.sol", "Test question?")
    
    def test_record_outcome_success(self, connector, mock_web3):
        """Test successful outcome recording."""
        contract_address = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
        contract_abi = [{'name': 'updateOutcome', 'type': 'function'}]
        outcome = "Positive"
        
        # Mock contract and function
        mock_contract = Mock()
        mock_function = Mock()
        mock_function.build_transaction.return_value = {
            'from': connector.address,
            'nonce': 1,
            'gas': 200000,
            'gasPrice': 22000000000
        }
        mock_contract.functions.updateOutcome.return_value = mock_function
        mock_web3.eth.contract.return_value = mock_contract
        
        # Mock transaction signing and sending
        mock_signed_txn = Mock()
        mock_signed_txn.rawTransaction = b'signed_transaction_data'
        mock_web3.eth.account.sign_transaction.return_value = mock_signed_txn
        
        tx_hash = b'\x12\x34\x56\x78' * 8  # 32 bytes
        mock_web3.eth.send_raw_transaction.return_value = tx_hash
        
        # Mock transaction receipt
        mock_receipt = Mock()
        mock_receipt.status = 1
        mock_receipt.blockNumber = 12346
        mock_receipt.gasUsed = 150000
        mock_web3.eth.wait_for_transaction_receipt.return_value = mock_receipt
        
        # Execute outcome recording
        result = connector.record_outcome(contract_address, contract_abi, outcome)
        
        # Verify result
        assert isinstance(result, BlockchainTransaction)
        assert result.contract_address == contract_address
        assert result.status == "success"
        assert result.block_number == 12346
        assert result.gas_used == 150000
    
    def test_record_outcome_invalid_outcome(self, connector):
        """Test outcome recording with invalid outcome value."""
        contract_address = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
        contract_abi = []
        invalid_outcome = "Invalid"
        
        with pytest.raises(ValueError, match="Invalid outcome 'Invalid'"):
            connector.record_outcome(contract_address, contract_abi, invalid_outcome)
    
    def test_record_outcome_invalid_address(self, connector, mock_web3):
        """Test outcome recording with invalid contract address."""
        mock_web3.is_address.return_value = False
        
        invalid_address = "invalid_address"
        contract_abi = []
        outcome = "Positive"
        
        with pytest.raises(ValueError, match="Invalid contract address"):
            connector.record_outcome(invalid_address, contract_abi, outcome)
    
    def test_get_contract_abi_success(self, connector, mock_solc):
        """Test successful ABI retrieval."""
        contract_source = "pragma solidity ^0.8.0; contract SocialOracle {}"
        
        with patch('builtins.open', mock_open_read_data(contract_source)), \
             patch('os.path.exists', return_value=True):
            
            abi = connector.get_contract_abi("contracts/SocialOracle.sol")
            
            assert isinstance(abi, list)
            assert len(abi) == 2  # constructor and updateOutcome
    
    def test_get_contract_abi_file_not_found(self, connector):
        """Test ABI retrieval with missing source file."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Contract source not found"):
                connector.get_contract_abi("nonexistent.sol")
    
    def test_verify_contract_status_success(self, connector, mock_web3):
        """Test successful contract status verification."""
        contract_address = "0x742d35Cc6634C0532925a3b8D4C9db96590645d8"
        contract_abi = []
        
        # Mock contract functions
        mock_contract = Mock()
        mock_contract.functions.getMarketStatus.return_value.call.return_value = (
            "Test question?", "Positive", True
        )
        mock_contract.functions.owner.return_value.call.return_value = connector.address
        mock_web3.eth.contract.return_value = mock_contract
        
        # Execute status verification
        status = connector.verify_contract_status(contract_address, contract_abi)
        
        # Verify result
        assert status['contract_address'] == contract_address
        assert status['owner'] == connector.address
        assert status['market_question'] == "Test question?"
        assert status['market_outcome'] == "Positive"
        assert status['is_resolved'] is True
        assert status['is_owner'] is True
    
    def test_verify_contract_status_invalid_address(self, connector, mock_web3):
        """Test contract status verification with invalid address."""
        mock_web3.is_address.return_value = False
        
        invalid_address = "invalid_address"
        contract_abi = []
        
        with pytest.raises(ValueError, match="Invalid contract address"):
            connector.verify_contract_status(invalid_address, contract_abi)
    
    def test_get_block_explorer_url(self, connector):
        """Test block explorer URL generation."""
        tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        expected_url = f"https://testnet.bscscan.com/tx/{tx_hash}"
        
        url = connector.get_block_explorer_url(tx_hash)
        
        assert url == expected_url
    
    def test_estimate_gas_price_success(self, connector, mock_web3):
        """Test gas price estimation."""
        mock_web3.eth.gas_price = 20000000000  # 20 Gwei
        
        gas_price = connector._estimate_gas_price()
        
        # Should be 10% higher than base price
        assert gas_price == 22000000000  # 22 Gwei
    
    def test_estimate_gas_price_fallback(self, connector, mock_web3):
        """Test gas price estimation with fallback."""
        mock_web3.eth.gas_price = None
        mock_web3.to_wei.return_value = 5000000000  # 5 Gwei
        
        # Mock the gas_price property to raise an exception
        type(mock_web3.eth).gas_price = PropertyMock(side_effect=Exception("Network error"))
        
        gas_price = connector._estimate_gas_price()
        
        assert gas_price == 5000000000  # Should use fallback


def mock_open_read_data(read_data):
    """Helper function to mock file reading."""
    mock_file = MagicMock()
    mock_file.read.return_value = read_data
    mock_file.__enter__.return_value = mock_file
    return MagicMock(return_value=mock_file)


