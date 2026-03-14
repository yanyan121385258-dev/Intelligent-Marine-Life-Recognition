@echo off
echo Starting Hertz Django UI Development Server...
echo.

if not exist "hertz_server_django_ui" (
    echo ERROR: Project directory not found
    pause
    exit /b 1
)

cd hertz_server_django_ui
echo Server starting... Press Ctrl+C to stop
echo.
npm run dev