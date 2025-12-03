@echo off
echo ========================================
echo   AutoML Platform - Render Deployment
echo ========================================
echo.

echo Step 1: Checking Git status...
git status
echo.

echo Step 2: Adding all files...
git add .
echo.

echo Step 3: Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Deploy to Render

git commit -m "%commit_msg%"
echo.

echo Step 4: Pushing to GitHub...
git push origin main
echo.

echo ========================================
echo   ✅ Code pushed to GitHub!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://render.com
echo 2. Click "New +" → "Web Service"
echo 3. Connect your GitHub repository
echo 4. Render will auto-detect render.yaml
echo 5. Click "Create Web Service"
echo.
echo Your app will be live in ~10-15 minutes!
echo.
pause
