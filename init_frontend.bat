@echo off
echo Initializing Hertz Django UI Project...
echo.

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
    pause
    exit /b 1
)

if not exist "hertz_server_django_ui" (
    echo ERROR: Project directory missing
    pause
    exit /b 1
)

cd hertz_server_django_ui
echo Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Dependency installation failed
    pause
    exit /b 1
)

echo SUCCESS: Project initialized successfully
echo Run "start.bat" to start the development server
pause