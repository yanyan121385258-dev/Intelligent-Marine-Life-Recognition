@echo off
chcp 65001 >nul
title Studio Django - Quick Start

echo ========================================
echo    Studio Django Quick Start Script
echo ========================================
echo.

cd /d %~dp0

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python first!
    pause
    exit /b 1
)

echo [2/4] Checking Python dependencies...
pip show django >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install requirements.txt!
        pause
        exit /b 1
    )
)

echo [3/4] Starting backend server...
start "Studio Django Backend" cmd /k "python start_server.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo [4/4] Starting frontend server...
cd server_django_ui
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies!
        pause
        exit /b 1
    )
)
start "Studio Django Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo    Startup Complete!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3001
echo.
echo Please visit: http://localhost:3001
echo.
echo Press any key to exit...
pause >nul
