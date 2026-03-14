@echo off
echo ================================
echo Hertz Django
echo ================================

echo activate venv
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Please run: init_project.bat
    pause
    exit /b 1
)


start "Hertz Backend" /D "%cd%" cmd /c "python start_server.py"


echo ================================
echo Hertz Django Starting Successful
echo Please wait for the server to start...
echo ================================
pause >nul