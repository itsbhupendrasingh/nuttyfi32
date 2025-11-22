@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo Pushing nuttyfi32 to GitHub
echo ========================================
echo.
echo Repository: https://github.com/itsbhupendrasingh/nuttyfi32
echo Branch: master
echo.

echo Step 1: Initializing Git...
if not exist ".git" (
    git init
    echo Git initialized.
) else (
    echo Git already initialized.
)
echo.

echo Step 2: Setting remote...
git remote remove origin 2>nul
git remote add origin https://github.com/itsbhupendrasingh/nuttyfi32.git
echo Remote set to: https://github.com/itsbhupendrasingh/nuttyfi32.git
echo.

echo Step 3: Adding all files...
git add .
echo Files added.
echo.

echo Step 4: Committing...
git commit -m "Initial commit: nuttyfi32 BSP v1.0.0"
echo Commit created.
echo.

echo Step 5: Setting branch to master...
git branch -M master
echo Branch set to master.
echo.

echo Step 6: Pushing to GitHub...
echo.
echo NOTE: You may be asked for GitHub credentials.
echo.
git push -u origin master

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo ✅ Successfully pushed to GitHub!
) else (
    echo ❌ Push failed. Check error above.
    echo.
    echo Common issues:
    echo 1. GitHub credentials not configured
    echo 2. Repository doesn't exist or no access
    echo 3. Need to authenticate
)
echo ========================================
echo.
pause

