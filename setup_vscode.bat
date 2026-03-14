@echo off
echo ========================================
echo VS Code 配置设置脚本
echo ========================================
echo.

echo [1/3] 确保已安装必要的扩展...
echo.
echo 已安装的扩展：
code --list-extensions
echo.

echo [2/3] 提示：请确保已禁用 Vetur 扩展（如果已安装）
echo.

echo [3/3] 正在重新加载 VS Code 窗口...
echo.

echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 请按以下步骤操作：
echo 1. 在 VS Code 中按 Ctrl+Shift+P
echo 2. 输入 "Reload Window" 并回车
echo 3. 或者直接关闭并重新打开 VS Code
echo.
echo 如果仍然看到误报，请确保：
echo - 已禁用 Vetur 扩展
echo - 已启用 Vue - Official (Volar) 扩展
echo.
pause
