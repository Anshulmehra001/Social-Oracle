"""
Blockchain connector for interacting with BNB Smart Chain Testnet.
Handles smart contract deployment and outcome recording.
"""

import json
import logging
from typing import Dict, Any, Optional
from web3 import Web3
from web3.contract import Contract
from solcx import compile_source, install_solc
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BlockchainTransaction:
    """Data class for blockchain transaction information."""
    contract_address: str
    transaction_hash: str
    block_number: int
    gas_used: int
    status: str
    timestamp: datetime


class BlockchainConnector:
    """
    Handles blockchain interactions for the Social Oracle system.
    Connects to BNB Smart Chain Testnet for contract deployment and updates.
    """
    
    def __init__(self, rpc_url: str, private_key: str):
        """
        Initialize blockchain connector with network configuration.
        
        Args:
            rpc_url: BNB Smart Chain Testnet RPC endpoint
            private_key: Private key for transaction signing (with 0x prefix)
        
        Raises:
            ValueError: If private key format is invalid
            ConnectionError: If unable to connect to blockchain network
        """
        self.logger = logging.getLogger(__name__)
        
        # Validate private key format
        if not private_key.startswith('0x') or len(private_key) != 66:
            raise ValueError("Private key must be 66 characters long and start with '0x'")
        
        # Initialize Web3 connection
        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not self.w3.is_connected():
                raise ConnectionError(f"Unable to connect to blockchain at {rpc_url}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Web3 connection: {str(e)}")
        
        # Set up account
        self.private_key = private_key
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        
        self.logger.info(f"Blockchain connector initialized for address: {self.address}")
        
        # Install Solidity compiler if needed
        try:
            install_solc('0.8.0')
        except Exception as e:
            self.logger.warning(f"Could not install Solidity compiler: {str(e)}")
    
    def _get_nonce(self) -> int:
        """Get the current nonce for the account."""
        return self.w3.eth.get_transaction_count(self.address)
    
    def _estimate_gas_price(self) -> int:
        """Estimate appropriate gas price for the network."""
        try:
            gas_price = self.w3.eth.gas_price
            # Add 10% buffer for faster confirmation
            return int(gas_price * 1.1)
        except Exception as e:
            self.logger.warning(f"Could not get gas price, using default: {str(e)}")
            return self.w3.to_wei('5', 'gwei')  # Default 5 Gwei
    
    def deploy_contract(self, contract_source_path: str, market_question: str) -> BlockchainTransaction:
        """
        Deploy SocialOracle smart contract to BNB Smart Chain Testnet.
        
        Args:
            contract_source_path: Path to the Solidity contract file
            market_question: The prediction market question to initialize
        
        Returns:
            BlockchainTransaction: Transaction details including contract address
        
        Raises:
            FileNotFoundError: If contract source file not found
            ValueError: If contract compilation fails
            Exception: If deployment transaction fails
        """
        self.logger.info(f"Deploying contract with market question: {market_question}")
        
        # Read contract source
        if not os.path.exists(contract_source_path):
            raise FileNotFoundError(f"Contract source not found: {contract_source_path}")
        
        with open(contract_source_path, 'r') as file:
            contract_source = file.read()
        
        # Compile contract
        try:
            compiled_sol = compile_source(contract_source)
            contract_interface = compiled_sol['<stdin>:SocialOracle']
        except Exception as e:
            raise ValueError(f"Contract compilation failed: {str(e)}")
        
        # Create contract instance
        contract = self.w3.eth.contract(
            abi=contract_interface['abi'],
            bytecode=contract_interface['bin']
        )
        
        # Build deployment transaction
        constructor_txn = contract.constructor(market_question).build_transaction({
            'from': self.address,
            'nonce': self._get_nonce(),
            'gas': 2000000,  # Conservative gas limit
            'gasPrice': self._estimate_gas_price(),
        })
        
        # Sign and send transaction
        try:
            signed_txn = self.w3.eth.account.sign_transaction(constructor_txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(f"Contract deployment transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status != 1:
                raise Exception(f"Contract deployment failed with status: {tx_receipt.status}")
            
            contract_address = tx_receipt.contractAddress
            self.logger.info(f"Contract deployed successfully at: {contract_address}")
            
            return BlockchainTransaction(
                contract_address=contract_address,
                transaction_hash=tx_hash.hex(),
                block_number=tx_receipt.blockNumber,
                gas_used=tx_receipt.gasUsed,
                status="success",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Contract deployment failed: {str(e)}")
            raise Exception(f"Failed to deploy contract: {str(e)}")
    
    def record_outcome(self, contract_address: str, contract_abi: list, outcome: str) -> BlockchainTransaction:
        """
        Record sentiment outcome in the deployed smart contract.
        
        Args:
            contract_address: Address of the deployed SocialOracle contract
            contract_abi: ABI of the contract for interaction
            outcome: Sentiment outcome ("Positive", "Negative", or "Neutral")
        
        Returns:
            BlockchainTransaction: Transaction details for the outcome update
        
        Raises:
            ValueError: If outcome format is invalid or contract address is invalid
            Exception: If transaction fails
        """
        self.logger.info(f"Recording outcome '{outcome}' to contract: {contract_address}")
        
        # Validate outcome
        valid_outcomes = ["Positive", "Negative", "Neutral"]
        if outcome not in valid_outcomes:
            raise ValueError(f"Invalid outcome '{outcome}'. Must be one of: {valid_outcomes}")
        
        # Validate contract address
        if not self.w3.is_address(contract_address):
            raise ValueError(f"Invalid contract address: {contract_address}")
        
        # Create contract instance
        try:
            contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(contract_address),
                abi=contract_abi
            )
        except Exception as e:
            raise ValueError(f"Failed to create contract instance: {str(e)}")
        
        # Build transaction for updateOutcome function
        try:
            update_txn = contract.functions.updateOutcome(outcome).build_transaction({
                'from': self.address,
                'nonce': self._get_nonce(),
                'gas': 200000,  # Conservative gas limit for update
                'gasPrice': self._estimate_gas_price(),
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(update_txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(f"Outcome update transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status != 1:
                raise Exception(f"Outcome update failed with status: {tx_receipt.status}")
            
            self.logger.info(f"Outcome recorded successfully in block: {tx_receipt.blockNumber}")
            
            return BlockchainTransaction(
                contract_address=contract_address,
                transaction_hash=tx_hash.hex(),
                block_number=tx_receipt.blockNumber,
                gas_used=tx_receipt.gasUsed,
                status="success",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to record outcome: {str(e)}")
            raise Exception(f"Failed to record outcome: {str(e)}")
    
    def get_contract_abi(self, contract_source_path: str) -> list:
        """
        Compile contract and return ABI for interaction.
        
        Args:
            contract_source_path: Path to the Solidity contract file
        
        Returns:
            list: Contract ABI
        
        Raises:
            FileNotFoundError: If contract source file not found
            ValueError: If contract compilation fails
        """
        if not os.path.exists(contract_source_path):
            raise FileNotFoundError(f"Contract source not found: {contract_source_path}")
        
        with open(contract_source_path, 'r') as file:
            contract_source = file.read()
        
        try:
            compiled_sol = compile_source(contract_source)
            contract_interface = compiled_sol['<stdin>:SocialOracle']
            return contract_interface['abi']
        except Exception as e:
            raise ValueError(f"Contract compilation failed: {str(e)}")
    
    def verify_contract_status(self, contract_address: str, contract_abi: list) -> Dict[str, Any]:
        """
        Verify the current status of a deployed contract.
        
        Args:
            contract_address: Address of the deployed contract
            contract_abi: ABI of the contract
        
        Returns:
            Dict containing contract status information
        
        Raises:
            ValueError: If contract address is invalid
            Exception: If contract interaction fails
        """
        if not self.w3.is_address(contract_address):
            raise ValueError(f"Invalid contract address: {contract_address}")
        
        try:
            contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(contract_address),
                abi=contract_abi
            )
            
            # Get contract status
            question, outcome, resolved = contract.functions.getMarketStatus().call()
            owner = contract.functions.owner().call()
            
            return {
                'contract_address': contract_address,
                'owner': owner,
                'market_question': question,
                'market_outcome': outcome,
                'is_resolved': resolved,
                'is_owner': owner.lower() == self.address.lower()
            }
            
        except Exception as e:
            raise Exception(f"Failed to verify contract status: {str(e)}")
    
    def get_block_explorer_url(self, tx_hash: str) -> str:
        """
        Generate block explorer URL for transaction verification.
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            str: BNB Smart Chain Testnet block explorer URL
        """
        return f"https://testnet.bscscan.com/tx/{tx_hash}"