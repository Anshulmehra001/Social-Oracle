// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SocialOracle
 * @dev Smart contract for storing prediction market outcomes based on social media sentiment analysis
 */
contract SocialOracle {
    // State variables
    address public owner;
    string public marketQuestion;
    string public marketOutcome;
    bool public isResolved;
    
    // Events
    event MarketResolved(string outcome, address resolvedBy);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier notResolved() {
        require(!isResolved, "Market has already been resolved");
        _;
    }
    
    /**
     * @dev Constructor to initialize the market question and set the owner
     * @param _marketQuestion The prediction market question to be resolved
     */
    constructor(string memory _marketQuestion) {
        require(bytes(_marketQuestion).length > 0, "Market question cannot be empty");
        owner = msg.sender;
        marketQuestion = _marketQuestion;
        isResolved = false;
    }
    
    /**
     * @dev Update the market outcome (can only be called once by owner)
     * @param _newOutcome The sentiment outcome: "Positive", "Negative", or "Neutral"
     */
    function updateOutcome(string memory _newOutcome) public onlyOwner notResolved {
        require(bytes(_newOutcome).length > 0, "Outcome cannot be empty");
        require(
            keccak256(abi.encodePacked(_newOutcome)) == keccak256(abi.encodePacked("Positive")) ||
            keccak256(abi.encodePacked(_newOutcome)) == keccak256(abi.encodePacked("Negative")) ||
            keccak256(abi.encodePacked(_newOutcome)) == keccak256(abi.encodePacked("Neutral")),
            "Outcome must be 'Positive', 'Negative', or 'Neutral'"
        );
        
        marketOutcome = _newOutcome;
        isResolved = true;
        
        emit MarketResolved(_newOutcome, msg.sender);
    }
    
    /**
     * @dev Get the current market status
     * @return question The market question
     * @return outcome The resolved outcome (empty if not resolved)
     * @return resolved Whether the market has been resolved
     */
    function getMarketStatus() public view returns (string memory question, string memory outcome, bool resolved) {
        return (marketQuestion, marketOutcome, isResolved);
    }
}