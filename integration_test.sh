#!/bin/bash

# Social Oracle Integration Test Script
# 
# This script provides complete workflow validation for the Social Oracle system.
# It includes environment configuration checks, dependency installation,
# unit test execution, and main application workflow validation with
# clear success/failure reporting and exit codes.
#
# Requirements: 4.3, 4.4, 4.5

set -e  # Exit on any error

# Color codes for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_LOG_FILE="integration_test_$(date +%Y%m%d_%H%M%S).log"
PYTHON_CMD="python"
PIP_CMD="pip"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print section headers
print_header() {
    local message=$1
    echo ""
    echo "=================================================================="
    print_status $BLUE "$message"
    echo "=================================================================="
}

# Function to log messages to both console and file
log_message() {
    local message=$1
    echo "$message" | tee -a "$TEST_LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_header "CHECKING PYTHON VERSION"
    
    if ! command_exists python && ! command_exists python3; then
        print_status $RED "❌ Python is not installed or not in PATH"
        return 1
    fi
    
    # Try python3 first, then python
    if command_exists python3; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command_exists python; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    fi
    
    local python_version=$($PYTHON_CMD --version 2>&1)
    log_message "✅ Found Python: $python_version"
    
    # Check if Python version is 3.8 or higher
    local version_check=$($PYTHON_CMD -c "import sys; print(sys.version_info >= (3, 8))" 2>/dev/null)
    if [ "$version_check" != "True" ]; then
        print_status $RED "❌ Python 3.8 or higher is required"
        return 1
    fi
    
    print_status $GREEN "✅ Python version check passed"
    return 0
}

# Function to check and install dependencies
check_dependencies() {
    print_header "CHECKING AND INSTALLING DEPENDENCIES"
    
    if [ ! -f "requirements.txt" ]; then
        print_status $RED "❌ requirements.txt not found"
        return 1
    fi
    
    log_message "📦 Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_message "🔧 Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_message "✅ Virtual environment activated (Unix/Linux)"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        log_message "✅ Virtual environment activated (Windows)"
    else
        print_status $YELLOW "⚠️  Virtual environment not found, using system Python"
    fi
    
    # Install dependencies
    $PIP_CMD install -r requirements.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Dependencies installed successfully"
    else
        print_status $RED "❌ Failed to install dependencies"
        return 1
    fi
    
    # Install test dependencies
    $PIP_CMD install pytest pytest-mock > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Test dependencies installed successfully"
    else
        print_status $RED "❌ Failed to install test dependencies"
        return 1
    fi
    
    return 0
}

# Function to validate environment configuration
validate_environment() {
    print_header "VALIDATING ENVIRONMENT CONFIGURATION"
    
    local required_vars=(
        "REDDIT_CLIENT_ID"
        "REDDIT_CLIENT_SECRET"
        "REDDIT_USER_AGENT"
        "GEMINI_API_KEY"
        "BNB_RPC_URL"
        "PRIVATE_KEY"
    )
    
    local missing_vars=()
    local env_file_exists=false
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        env_file_exists=true
        log_message "✅ Found .env file"
        # Source the .env file to load variables
        set -a  # Automatically export all variables
        source .env
        set +a  # Stop automatically exporting
    else
        log_message "⚠️  .env file not found, checking system environment variables"
    fi
    
    # Check each required variable
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        else
            log_message "✅ $var is set"
        fi
    done
    
    # Report missing variables
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_status $RED "❌ Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            print_status $RED "   - $var"
        done
        
        if [ "$env_file_exists" = false ]; then
            print_status $YELLOW "💡 Create a .env file based on .env.example"
        fi
        
        return 1
    fi
    
    print_status $GREEN "✅ All required environment variables are set"
    return 0
}

# Function to run unit tests
run_unit_tests() {
    print_header "RUNNING UNIT TESTS"
    
    local test_files=(
        "tests/test_social_fetcher.py"
        "tests/test_ai_analyzer.py"
        "tests/test_blockchain_connector.py"
        "tests/test_main_integration.py"
        "test_oracle_logic.py"
    )
    
    local failed_tests=()
    local total_tests=0
    local passed_tests=0
    
    for test_file in "${test_files[@]}"; do
        if [ -f "$test_file" ]; then
            log_message "🧪 Running tests in $test_file..."
            
            # Run pytest with verbose output and capture results
            if $PYTHON_CMD -m pytest "$test_file" -v --tb=short >> "$TEST_LOG_FILE" 2>&1; then
                print_status $GREEN "✅ $test_file - PASSED"
                ((passed_tests++))
            else
                print_status $RED "❌ $test_file - FAILED"
                failed_tests+=("$test_file")
            fi
            ((total_tests++))
        else
            print_status $YELLOW "⚠️  Test file not found: $test_file"
        fi
    done
    
    # Summary
    log_message ""
    log_message "Unit Test Summary:"
    log_message "  Total test files: $total_tests"
    log_message "  Passed: $passed_tests"
    log_message "  Failed: ${#failed_tests[@]}"
    
    if [ ${#failed_tests[@]} -gt 0 ]; then
        print_status $RED "❌ Some unit tests failed:"
        for test in "${failed_tests[@]}"; do
            print_status $RED "   - $test"
        done
        return 1
    fi
    
    print_status $GREEN "✅ All unit tests passed"
    return 0
}

# Function to validate project structure
validate_project_structure() {
    print_header "VALIDATING PROJECT STRUCTURE"
    
    local required_files=(
        "main.py"
        "requirements.txt"
        "src/config.py"
        "src/social_fetcher.py"
        "src/ai_analyzer.py"
        "src/blockchain_connector.py"
        "contracts/SocialOracle.sol"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_message "✅ $file exists"
        else
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_status $RED "❌ Missing required files:"
        for file in "${missing_files[@]}"; do
            print_status $RED "   - $file"
        done
        return 1
    fi
    
    print_status $GREEN "✅ All required project files are present"
    return 0
}

# Function to test configuration loading
test_configuration_loading() {
    print_header "TESTING CONFIGURATION LOADING"
    
    log_message "🔧 Testing configuration validation..."
    
    # Test configuration loading with Python
    local config_test_result=$($PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')
try:
    from config import Config
    config = Config.get_api_config()
    print('SUCCESS: Configuration loaded successfully')
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
" 2>&1)
    
    if echo "$config_test_result" | grep -q "SUCCESS"; then
        print_status $GREEN "✅ Configuration loading test passed"
        log_message "$config_test_result"
        return 0
    else
        print_status $RED "❌ Configuration loading test failed"
        log_message "$config_test_result"
        return 1
    fi
}

# Function to test component imports
test_component_imports() {
    print_header "TESTING COMPONENT IMPORTS"
    
    local components=(
        "src.config:Config"
        "src.social_fetcher:SocialMediaFetcher"
        "src.ai_analyzer:AIAnalyzer"
        "src.blockchain_connector:BlockchainConnector"
    )
    
    for component in "${components[@]}"; do
        local module="${component%:*}"
        local class="${component#*:}"
        
        log_message "🔍 Testing import: $module.$class"
        
        local import_result=$($PYTHON_CMD -c "
try:
    from $module import $class
    print('SUCCESS: $class imported successfully')
except Exception as e:
    print(f'ERROR: Failed to import $class - {str(e)}')
    exit(1)
" 2>&1)
        
        if echo "$import_result" | grep -q "SUCCESS"; then
            print_status $GREEN "✅ $class import successful"
        else
            print_status $RED "❌ $class import failed"
            log_message "$import_result"
            return 1
        fi
    done
    
    print_status $GREEN "✅ All component imports successful"
    return 0
}

# Function to run main application workflow validation
validate_main_workflow() {
    print_header "VALIDATING MAIN APPLICATION WORKFLOW"
    
    log_message "🚀 Testing main application initialization..."
    
    # Test main.py can be imported and initialized without errors
    local main_test_result=$($PYTHON_CMD -c "
import sys
import os
sys.path.insert(0, '.')

# Mock environment for testing
os.environ.setdefault('REDDIT_CLIENT_ID', 'test_client_id')
os.environ.setdefault('REDDIT_CLIENT_SECRET', 'test_client_secret')
os.environ.setdefault('REDDIT_USER_AGENT', 'test_user_agent')
os.environ.setdefault('GEMINI_API_KEY', 'test_gemini_key')
os.environ.setdefault('BNB_RPC_URL', 'https://test-rpc.binance.org:8545/')
os.environ.setdefault('PRIVATE_KEY', '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')

try:
    # Test orchestrator initialization
    from main import SocialOracleOrchestrator
    orchestrator = SocialOracleOrchestrator()
    print('SUCCESS: Main orchestrator initialized successfully')
    
    # Test configuration loading logic
    from src.config import Config
    if Config.validate_environment():
        print('SUCCESS: Environment validation passed')
    else:
        print('WARNING: Environment validation failed with test data')
    
except Exception as e:
    print(f'ERROR: Main workflow validation failed - {str(e)}')
    import traceback
    traceback.print_exc()
    exit(1)
" 2>&1)
    
    if echo "$main_test_result" | grep -q "SUCCESS.*Main orchestrator initialized"; then
        print_status $GREEN "✅ Main application workflow validation passed"
        log_message "$main_test_result"
        return 0
    else
        print_status $RED "❌ Main application workflow validation failed"
        log_message "$main_test_result"
        return 1
    fi
}

# Function to generate test report
generate_test_report() {
    print_header "GENERATING TEST REPORT"
    
    local report_file="integration_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
Social Oracle Integration Test Report
Generated: $(date)
Log File: $TEST_LOG_FILE

Test Results Summary:
- Python Version Check: $python_check_status
- Dependency Installation: $dependency_check_status
- Environment Validation: $env_validation_status
- Project Structure: $structure_validation_status
- Configuration Loading: $config_test_status
- Component Imports: $import_test_status
- Unit Tests: $unit_test_status
- Main Workflow Validation: $workflow_validation_status

Overall Status: $overall_status

For detailed logs, see: $TEST_LOG_FILE
EOF
    
    log_message "📄 Test report generated: $report_file"
    
    if [ "$overall_status" = "PASSED" ]; then
        print_status $GREEN "✅ Integration test report: $report_file"
    else
        print_status $RED "❌ Integration test report: $report_file"
    fi
}

# Function to cleanup test artifacts
cleanup_test_artifacts() {
    print_header "CLEANING UP TEST ARTIFACTS"
    
    # Remove temporary files created during testing
    if [ -d "__pycache__" ]; then
        rm -rf __pycache__
        log_message "🧹 Removed __pycache__ directory"
    fi
    
    if [ -d "src/__pycache__" ]; then
        rm -rf src/__pycache__
        log_message "🧹 Removed src/__pycache__ directory"
    fi
    
    if [ -d "tests/__pycache__" ]; then
        rm -rf tests/__pycache__
        log_message "🧹 Removed tests/__pycache__ directory"
    fi
    
    # Remove pytest cache
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        log_message "🧹 Removed .pytest_cache directory"
    fi
    
    print_status $GREEN "✅ Cleanup completed"
}

# Main execution function
main() {
    print_status $BLUE "🔮 Social Oracle Integration Test Suite"
    print_status $BLUE "======================================"
    log_message "Integration test started at: $(date)"
    log_message "Test log file: $TEST_LOG_FILE"
    
    # Initialize status variables
    python_check_status="FAILED"
    dependency_check_status="FAILED"
    env_validation_status="FAILED"
    structure_validation_status="FAILED"
    config_test_status="FAILED"
    import_test_status="FAILED"
    unit_test_status="FAILED"
    workflow_validation_status="FAILED"
    overall_status="FAILED"
    
    # Run all test phases
    if check_python_version; then
        python_check_status="PASSED"
        
        if validate_project_structure; then
            structure_validation_status="PASSED"
            
            if check_dependencies; then
                dependency_check_status="PASSED"
                
                if validate_environment; then
                    env_validation_status="PASSED"
                    
                    if test_configuration_loading; then
                        config_test_status="PASSED"
                        
                        if test_component_imports; then
                            import_test_status="PASSED"
                            
                            if run_unit_tests; then
                                unit_test_status="PASSED"
                                
                                if validate_main_workflow; then
                                    workflow_validation_status="PASSED"
                                    overall_status="PASSED"
                                fi
                            fi
                        fi
                    fi
                fi
            fi
        fi
    fi
    
    # Generate final report
    generate_test_report
    
    # Final status
    print_header "INTEGRATION TEST RESULTS"
    
    if [ "$overall_status" = "PASSED" ]; then
        print_status $GREEN "🎉 ALL INTEGRATION TESTS PASSED!"
        print_status $GREEN "✅ Social Oracle system is ready for deployment"
        cleanup_test_artifacts
        exit 0
    else
        print_status $RED "❌ INTEGRATION TESTS FAILED"
        print_status $RED "🔍 Check the test log for detailed error information: $TEST_LOG_FILE"
        print_status $YELLOW "💡 Fix the failing components and run the tests again"
        exit 1
    fi
}

# Trap to ensure cleanup on script exit
trap cleanup_test_artifacts EXIT

# Run main function
main "$@"