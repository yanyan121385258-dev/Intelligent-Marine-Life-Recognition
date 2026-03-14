@echo off
chcp 65001 >nul
echo ================================
echo Hertz Django Project Initialization Script
echo ================================

echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo Error: Python not detected, please install Python first!
    pause
    exit /b 1
)

echo Configuring pip global mirror...
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment!
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment!
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Error: Failed to upgrade pip!
    pause
    exit /b 1
)

echo Installing Python third-party dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install requirements.txt!
    pause
    exit /b 1
)

echo Installing Hertz official dependencies...
pip install -r hertz.txt -i https://hertz:hertz@hzpypi.hzsystems.cn/simple/
if %errorlevel% neq 0 (
    echo Error: Failed to install hertz.txt! Please activate the machine code first.
    pause
    exit /b 1
)

echo ================================
echo Project initialization completed!
echo ================================
echo Please run start_project.bat to start the project
pause