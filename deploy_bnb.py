"""
BNB Chain Deployment Script

Deploys the SocialOracle smart contract to BNB Chain testnet or mainnet.
"""

import os
import json
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Network configurations
NETWORKS = {
    'bnb_testnet': {
        'name': 'BNB Chain Testnet',
        'rpc': 'https://data-seed-prebsc-1-s1.binance.org:8545/',
        'chain_id': 97,
        'explorer': 'https://testnet.bscscan.com'
    },
    'bnb_mainnet': {
        'name': 'BNB Chain Mainnet',
        'rpc': 'https://bsc-dataseed.binance.org/',
        'chain_id': 56,
        'explorer': 'https://bscscan.com'
    }
}

def load_contract():
    """Load compiled contract ABI and bytecode."""
    # Read compiled contract (you'll need to compile SocialOracle.sol first)
    contract_path = 'contracts/SocialOracle.json'
    
    if not os.path.exists(contract_path):
        print("❌ Contract not compiled. Run: solc --abi --bin contracts/SocialOracle.sol -o contracts/")
        return None, None
    
    with open(contract_path, 'r') as f:
        contract_data = json.load(f)
        abi = contract_data.get('abi')
        bytecode = contract_data.get('bytecode')
        return abi, bytecode

def deploy_contract(network='bnb_testnet', market_question="Will BTC sentiment be positive?"):
    """
    Deploy SocialOracle contract to BNB Chain.
    
    Args:
        network: 'bnb_testnet' or 'bnb_mainnet'
        market_question: Initial market question for the oracle
    """
    
    # Get private key from environment
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("❌ PRIVATE_KEY not found in .env file")
        print("ℹ️  Add: PRIVATE_KEY=your_private_key_here")
        return None
    
    # Connect to network
    config = NETWORKS[network]
    print(f"\n🔗 Connecting to {config['name']}...")
    w3 = Web3(Web3.HTTPProvider(config['rpc']))
    
    if not w3.is_connected():
        print(f"❌ Failed to connect to {config['name']}")
        return None
    
    print(f"✅ Connected to {config['name']}")
    
    # Get account
    account = Account.from_key(private_key)
    address = account.address
    balance = w3.eth.get_balance(address)
    balance_bnb = w3.from_wei(balance, 'ether')
    
    print(f"📍 Deploying from: {address}")
    print(f"💰 Balance: {balance_bnb:.4f} BNB")
    
    if balance_bnb < 0.01:
        print("⚠️  Warning: Low balance. Get testnet BNB from https://testnet.binance.org/faucet-smart")
    
    # Load contract
    abi, bytecode = load_contract()
    if not abi or not bytecode:
        return None
    
    # Create contract instance
    print(f"\n📝 Creating contract instance...")
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Build constructor transaction
    print(f"🔨 Building deployment transaction...")
    constructor_txn = Contract.constructor(market_question).build_transaction({
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price,
        'chainId': config['chain_id']
    })
    
    # Sign transaction
    print(f"✍️  Signing transaction...")
    signed_txn = account.sign_transaction(constructor_txn)
    
    # Send transaction
    print(f"📤 Sending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"⏳ Transaction hash: {tx_hash.hex()}")
    print(f"🔗 {config['explorer']}/tx/{tx_hash.hex()}")
    
    # Wait for receipt
    print(f"⏳ Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if tx_receipt['status'] == 1:
        contract_address = tx_receipt['contractAddress']
        print(f"\n🎉 Contract deployed successfully!")
        print(f"📍 Contract address: {contract_address}")
        print(f"🔗 {config['explorer']}/address/{contract_address}")
        
        # Save to .env
        env_var = f"\nCONTRACT_ADDRESS_{network.upper()}={contract_address}\n"
        with open('.env', 'a') as f:
            f.write(env_var)
        
        print(f"\n✅ Contract address saved to .env")
        
        return contract_address
    else:
        print(f"\n❌ Deployment failed!")
        return None

def verify_deployment(network='bnb_testnet', contract_address=None):
    """
    Verify deployed contract.
    
    Args:
        network: 'bnb_testnet' or 'bnb_mainnet'
        contract_address: Address of deployed contract
    """
    if not contract_address:
        contract_address = os.getenv(f'CONTRACT_ADDRESS_{network.upper()}')
    
    if not contract_address:
        print("❌ Contract address not found")
        return False
    
    config = NETWORKS[network]
    w3 = Web3(Web3.HTTPProvider(config['rpc']))
    
    if not w3.is_connected():
        print(f"❌ Failed to connect to {config['name']}")
        return False
    
    print(f"\n🔍 Verifying contract at {contract_address}...")
    
    # Check if contract exists
    code = w3.eth.get_code(contract_address)
    if code == b'' or code == '0x':
        print(f"❌ No contract found at {contract_address}")
        return False
    
    print(f"✅ Contract verified on {config['name']}")
    print(f"🔗 {config['explorer']}/address/{contract_address}")
    
    # Load ABI and interact
    abi, _ = load_contract()
    if abi:
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        try:
            question, outcome, resolved = contract.functions.getMarketStatus().call()
            print(f"\n📊 Contract Status:")
            print(f"   Question: {question}")
            print(f"   Outcome: {outcome if outcome else 'Not resolved'}")
            print(f"   Resolved: {resolved}")
            return True
        except Exception as e:
            print(f"⚠️  Could not read contract: {e}")
            return False
    
    return True

def main():
    """Main deployment script."""
    print("╔════════════════════════════════════════════════════╗")
    print("║   Social Oracle - BNB Chain Deployment Script    ║")
    print("╚════════════════════════════════════════════════════╝")
    
    print("\nSelect network:")
    print("1. BNB Testnet (recommended for testing)")
    print("2. BNB Mainnet (production)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        network = 'bnb_testnet'
    elif choice == '2':
        confirm = input("⚠️  Deploy to MAINNET? This costs real BNB. Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("❌ Deployment cancelled")
            return
        network = 'bnb_mainnet'
    else:
        print("❌ Invalid choice")
        return
    
    market_question = input("\nEnter market question (default: 'Will BTC sentiment be positive?'): ").strip()
    if not market_question:
        market_question = "Will BTC sentiment be positive?"
    
    # Deploy
    contract_address = deploy_contract(network, market_question)
    
    if contract_address:
        # Verify
        verify_deployment(network, contract_address)
        
        print("\n" + "="*60)
        print("🎉 Deployment Complete!")
        print("="*60)
        print(f"\nNext Steps:")
        print(f"1. Update your app to use this contract address")
        print(f"2. Test sentiment recording with: python test_blockchain.py")
        print(f"3. Integrate with prediction market platforms")
        print(f"\n💡 Contract address saved to .env file")

if __name__ == "__main__":
    main()
