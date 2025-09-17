@echo off
setlocal enabledelayedexpansion

:: ===== 用户输入参数 =====
set /p "source=source path: "
set /p "target=target path: "
set /p "csv=csv path: "
set /p "log=log path: "

:: 确保目标目录存在
if not exist "%target%" mkdir "%target%"

:: 清空旧的log并写表头
> "%log%" echo "Folder_Structure"

:: 逐行读取CSV
for /f "tokens=1 delims=, " %%a in (%csv%) do (
    echo 正在搜索文件夹: %%a
    for /f "delims=" %%i in ('dir /s /b /ad "%source%" ^| findstr /i "\\%%a$"') do (
        echo 找到: %%i
        echo 正在复制到 "%target%\%%a" ...
        robocopy "%%i" "%target%\%%a" /E /NFL /NDL /NJH /NJS /nc /ns /np
    )
)

:: 导出目标路径的文件夹结构到CSV
echo 正在导出文件夹结构到 %log% ...
for /f "delims=" %%j in ('dir "%target%" /s /b /ad') do (
    echo "%%j" >> "%log%"
)

echo 完成！结果保存在 %log%
pause
