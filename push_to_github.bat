@echo off
echo ========================================
echo   Pushing Clean Code to GitHub
echo ========================================
echo.

echo Step 1: Removing old git history...
rmdir /s /q .git
echo.

echo Step 2: Initializing fresh repository...
git init
echo.

echo Step 3: Adding all files (venv excluded by .gitignore)...
git add .
echo.

echo Step 4: Creating initial commit...
git commit -m "Complete AutoML Platform - Ready for Render deployment"
echo.

echo Step 5: Setting remote to your GitHub repo...
git remote add origin https://github.com/HARSH83022/AutoML-Agent-.git
echo.

echo Step 6: Creating Phase-4 branch...
git branch -M Phase-4
echo.

echo Step 7: Force pushing to GitHub (this will replace Phase-4 branch)...
git push -u origin Phase-4 --force
echo.

echo ========================================
echo   ✅ Upload Complete!
echo ========================================
echo.
echo Your code is now on GitHub at:
echo https://github.com/HARSH83022/AutoML-Agent-/tree/Phase-4
echo.
echo Next: Deploy on Render
echo 1. Go to https://render.com
echo 2. Click "New +" → "Web Service"
echo 3. Select your repository
echo 4. Select branch: Phase-4
echo 5. Click "Create Web Service"
echo.
pause
