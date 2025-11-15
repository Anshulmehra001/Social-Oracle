#!/usr/bin/env python3
"""
Social Oracle Main Orchestrator

This script coordinates the complete workflow of the Social Oracle system:
1. Load environment variables and configuration
2. Fetch social media data from Reddit
3. Analyze sentiment using Google Gemini AI
4. Deploy smart contract and record outcome on BNB Smart Chain Testnet
5. Provide comprehensive logging and verification links

Requirements: 1.1, 2.1, 3.1, 3.5, 5.4, 5.5
"""

import sys
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import asdict

from src.config import Config, MarketConfig, APIConfig
from src.social_fetcher import SocialMediaFetcher
from src.ai_analyzer import AIAnalyzer
from src.blockchain_connector import BlockchainConnector


class SocialOracleOrchestrator:
    """Main orchestrator for the Social Oracle workflow."""
    
    def __init__(self, simulation_mode: bool = False):
        """Initialize the orchestrator with logging and configuration.
        
        Args:
            simulation_mode: If True, uses simulated data instead of real APIs
        """
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.simulation_mode = simulation_mode
        
        # Initialize components
        self.api_config: Optional[APIConfig] = None
        self.social_fetcher: Optional[SocialMediaFetcher] = None
        self.ai_analyzer: Optional[AIAnalyzer] = None
        self.blockchain_connector: Optional[BlockchainConnector] = None
        
        if simulation_mode:
            self.logger.info("Social Oracle Orchestrator initialized in SIMULATION MODE")
            self.logger.warning("⚠️  SIMULATION MODE: Using mock data instead of real APIs")
        else:
            self.logger.info("Social Oracle Orchestrator initialized")
    
    def setup_logging(self) -> None:
        """Configure comprehensive logging for the workflow."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f'social_oracle_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
    
    def load_configuration(self) -> bool:
        """
        Load and validate environment variables and configuration.
        
        Returns:
            bool: True if configuration loaded successfully, False otherwise
        """
        self.logger.info("Loading configuration and validating environment variables...")
        
        try:
            # Validate environment variables
            if not Config.validate_environment():
                self.logger.error("Environment validation failed")
                return False
            
            # Load API configuration
            self.api_config = Config.get_api_config()
            self.logger.info("API configuration loaded successfully")
            
            # Initialize components
            self.social_fetcher = SocialMediaFetcher(self.api_config)
            self.ai_analyzer = AIAnalyzer(self.api_config.gemini_api_key)
            self.blockchain_connector = BlockchainConnector(
                self.api_config.bnb_rpc_url,
                self.api_config.private_key
            )
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration loading failed: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def fetch_social_data(self, market_config: MarketConfig) -> Optional[str]:
        """
        Fetch social media data for sentiment analysis.
        
        Args:
            market_config: Market configuration with search parameters
            
        Returns:
            Optional[str]: Concatenated social media text or None if failed
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 1: FETCHING SOCIAL MEDIA DATA")
        self.logger.info("=" * 60)
        
        if self.simulation_mode:
            return self._simulate_social_data(market_config)
        
        try:
            self.logger.info(f"Market Question: {market_config.question}")
            self.logger.info(f"Search Keywords: {market_config.search_keywords}")
            self.logger.info(f"Target Subreddit: r/{market_config.reddit_subreddit}")
            self.logger.info(f"Post Limit: {market_config.post_limit}")
            
            social_data = self.social_fetcher.fetch_reddit_sentiment_data(
                keywords=market_config.search_keywords,
                subreddit=market_config.reddit_subreddit,
                limit=market_config.post_limit
            )
            
            if not social_data:
                self.logger.warning("No social media data retrieved")
                return None
            
            self.logger.info(f"Successfully fetched {len(social_data)} characters of social media data")
            self.logger.info("Social media data fetching completed successfully")
            
            return social_data
            
        except Exception as e:
            self.logger.error(f"Social media data fetching failed: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def analyze_sentiment(self, social_data: str, market_question: str) -> Optional[str]:
        """
        Analyze sentiment of social media data using AI.
        
        Args:
            social_data: Concatenated social media text
            market_question: The prediction market question
            
        Returns:
            Optional[str]: Sentiment outcome or None if failed
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: AI SENTIMENT ANALYSIS")
        self.logger.info("=" * 60)
        
        if self.simulation_mode:
            return self._simulate_sentiment_analysis(social_data, market_question)
        
        try:
            self.logger.info(f"Analyzing sentiment for: {market_question}")
            self.logger.info(f"Processing {len(social_data)} characters of text data")
            
            sentiment_outcome = self.ai_analyzer.get_sentiment_analysis(
                text_data=social_data,
                market_question=market_question
            )
            
            self.logger.info(f"AI Analysis Result: {sentiment_outcome}")
            self.logger.info("Sentiment analysis completed successfully")
            
            return sentiment_outcome
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def deploy_and_record_outcome(self, market_question: str, sentiment_outcome: str) -> Optional[Dict[str, Any]]:
        """
        Deploy smart contract and record the sentiment outcome.
        
        Args:
            market_question: The prediction market question
            sentiment_outcome: The determined sentiment outcome
            
        Returns:
            Optional[Dict[str, Any]]: Transaction details or None if failed
        """
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: BLOCKCHAIN DEPLOYMENT AND RECORDING")
        self.logger.info("=" * 60)
        
        if self.simulation_mode:
            return self._simulate_blockchain_operations(market_question, sentiment_outcome)
        
        try:
            # Deploy smart contract
            self.logger.info("Deploying SocialOracle smart contract...")
            self.logger.info(f"Market Question: {market_question}")
            
            contract_source_path = "contracts/SocialOracle.sol"
            deployment_tx = self.blockchain_connector.deploy_contract(
                contract_source_path=contract_source_path,
                market_question=market_question
            )
            
            self.logger.info(f"Contract deployed successfully!")
            self.logger.info(f"Contract Address: {deployment_tx.contract_address}")
            self.logger.info(f"Deployment Transaction: {deployment_tx.transaction_hash}")
            self.logger.info(f"Block Number: {deployment_tx.block_number}")
            self.logger.info(f"Gas Used: {deployment_tx.gas_used}")
            
            # Get contract ABI for interaction
            contract_abi = self.blockchain_connector.get_contract_abi(contract_source_path)
            
            # Record sentiment outcome
            self.logger.info(f"Recording sentiment outcome: {sentiment_outcome}")
            
            outcome_tx = self.blockchain_connector.record_outcome(
                contract_address=deployment_tx.contract_address,
                contract_abi=contract_abi,
                outcome=sentiment_outcome
            )
            
            self.logger.info(f"Outcome recorded successfully!")
            self.logger.info(f"Outcome Transaction: {outcome_tx.transaction_hash}")
            self.logger.info(f"Block Number: {outcome_tx.block_number}")
            self.logger.info(f"Gas Used: {outcome_tx.gas_used}")
            
            # Verify contract status
            contract_status = self.blockchain_connector.verify_contract_status(
                contract_address=deployment_tx.contract_address,
                contract_abi=contract_abi
            )
            
            self.logger.info("Contract verification completed:")
            self.logger.info(f"  Market Question: {contract_status['market_question']}")
            self.logger.info(f"  Market Outcome: {contract_status['market_outcome']}")
            self.logger.info(f"  Is Resolved: {contract_status['is_resolved']}")
            self.logger.info(f"  Owner: {contract_status['owner']}")
            
            return {
                'deployment_transaction': asdict(deployment_tx),
                'outcome_transaction': asdict(outcome_tx),
                'contract_status': contract_status,
                'explorer_urls': {
                    'deployment': self.blockchain_connector.get_block_explorer_url(deployment_tx.transaction_hash),
                    'outcome': self.blockchain_connector.get_block_explorer_url(outcome_tx.transaction_hash)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Blockchain operations failed: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def run_complete_workflow(self, market_config: MarketConfig) -> bool:
        """
        Execute the complete Social Oracle workflow.
        
        Args:
            market_config: Configuration for the prediction market
            
        Returns:
            bool: True if workflow completed successfully, False otherwise
        """
        self.logger.info("🚀 STARTING SOCIAL ORACLE WORKFLOW")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch social media data
            social_data = self.fetch_social_data(market_config)
            if not social_data:
                self.logger.error("Workflow failed: Unable to fetch social media data")
                return False
            
            # Step 2: Analyze sentiment
            sentiment_outcome = self.analyze_sentiment(social_data, market_config.question)
            if not sentiment_outcome:
                self.logger.error("Workflow failed: Unable to analyze sentiment")
                return False
            
            # Step 3: Deploy contract and record outcome
            blockchain_result = self.deploy_and_record_outcome(market_config.question, sentiment_outcome)
            if not blockchain_result:
                self.logger.error("Workflow failed: Unable to deploy contract or record outcome")
                return False
            
            # Workflow completed successfully
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.logger.info("=" * 80)
            self.logger.info("🎉 SOCIAL ORACLE WORKFLOW COMPLETED SUCCESSFULLY!")
            self.logger.info("=" * 80)
            
            self.logger.info("FINAL RESULTS:")
            self.logger.info(f"  Market Question: {market_config.question}")
            self.logger.info(f"  Sentiment Outcome: {sentiment_outcome}")
            self.logger.info(f"  Contract Address: {blockchain_result['deployment_transaction']['contract_address']}")
            self.logger.info(f"  Total Execution Time: {duration.total_seconds():.2f} seconds")
            
            self.logger.info("\nVERIFICATION LINKS:")
            self.logger.info(f"  Deployment Transaction: {blockchain_result['explorer_urls']['deployment']}")
            self.logger.info(f"  Outcome Transaction: {blockchain_result['explorer_urls']['outcome']}")
            
            self.logger.info("\nWorkflow completed successfully! ✅")
            return True
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _simulate_social_data(self, market_config: MarketConfig) -> str:
        """Simulate social media data fetching."""
        import time
        import random
        
        self.logger.warning("🔄 SIMULATION: Generating mock social media data")
        self.logger.info(f"Market Question: {market_config.question}")
        self.logger.info(f"Search Keywords: {market_config.search_keywords}")
        self.logger.info(f"Target Subreddit: r/{market_config.reddit_subreddit}")
        self.logger.info(f"Post Limit: {market_config.post_limit}")
        
        # Simulate API delay
        time.sleep(0.5)
        
        # Generate realistic mock data based on the question
        question_lower = market_config.question.lower()
        keywords_lower = market_config.search_keywords.lower()
        
        # Determine sentiment bias based on keywords
        positive_keywords = ['success', 'good', 'positive', 'up', 'rise', 'bull', 'growth']
        negative_keywords = ['fail', 'bad', 'negative', 'down', 'fall', 'bear', 'crash']
        
        sentiment_bias = 0  # neutral
        for word in positive_keywords:
            if word in keywords_lower or word in question_lower:
                sentiment_bias += 1
        for word in negative_keywords:
            if word in keywords_lower or word in question_lower:
                sentiment_bias -= 1
        
        # Generate mock posts and comments
        mock_posts = []
        
        if sentiment_bias > 0:
            # Positive bias
            mock_posts = [
                "Title: Great news about the upcoming developments\nContent: The community is really excited about the positive changes coming. This looks very promising!\nComment: I'm bullish on this\nComment: Definitely positive outlook\nComment: This is exactly what we needed",
                "Title: Strong community support\nContent: Seeing a lot of positive sentiment in the community discussions\nComment: Very optimistic about this\nComment: The fundamentals look strong\nComment: Positive momentum building",
                "Title: Excellent progress update\nContent: The recent developments show great promise for the future\nComment: This is fantastic news\nComment: Really positive direction\nComment: Community is very supportive"
            ]
        elif sentiment_bias < 0:
            # Negative bias
            mock_posts = [
                "Title: Concerns about recent developments\nContent: There are some worrying signs that the community is discussing\nComment: Not looking good\nComment: I'm concerned about this direction\nComment: This doesn't seem right",
                "Title: Community expressing doubts\nContent: Many users are questioning the recent decisions and changes\nComment: Very skeptical about this\nComment: Not confident in this approach\nComment: This seems problematic",
                "Title: Negative feedback from users\nContent: The community response has been largely negative\nComment: This is disappointing\nComment: Not what we expected\nComment: Concerning developments"
            ]
        else:
            # Neutral/mixed
            mock_posts = [
                "Title: Mixed reactions to recent news\nContent: The community has varied opinions on the latest developments\nComment: Cautiously optimistic\nComment: Need to wait and see\nComment: Mixed feelings about this",
                "Title: Community discussion ongoing\nContent: People are still debating the implications of recent changes\nComment: Interesting perspective\nComment: Time will tell\nComment: Neutral on this for now",
                "Title: Balanced analysis of situation\nContent: There are both positive and negative aspects to consider\nComment: Fair assessment\nComment: Reasonable approach\nComment: Balanced viewpoint"
            ]
        
        # Select random posts based on post limit
        selected_posts = random.sample(mock_posts, min(len(mock_posts), market_config.post_limit))
        social_data = "\n\n".join(selected_posts)
        
        self.logger.info(f"🔄 SIMULATION: Generated {len(social_data)} characters of mock social media data")
        self.logger.warning("⚠️  This is simulated data, not real social media content")
        
        return social_data
    
    def _simulate_sentiment_analysis(self, social_data: str, market_question: str) -> str:
        """Simulate AI sentiment analysis."""
        import time
        import random
        
        self.logger.warning("🔄 SIMULATION: Performing mock AI sentiment analysis")
        self.logger.info(f"Analyzing sentiment for: {market_question}")
        self.logger.info(f"Processing {len(social_data)} characters of text data")
        
        # Simulate AI processing delay
        time.sleep(0.3)
        
        # Analyze the mock data to determine sentiment
        positive_words = ['great', 'excellent', 'positive', 'bullish', 'optimistic', 'fantastic', 'strong', 'promising', 'excited', 'supportive']
        negative_words = ['concerns', 'worrying', 'doubts', 'skeptical', 'negative', 'disappointing', 'problematic', 'concerning']
        neutral_words = ['mixed', 'neutral', 'balanced', 'cautious', 'wait', 'time will tell']
        
        social_data_lower = social_data.lower()
        
        positive_count = sum(1 for word in positive_words if word in social_data_lower)
        negative_count = sum(1 for word in negative_words if word in social_data_lower)
        neutral_count = sum(1 for word in neutral_words if word in social_data_lower)
        
        # Determine sentiment based on word counts
        if positive_count > negative_count and positive_count > neutral_count:
            sentiment = "Positive"
        elif negative_count > positive_count and negative_count > neutral_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        # Add some randomness for realism
        if random.random() < 0.1:  # 10% chance to flip to neutral
            sentiment = "Neutral"
        
        self.logger.info(f"🔄 SIMULATION: AI Analysis Result: {sentiment}")
        self.logger.warning("⚠️  This is simulated AI analysis, not real Google Gemini output")
        
        return sentiment
    
    def _simulate_blockchain_operations(self, market_question: str, sentiment_outcome: str) -> Dict[str, Any]:
        """Simulate blockchain deployment and recording."""
        import time
        import random
        from datetime import datetime
        
        self.logger.warning("🔄 SIMULATION: Performing mock blockchain operations")
        self.logger.info("Deploying SocialOracle smart contract...")
        self.logger.info(f"Market Question: {market_question}")
        
        # Simulate deployment delay
        time.sleep(0.8)
        
        # Generate mock transaction data
        mock_contract_address = f"0x{''.join(random.choices('0123456789abcdef', k=40))}"
        mock_deployment_hash = f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
        mock_outcome_hash = f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
        mock_block_number = random.randint(15000000, 16000000)
        
        self.logger.info(f"🔄 SIMULATION: Contract deployed successfully!")
        self.logger.info(f"Contract Address: {mock_contract_address}")
        self.logger.info(f"Deployment Transaction: {mock_deployment_hash}")
        self.logger.info(f"Block Number: {mock_block_number}")
        self.logger.info(f"Gas Used: 1500000")
        
        # Simulate outcome recording
        self.logger.info(f"Recording sentiment outcome: {sentiment_outcome}")
        time.sleep(0.3)
        
        self.logger.info(f"🔄 SIMULATION: Outcome recorded successfully!")
        self.logger.info(f"Outcome Transaction: {mock_outcome_hash}")
        self.logger.info(f"Block Number: {mock_block_number + 1}")
        self.logger.info(f"Gas Used: 150000")
        
        # Mock contract verification
        self.logger.info("Contract verification completed:")
        self.logger.info(f"  Market Question: {market_question}")
        self.logger.info(f"  Market Outcome: {sentiment_outcome}")
        self.logger.info(f"  Is Resolved: True")
        self.logger.info(f"  Owner: {mock_contract_address}")
        
        self.logger.warning("⚠️  This is simulated blockchain data, not real BNB Smart Chain transactions")
        
        return {
            'deployment_transaction': {
                'contract_address': mock_contract_address,
                'transaction_hash': mock_deployment_hash,
                'block_number': mock_block_number,
                'gas_used': 1500000,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            },
            'outcome_transaction': {
                'contract_address': mock_contract_address,
                'transaction_hash': mock_outcome_hash,
                'block_number': mock_block_number + 1,
                'gas_used': 150000,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            },
            'contract_status': {
                'market_question': market_question,
                'market_outcome': sentiment_outcome,
                'is_resolved': True,
                'owner': mock_contract_address
            },
            'explorer_urls': {
                'deployment': f"https://testnet.bscscan.com/tx/{mock_deployment_hash}",
                'outcome': f"https://testnet.bscscan.com/tx/{mock_outcome_hash}"
            }
        }


def main():
    """Main entry point for the Social Oracle system."""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Social Oracle - Decentralized Prediction Market Resolution System")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode (no real API calls)")
    parser.add_argument("--question", type=str, help="Custom market question")
    parser.add_argument("--keywords", type=str, help="Custom search keywords")
    parser.add_argument("--subreddit", type=str, help="Custom subreddit")
    parser.add_argument("--limit", type=int, default=30, help="Post limit (default: 30)")
    
    args = parser.parse_args()
    
    print("Social Oracle - Decentralized Prediction Market Resolution System")
    print("=" * 80)
    
    if args.simulate:
        print("SIMULATION MODE: Using mock data instead of real APIs")
        print("This mode demonstrates the workflow without requiring API keys")
        print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = SocialOracleOrchestrator(simulation_mode=args.simulate)
    
    # Load configuration (skip for simulation mode)
    if not args.simulate:
        if not orchestrator.load_configuration():
            print("Configuration loading failed. Trying simulation mode...")
            print("Run with --simulate flag to use mock data")
            
            # Ask user if they want to continue in simulation mode
            try:
                response = input("\nWould you like to run in simulation mode instead? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    print("\nSwitching to simulation mode...")
                    orchestrator = SocialOracleOrchestrator(simulation_mode=True)
                else:
                    print("Please configure your API keys in .env file and try again.")
                    print("Refer to .env.example for required configuration.")
                    sys.exit(1)
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(1)
    
    # Create market configuration
    try:
        if args.question and args.keywords and args.subreddit:
            # Use custom configuration
            market_config = Config.create_market_config(
                question=args.question,
                keywords=args.keywords,
                subreddit=args.subreddit,
                post_limit=args.limit
            )
        else:
            # Use default configuration
            market_config = Config.create_market_config(
                question="Will Bitcoin price be above $50,000 by the end of this month?",
                keywords="Bitcoin price prediction $50000",
                subreddit="CryptoCurrency",
                post_limit=args.limit
            )
        
        print(f"Market Question: {market_config.question}")
        print(f"Search Keywords: {market_config.search_keywords}")
        print(f"Target Subreddit: r/{market_config.reddit_subreddit}")
        print(f"Post Limit: {market_config.post_limit}")
        print("=" * 80)
        
        # Run the complete workflow
        success = orchestrator.run_complete_workflow(market_config)
        
        if success:
            if args.simulate:
                print("\nSIMULATION COMPLETED: Mock workflow executed successfully!")
                print("To run with real APIs, configure your .env file and run without --simulate")
            else:
                print("\nSocial Oracle workflow completed successfully!")
            sys.exit(0)
        else:
            print("\nSocial Oracle workflow failed. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()