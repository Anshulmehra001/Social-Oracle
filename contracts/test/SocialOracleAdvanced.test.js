// Advanced JavaScript tests for SocialOracle contract
// This file would be used with Hardhat or Truffle testing framework

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SocialOracle", function () {
    let SocialOracle;
    let socialOracle;
    let owner;
    let nonOwner;
    const testQuestion = "Will Bitcoin reach $100,000 by end of 2024?";

    beforeEach(async function () {
        // Get signers
        [owner, nonOwner] = await ethers.getSigners();
        
        // Deploy contract
        SocialOracle = await ethers.getContractFactory("SocialOracle");
        socialOracle = await SocialOracle.deploy(testQuestion);
        await socialOracle.deployed();
    });

    describe("Deployment", function () {
        it("Should set the right owner", async function () {
            expect(await socialOracle.owner()).to.equal(owner.address);
        });

        it("Should set the market question", async function () {
            expect(await socialOracle.marketQuestion()).to.equal(testQuestion);
        });

        it("Should initialize as unresolved", async function () {
            expect(await socialOracle.isResolved()).to.equal(false);
        });

        it("Should have empty initial outcome", async function () {
            expect(await socialOracle.marketOutcome()).to.equal("");
        });

        it("Should revert with empty market question", async function () {
            await expect(SocialOracle.deploy("")).to.be.revertedWith("Market question cannot be empty");
        });
    });

    describe("Owner Permissions", function () {
        it("Should allow owner to update outcome", async function () {
            await socialOracle.updateOutcome("Positive");
            expect(await socialOracle.marketOutcome()).to.equal("Positive");
            expect(await socialOracle.isResolved()).to.equal(true);
        });

        it("Should not allow non-owner to update outcome", async function () {
            await expect(
                socialOracle.connect(nonOwner).updateOutcome("Positive")
            ).to.be.revertedWith("Only owner can call this function");
        });
    });

    describe("Single Resolution Enforcement", function () {
        it("Should not allow updating outcome twice", async function () {
            await socialOracle.updateOutcome("Positive");
            await expect(
                socialOracle.updateOutcome("Negative")
            ).to.be.revertedWith("Market has already been resolved");
        });
    });

    describe("Input Validation", function () {
        it("Should accept valid outcomes", async function () {
            // Test Positive
            await socialOracle.updateOutcome("Positive");
            expect(await socialOracle.marketOutcome()).to.equal("Positive");
            
            // Deploy new contract for next test
            const newOracle1 = await SocialOracle.deploy(testQuestion);
            await newOracle1.updateOutcome("Negative");
            expect(await newOracle1.marketOutcome()).to.equal("Negative");
            
            // Deploy new contract for next test
            const newOracle2 = await SocialOracle.deploy(testQuestion);
            await newOracle2.updateOutcome("Neutral");
            expect(await newOracle2.marketOutcome()).to.equal("Neutral");
        });

        it("Should reject invalid outcomes", async function () {
            await expect(
                socialOracle.updateOutcome("Invalid")
            ).to.be.revertedWith("Outcome must be 'Positive', 'Negative', or 'Neutral'");
            
            await expect(
                socialOracle.updateOutcome("positive")
            ).to.be.revertedWith("Outcome must be 'Positive', 'Negative', or 'Neutral'");
            
            await expect(
                socialOracle.updateOutcome("")
            ).to.be.revertedWith("Outcome cannot be empty");
        });
    });

    describe("State Transitions", function () {
        it("Should transition from unresolved to resolved", async function () {
            expect(await socialOracle.isResolved()).to.equal(false);
            expect(await socialOracle.marketOutcome()).to.equal("");
            
            await socialOracle.updateOutcome("Positive");
            
            expect(await socialOracle.isResolved()).to.equal(true);
            expect(await socialOracle.marketOutcome()).to.equal("Positive");
        });

        it("Should emit MarketResolved event", async function () {
            await expect(socialOracle.updateOutcome("Positive"))
                .to.emit(socialOracle, "MarketResolved")
                .withArgs("Positive", owner.address);
        });
    });

    describe("getMarketStatus Function", function () {
        it("Should return correct initial status", async function () {
            const [question, outcome, resolved] = await socialOracle.getMarketStatus();
            expect(question).to.equal(testQuestion);
            expect(outcome).to.equal("");
            expect(resolved).to.equal(false);
        });

        it("Should return correct status after resolution", async function () {
            await socialOracle.updateOutcome("Negative");
            const [question, outcome, resolved] = await socialOracle.getMarketStatus();
            expect(question).to.equal(testQuestion);
            expect(outcome).to.equal("Negative");
            expect(resolved).to.equal(true);
        });
    });
});