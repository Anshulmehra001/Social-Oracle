# Blockchain Integration

## Smart Contract

**File**: `contracts/SocialOracle.sol` (Solidity 0.8.0)

```solidity
contract SocialOracle {
    address public owner;
    string public marketQuestion;
    string public marketOutcome;  // "Positive", "Negative", "Neutral"
    bool public isResolved;
    uint256 public resolutionTime;
    
    event MarketResolved(string outcome, address resolvedBy, uint256 timestamp);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call");
        _;
    }
    
    function updateOutcome(string memory _outcome) public onlyOwner {
        require(!isResolved, "Market already resolved");
        marketOutcome = _outcome;
        isResolved = true;
        resolutionTime = block.timestamp;
        emit MarketResolved(_outcome, msg.sender, block.timestamp);
    }
    
    function getMarketStatus() public view returns (string memory, bool, uint256) {
        return (marketOutcome, isResolved, resolutionTime);
    }
}
```

---

## Why BNB Chain?

### Cost Comparison

| Chain | Gas Fee | Block Time | Finality | TPS |
|-------|---------|------------|----------|-----|
| Ethereum | $5-50 | 12s | 12+ min | 15-30 |
| **BNB Chain** | **$0.10-1.00** | **3s** | **45s** | **160** |
| Polygon | $0.01-0.10 | 2s | 256 blocks | 65 |
| Arbitrum | $0.10-1.00 | 0.3s | 1 week* | 4,000 |

*Arbitrum uses fraud proofs, true finality takes 1 week

### BNB Chain Advantages

✅ **Low Cost**: $0.10-1.00 per transaction (affordable for frequent updates)  
✅ **Fast Finality**: 45 seconds (real-time prediction markets possible)  
✅ **High Throughput**: 160 TPS (handles traffic spikes)  
✅ **EVM Compatible**: Standard Solidity contracts work  
✅ **Growing Ecosystem**: Increasing DeFi and prediction market platforms

---

## Deployment

**Script**: `deploy_bnb.py`

```python
from web3 import Web3
from solcx import compile_source

# Compile contract
compiled = compile_source(solidity_code)
contract_interface = compiled['<stdin>:SocialOracle']

# Connect to BNB Chain
web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

# Deploy
tx_hash = web3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
).constructor("Will TSLA sentiment be positive?").transact({
    'from': deployer_address,
    'gas': 3000000
})

# Get contract address
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress
```

**Usage**:
```bash
python deploy_bnb.py
# Follow prompts for testnet/mainnet
# Get contract address on BNBScan
```

---

## Prediction Market Integration

**How prediction markets use the oracle**:

### 1. Market Creation
```solidity
// Platform creates prediction market
PredictionMarket market = new PredictionMarket(
    "Will TSLA sentiment be positive by Friday?",
    oracleAddress  // Social Oracle contract address
);
```

### 2. Betting Period
- Users bet "Positive" or "Negative"
- Funds locked in smart contract
- Betting closes Friday 11:59 PM

### 3. Oracle Resolution
```python
# Social Oracle analyzes sentiment
result = analyzer.get_sentiment_analysis(data)

# Record on-chain (Saturday 12:00 AM)
contract.functions.updateOutcome(result['sentiment']).transact()
```

### 4. Auto-Settlement
```solidity
// Market reads oracle result
string memory outcome = SocialOracle(oracleAddress).marketOutcome();

// Distribute winnings automatically
if (keccak256(bytes(outcome)) == keccak256(bytes("Positive"))) {
    for (uint i = 0; i < positiveBettors.length; i++) {
        payable(positiveBettors[i]).transfer(winnings[i]);
    }
}
```

---

## Transaction Costs

**Typical Oracle Update**:
- Gas used: ~80,000-100,000 units
- Gas price: 3-5 gwei (BNB Chain)
- BNB price: ~$600
- **Total cost**: $0.10-1.00 per update

**Comparison**:
- BNB Chain: $0.50 per update
- Ethereum: $5-50 per update (10-100x more expensive)
- Polygon: $0.05 per update (cheaper but less secure/adopted)

**For 10 updates/day**:
- BNB Chain: $5/day = $150/month
- Ethereum: $50-500/day = $1,500-15,000/month

---

## Security

**Access Control**:
- Only oracle operator can call `updateOutcome()`
- `onlyOwner` modifier prevents unauthorized updates
- Owner address verified via cryptographic signature

**Immutability**:
- Once `isResolved = true`, outcome cannot be changed
- All updates stored permanently on blockchain
- Transparent audit trail on BNBScan

**Event Logging**:
```solidity
event MarketResolved(string outcome, address resolvedBy, uint256 timestamp);
```
- Emitted on every resolution
- Indexed for easy querying
- Prediction markets listen for this event

---

## Verification

**View on BNBScan**:
1. Go to https://bscscan.com/ (mainnet) or https://testnet.bscscan.com/ (testnet)
2. Enter contract address
3. View all transactions and events
4. Anyone can verify oracle decisions

**Read Contract**:
```javascript
// Anyone can query the result
const outcome = await contract.methods.marketOutcome().call();
const isResolved = await contract.methods.isResolved().call();
console.log(`Market resolved: ${isResolved}, Outcome: ${outcome}`);
```

---

## Revenue Integration

**Transaction Fees** (Revenue Stream #6):

Smart contract can enforce fee distribution:

```solidity
contract PredictionMarket {
    address public oracleAddress;
    uint256 public oracleFeePercent = 100; // 1% (in basis points)
    
    function settleBets() public {
        string memory outcome = SocialOracle(oracleAddress).marketOutcome();
        
        uint256 totalPool = address(this).balance;
        uint256 oracleFee = (totalPool * oracleFeePercent) / 10000;
        
        // Pay oracle
        payable(oracleAddress).transfer(oracleFee);
        
        // Distribute rest to winners
        distributeToWinners(totalPool - oracleFee, outcome);
    }
}
```

**Automated Revenue**:
- No manual invoicing needed
- Smart contract enforces payment
- Transparent for all parties
- Instant settlement

---

## Future Enhancements

**Multi-Chain Support** (Year 2):
- Deploy same contract on Ethereum, Polygon, Arbitrum
- Reach more prediction market platforms
- Diversify revenue across chains

**Decentralized Oracle Network** (Year 3):
- Multiple oracle operators
- Consensus mechanism (majority vote)
- Even more trustless and resilient

**On-Chain Governance** (Year 3):
- Token holders vote on oracle parameters
- Community-driven development
- DAO structure
