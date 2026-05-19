@echo off
chcp 65001 >nul
title Studio Django - 打包部署

echo ========================================
echo    Studio Django 项目打包工具
echo ========================================
echo.

set "PROJECT_NAME=HertzStudioDjango"
set "VERSION=1.0.0"

echo 正在创建打包目录...
if exist "deploy_package" rmdir /s /q "deploy_package"
mkdir "deploy_package"

echo.
echo [1/4] 复制项目文件...

xcopy /E /I /Y /Q ".env" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q ".gitignore" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "data" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "demo" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "docs" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "server_django" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\src" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\public" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\.env" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\.env.development" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\.env.production" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\package.json" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\vite.config.ts" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\tsconfig*.json" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\index.html" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\.eslintrc.cjs" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\.prettierrc" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "server_django_ui\.editorconfig" "deploy_package\server_django_ui\" >nul 2>&1
xcopy /E /I /Y /Q "static" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "studio_django_utils" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "manage.py" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "requirements.txt" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "hertz.txt" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "run.bat" "deploy_package\" >nul 2>&1
xcopy /E /I /Y /Q "README.md" "deploy_package\" >nul 2>&1

echo.
echo [2/4] 复制必要配置文件...
if not exist "deploy_package\server_django_ui" mkdir "deploy_package\server_django_ui"

echo. > "deploy_package\README_DEPLOY.txt"

echo.
echo [3/4] 创建压缩包...
powershell -Command "Compress-Archive -Path 'deploy_package\*' -DestinationPath '%PROJECT_NAME%_v%VERSION%.zip' -Force"

echo.
echo [4/4] 清理临时文件...
rmdir /s /q "deploy_package"

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 输出文件: %PROJECT_NAME%_v%VERSION%.zip
echo.
echo 部署说明:
echo   1. 解压 zip 文件到目标电脑
echo   2. 确保已安装 Python 3.10+ 和 Node.js 16+
echo   3. 双击运行 run.bat 即可
echo.
pause
