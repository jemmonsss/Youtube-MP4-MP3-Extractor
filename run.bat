@echo off
REM Check if Python is available in PATH
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not added to your PATH.
    pause
    exit /b 1
)

REM Run the downloader script
python main.py

REM Pause so you can see any output before the window closes
pause
