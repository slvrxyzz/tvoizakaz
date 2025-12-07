@echo off
echo Starting TeenFreelance Frontend...
echo.

REM Navigate to frontend directory
cd fronted

REM Check if .env.local file exists
if not exist .env.local (
    echo WARNING: .env.local file not found!
    echo Creating .env.local from example...
    if exist env.local.example (
        copy env.local.example .env.local >nul
    ) else (
        copy .env.example .env.local 2>nul
    )
    if errorlevel 1 (
        echo Creating default .env.local...
        (
            echo NEXT_PUBLIC_API_URL=http://localhost:8000
            echo NEXT_PUBLIC_WS_URL=ws://localhost:8000
            echo NEXT_PUBLIC_MODE=dev
        ) > .env.local
    )
)

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

REM Start the frontend server
echo Starting frontend server on http://localhost:3000
echo.
call npm run dev


