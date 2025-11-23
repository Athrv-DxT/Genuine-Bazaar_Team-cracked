@echo off
title Retail Cortex - Starting All Services
color 0A

echo ======================================================================
echo                    Retail Cortex - Starting All Services
echo ======================================================================
echo.

echo [1/2] Starting Backend Server...
echo      URL: http://localhost:8000
echo      API Docs: http://localhost:8000/docs
echo.

start "Retail Cortex Backend" cmd /k "cd /d %~dp0 && python run_server.py"

echo      Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Frontend Server...
echo      URL: http://localhost:3000
echo.

cd frontend
if not exist node_modules (
    echo      Installing dependencies...
    call npm install
)

start "Retail Cortex Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

cd ..

echo.
echo ======================================================================
echo                        All Services Started!
echo ======================================================================
echo.
echo Access Points:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Open http://localhost:3000 in your browser to get started!
echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul

