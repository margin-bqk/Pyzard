@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo         Pyzard 构建工具
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查PyInstaller是否安装
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 错误: PyInstaller未安装
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 安装PyInstaller失败，请手动运行: pip install pyinstaller
        pause
        exit /b 1
    )
    echo ✓ PyInstaller安装成功
)

:: 显示版本信息
echo 正在获取版本信息...
for /f "tokens=*" %%i in ('python -c "from version import get_version; print(get_version())"') do set VERSION=%%i
echo 当前版本: !VERSION!

:: 显示构建选项
echo.
echo 请选择构建选项:
echo 1. 完整构建 (清理并重新构建)
echo 2. 增量构建 (不清理构建目录)
echo 3. 显示构建信息
echo 4. 退出
echo.

set /p CHOICE="请输入选项 (1-4): "

if "!CHOICE!"=="1" (
    echo.
    echo 开始完整构建...
    python build.py
) else if "!CHOICE!"=="2" (
    echo.
    echo 开始增量构建...
    python build.py --no-clean
) else if "!CHOICE!"=="3" (
    echo.
    echo 显示构建信息...
    python build.py --info
    pause
    goto :EOF
) else if "!CHOICE!"=="4" (
    echo 退出构建工具
    exit /b 0
) else (
    echo 无效选项，请重新选择
    goto :menu
)

:: 检查构建结果
if errorlevel 1 (
    echo.
    echo ❌ 构建失败!
    echo 请检查错误信息并重试
    pause
    exit /b 1
) else (
    echo.
    echo ✓ 构建成功完成!
    echo 可执行文件位置: dist\Pyzard_!VERSION!.exe
    echo.
    
    :: 询问是否打开输出目录
    set /p OPEN_DIR="是否打开输出目录? (y/n, 默认n): "
    if /i "!OPEN_DIR!"=="y" (
        if exist "dist\" (
            explorer "dist\"
        ) else (
            echo 输出目录不存在
        )
    )
)

echo.
pause
