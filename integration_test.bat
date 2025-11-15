@echo off
REM Social Oracle Integration Test Script (Windows)
REM 
REM This script provides complete workflow validation for the Social Oracle system.
REM It includes environment configuration checks, dependency installation,
REM unit test execution, and main application workflow validation with
REM clear success/failure reporting and exit codes.
REM
REM Requirements: 4.3, 4.4, 4.5

setlocal enabledelayedexpansion

REM Test configuration
set "TEST_LOG_FILE=integration_test_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
set "PYTHON_CMD=python"
set "PIP_CMD=pip"
set "OVERALL_STATUS=FAILED"

REM Clean up log file name (remove spaces)
set "TEST_LOG_FILE=%TEST_LOG_FILE: =0%"

echo Social Oracle Integration Test Suite > "%TEST_LOG_FILE%"
echo ====================================== >> "%TEST_LOG_FILE%"
echo Integration test started at: %date% %time% >> "%TEST_LOG_FILE%"
echo Test log file: %TEST_LOG_FILE% >> "%TEST_LOG_FILE%"

REM Function to print colored output (Windows doesn't support colors easily, so we'll use plain text)
echo.
echo ==================================================================
echo SOCIAL ORACLE INTEGRATION TEST SUITE
echo ==================================================================

REM Check Python version
echo.
echo ==================================================================
echo CHECKING PYTHON VERSION
echo ==================================================================

python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo ERROR: Python is not installed or not in PATH >> "%TEST_LOG_FILE%"
        goto :failure
    ) else (
        set "PYTHON_CMD=python3"
        set "PIP_CMD=pip3"
    )
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo SUCCESS: Found Python: %PYTHON_VERSION%
echo SUCCESS: Found Python: %PYTHON_VERSION% >> "%TEST_LOG_FILE%"

REM Check Python version is 3.8 or higher
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    echo ERROR: Python 3.8 or higher is required >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: Python version check passed
echo SUCCESS: Python version check passed >> "%TEST_LOG_FILE%"

REM Validate project structure
echo.
echo ==================================================================
echo VALIDATING PROJECT STRUCTURE
echo ==================================================================

set "REQUIRED_FILES=main.py requirements.txt src\config.py src\social_fetcher.py src\ai_analyzer.py src\blockchain_connector.py contracts\SocialOracle.sol"
set "MISSING_FILES="

for %%f in (%REQUIRED_FILES%) do (
    if exist "%%f" (
        echo SUCCESS: %%f exists
        echo SUCCESS: %%f exists >> "%TEST_LOG_FILE%"
    ) else (
        echo ERROR: Missing required file: %%f
        echo ERROR: Missing required file: %%f >> "%TEST_LOG_FILE%"
        set "MISSING_FILES=!MISSING_FILES! %%f"
    )
)

if not "%MISSING_FILES%"=="" (
    echo ERROR: Missing required files: %MISSING_FILES%
    echo ERROR: Missing required files: %MISSING_FILES% >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: All required project files are present
echo SUCCESS: All required project files are present >> "%TEST_LOG_FILE%"

REM Check and install dependencies
echo.
echo ==================================================================
echo CHECKING AND INSTALLING DEPENDENCIES
echo ==================================================================

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo ERROR: requirements.txt not found >> "%TEST_LOG_FILE%"
    goto :failure
)

echo Installing Python dependencies...
echo Installing Python dependencies... >> "%TEST_LOG_FILE%"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    echo Creating virtual environment... >> "%TEST_LOG_FILE%"
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo SUCCESS: Virtual environment activated
    echo SUCCESS: Virtual environment activated >> "%TEST_LOG_FILE%"
) else (
    echo WARNING: Virtual environment not found, using system Python
    echo WARNING: Virtual environment not found, using system Python >> "%TEST_LOG_FILE%"
)

REM Install dependencies
%PIP_CMD% install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo ERROR: Failed to install dependencies >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: Dependencies installed successfully
echo SUCCESS: Dependencies installed successfully >> "%TEST_LOG_FILE%"

REM Install test dependencies
%PIP_CMD% install pytest pytest-mock >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install test dependencies
    echo ERROR: Failed to install test dependencies >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: Test dependencies installed successfully
echo SUCCESS: Test dependencies installed successfully >> "%TEST_LOG_FILE%"

REM Validate environment configuration
echo.
echo ==================================================================
echo VALIDATING ENVIRONMENT CONFIGURATION
echo ==================================================================

set "ENV_VARS=REDDIT_CLIENT_ID REDDIT_CLIENT_SECRET REDDIT_USER_AGENT GEMINI_API_KEY BNB_RPC_URL PRIVATE_KEY"
set "MISSING_VARS="

if exist ".env" (
    echo SUCCESS: Found .env file
    echo SUCCESS: Found .env file >> "%TEST_LOG_FILE%"
    REM Load .env file (simplified approach for Windows batch)
    for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
        set "%%a=%%b"
    )
) else (
    echo WARNING: .env file not found, checking system environment variables
    echo WARNING: .env file not found, checking system environment variables >> "%TEST_LOG_FILE%"
)

for %%v in (%ENV_VARS%) do (
    if defined %%v (
        echo SUCCESS: %%v is set
        echo SUCCESS: %%v is set >> "%TEST_LOG_FILE%"
    ) else (
        echo ERROR: Missing environment variable: %%v
        echo ERROR: Missing environment variable: %%v >> "%TEST_LOG_FILE%"
        set "MISSING_VARS=!MISSING_VARS! %%v"
    )
)

if not "%MISSING_VARS%"=="" (
    echo ERROR: Missing required environment variables: %MISSING_VARS%
    echo ERROR: Missing required environment variables: %MISSING_VARS% >> "%TEST_LOG_FILE%"
    echo HINT: Create a .env file based on .env.example
    echo HINT: Create a .env file based on .env.example >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: All required environment variables are set
echo SUCCESS: All required environment variables are set >> "%TEST_LOG_FILE%"

REM Test configuration loading
echo.
echo ==================================================================
echo TESTING CONFIGURATION LOADING
echo ==================================================================

echo Testing configuration validation...
echo Testing configuration validation... >> "%TEST_LOG_FILE%"

%PYTHON_CMD% -c "import sys; sys.path.insert(0, 'src'); from config import Config; config = Config.get_api_config(); print('SUCCESS: Configuration loaded successfully')" 2>nul
if errorlevel 1 (
    echo ERROR: Configuration loading test failed
    echo ERROR: Configuration loading test failed >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: Configuration loading test passed
echo SUCCESS: Configuration loading test passed >> "%TEST_LOG_FILE%"

REM Test component imports
echo.
echo ==================================================================
echo TESTING COMPONENT IMPORTS
echo ==================================================================

set "COMPONENTS=src.config:Config src.social_fetcher:SocialMediaFetcher src.ai_analyzer:AIAnalyzer src.blockchain_connector:BlockchainConnector"

for %%c in (%COMPONENTS%) do (
    for /f "tokens=1,2 delims=:" %%a in ("%%c") do (
        echo Testing import: %%a.%%b
        echo Testing import: %%a.%%b >> "%TEST_LOG_FILE%"
        
        %PYTHON_CMD% -c "from %%a import %%b; print('SUCCESS: %%b imported successfully')" 2>nul
        if errorlevel 1 (
            echo ERROR: %%b import failed
            echo ERROR: %%b import failed >> "%TEST_LOG_FILE%"
            goto :failure
        )
        
        echo SUCCESS: %%b import successful
        echo SUCCESS: %%b import successful >> "%TEST_LOG_FILE%"
    )
)

echo SUCCESS: All component imports successful
echo SUCCESS: All component imports successful >> "%TEST_LOG_FILE%"

REM Run unit tests
echo.
echo ==================================================================
echo RUNNING UNIT TESTS
echo ==================================================================

set "TEST_FILES=tests\test_social_fetcher.py tests\test_ai_analyzer.py tests\test_blockchain_connector.py tests\test_main_integration.py test_oracle_logic.py"
set "FAILED_TESTS="
set "TOTAL_TESTS=0"
set "PASSED_TESTS=0"

for %%t in (%TEST_FILES%) do (
    if exist "%%t" (
        echo Running tests in %%t...
        echo Running tests in %%t... >> "%TEST_LOG_FILE%"
        
        %PYTHON_CMD% -m pytest "%%t" -v --tb=short >> "%TEST_LOG_FILE%" 2>&1
        if errorlevel 1 (
            echo ERROR: %%t - FAILED
            echo ERROR: %%t - FAILED >> "%TEST_LOG_FILE%"
            set "FAILED_TESTS=!FAILED_TESTS! %%t"
        ) else (
            echo SUCCESS: %%t - PASSED
            echo SUCCESS: %%t - PASSED >> "%TEST_LOG_FILE%"
            set /a PASSED_TESTS+=1
        )
        set /a TOTAL_TESTS+=1
    ) else (
        echo WARNING: Test file not found: %%t
        echo WARNING: Test file not found: %%t >> "%TEST_LOG_FILE%"
    )
)

echo.
echo Unit Test Summary:
echo   Total test files: %TOTAL_TESTS%
echo   Passed: %PASSED_TESTS%
echo Unit Test Summary: >> "%TEST_LOG_FILE%"
echo   Total test files: %TOTAL_TESTS% >> "%TEST_LOG_FILE%"
echo   Passed: %PASSED_TESTS% >> "%TEST_LOG_FILE%"

if not "%FAILED_TESTS%"=="" (
    echo ERROR: Some unit tests failed: %FAILED_TESTS%
    echo ERROR: Some unit tests failed: %FAILED_TESTS% >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: All unit tests passed
echo SUCCESS: All unit tests passed >> "%TEST_LOG_FILE%"

REM Validate main workflow
echo.
echo ==================================================================
echo VALIDATING MAIN APPLICATION WORKFLOW
echo ==================================================================

echo Testing main application initialization...
echo Testing main application initialization... >> "%TEST_LOG_FILE%"

%PYTHON_CMD% -c "import sys, os; sys.path.insert(0, '.'); os.environ.setdefault('REDDIT_CLIENT_ID', 'test_client_id'); os.environ.setdefault('REDDIT_CLIENT_SECRET', 'test_client_secret'); os.environ.setdefault('REDDIT_USER_AGENT', 'test_user_agent'); os.environ.setdefault('GEMINI_API_KEY', 'test_gemini_key'); os.environ.setdefault('BNB_RPC_URL', 'https://test-rpc.binance.org:8545/'); os.environ.setdefault('PRIVATE_KEY', '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'); from main import SocialOracleOrchestrator; orchestrator = SocialOracleOrchestrator(); print('SUCCESS: Main orchestrator initialized successfully')" 2>nul
if errorlevel 1 (
    echo ERROR: Main application workflow validation failed
    echo ERROR: Main application workflow validation failed >> "%TEST_LOG_FILE%"
    goto :failure
)

echo SUCCESS: Main application workflow validation passed
echo SUCCESS: Main application workflow validation passed >> "%TEST_LOG_FILE%"

REM All tests passed
set "OVERALL_STATUS=PASSED"

echo.
echo ==================================================================
echo INTEGRATION TEST RESULTS
echo ==================================================================
echo SUCCESS: ALL INTEGRATION TESTS PASSED!
echo SUCCESS: Social Oracle system is ready for deployment
echo SUCCESS: ALL INTEGRATION TESTS PASSED! >> "%TEST_LOG_FILE%"
echo SUCCESS: Social Oracle system is ready for deployment >> "%TEST_LOG_FILE%"

REM Cleanup
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
if exist "src\__pycache__" rmdir /s /q "src\__pycache__" >nul 2>&1
if exist "tests\__pycache__" rmdir /s /q "tests\__pycache__" >nul 2>&1
if exist ".pytest_cache" rmdir /s /q ".pytest_cache" >nul 2>&1

echo Test log saved to: %TEST_LOG_FILE%
exit /b 0

:failure
echo.
echo ==================================================================
echo INTEGRATION TEST RESULTS
echo ==================================================================
echo ERROR: INTEGRATION TESTS FAILED
echo Check the test log for detailed error information: %TEST_LOG_FILE%
echo Fix the failing components and run the tests again
echo ERROR: INTEGRATION TESTS FAILED >> "%TEST_LOG_FILE%"
echo Check the test log for detailed error information: %TEST_LOG_FILE% >> "%TEST_LOG_FILE%"
exit /b 1