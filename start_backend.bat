@echo off
setlocal
echo Starting TeenFreelance Backend...
echo.

REM --- Resolve Python command (prefers py -3, then python) ---
set PYTHON_CMD=
py -3 --version >nul 2>&1 && set PYTHON_CMD=py -3
if not defined PYTHON_CMD (
    python --version >nul 2>&1 && set PYTHON_CMD=python
)
if not defined PYTHON_CMD (
    echo [ERROR] Python is not available in PATH.
    echo Install Python from https://www.python.org/downloads/ and check "Add python.exe to PATH".
    echo Then re-run this script.
    pause
    exit /b 1
)

REM --- Warn about missing .env ---
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create .env from .env.example before running in production.
    echo Using defaults may fail.
    echo.
    REM Fallback env vars for local run (not for production)
    set "SECRET_KEY=dev-secret-key-change-me-32chars-001"
    set "DATABASE_URL=sqlite+aiosqlite:///./teenfreelance.db"
    set "CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000"
    set "DEBUG=true"
    set "ENVIRONMENT=development"
    set "REDIS_URL=redis://localhost:6379/0"
    set "REDIS_PASSWORD="
    set "ACCESS_TOKEN_EXPIRE_MINUTES=30"
    set "REFRESH_TOKEN_EXPIRE_DAYS=7"
    set "PASSWORD_RESET_TOKEN_TTL=3600"
    set "RATE_LIMIT_REQUESTS=100"
    set "RATE_LIMIT_WINDOW=60"
    set "MAX_FILE_SIZE=10485760"
    set "ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf"
    set "LOG_LEVEL=INFO"
    set "APP_NAME=TeenFreelance"
    set "APP_VERSION=1.0.0"
    set "FRONTEND_URL=http://localhost:3000"
)

REM --- Create venv if missing ---
if not exist venv (
    echo Creating virtual environment with %PYTHON_CMD% ...
    %PYTHON_CMD% -m venv venv || (
        echo [ERROR] Failed to create venv. Check Python install.
        pause
        exit /b 1
    )
)

REM --- Activate venv ---
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] venv activation script not found.
    pause
    exit /b 1
)

REM --- Install deps if needed (only if fastapi missing) ---
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies (pip install -e .)...
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -e . || (
        echo [ERROR] Failed to install dependencies. Check internet/proxy.
        pause
        exit /b 1
    )
)

REM --- Start the backend ---
echo Starting backend server on http://localhost:8000
echo API docs available at http://localhost:8000/docs
echo.
python main.py

endlocal
