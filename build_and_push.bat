@echo off
REM nuttyfi32 Complete Build and Push Script
REM This script: builds package AND pushes to GitHub

echo ========================================
echo nuttyfi32 Complete Package Builder
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [Step 1/2] Building package...
echo (This will: clean old ZIPs, build package, update JSON)
echo.
python build_nuttyfi32_complete.py
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo [Step 2/2] Pushing to GitHub...
echo ========================================
echo.
python push_to_github.py
if errorlevel 1 (
    echo.
    echo WARNING: GitHub push failed!
    echo You can push manually later using: python push_to_github.py
    pause
    exit /b 1
)

echo.
echo ========================================
echo All Done! Package built and pushed!
echo ========================================
echo.
pause

