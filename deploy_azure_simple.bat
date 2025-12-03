@echo off
REM 🔵 Simple Azure Deployment Script for AutoML Platform (Windows)
REM This script deploys your AutoML platform to Azure in one command

setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════════════════════════╗
echo ║   🚀 AutoML Platform - Azure Deployment                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Configuration
if "%1"=="" (
    set APP_NAME=automl-platform-%RANDOM%
) else (
    set APP_NAME=%1
)
set RESOURCE_GROUP=automl-rg
set LOCATION=eastus
set RUNTIME=PYTHON:3.11

echo 📋 Configuration:
echo    App Name: %APP_NAME%
echo    Resource Group: %RESOURCE_GROUP%
echo    Location: %LOCATION%
echo    Runtime: %RUNTIME%
echo.

REM Check if Azure CLI is installed
where az >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Azure CLI not found!
    echo    Install from: https://aka.ms/installazurecliwindows
    exit /b 1
)

echo ✅ Azure CLI found

REM Check if logged in
echo 🔐 Checking Azure login...
az account show >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo    Please login to Azure...
    az login
)

echo ✅ Logged in to Azure
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo 📦 Deploying application...
echo.

REM Deploy using az webapp up
az webapp up ^
  --name "%APP_NAME%" ^
  --resource-group "%RESOURCE_GROUP%" ^
  --location "%LOCATION%" ^
  --runtime "%RUNTIME%" ^
  --sku F1 ^
  --logs

echo.
echo ⚙️  Configuring environment variables...

REM Set environment variables
az webapp config appsettings set ^
  --name "%APP_NAME%" ^
  --resource-group "%RESOURCE_GROUP%" ^
  --settings ^
    APP_ENV=production ^
    LOG_LEVEL=info ^
    KAGGLE_USERNAME=ramyasharma10 ^
    KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 ^
    LLM_MODE=ollama ^
    OLLAMA_URL=http://localhost:11434/api/generate ^
  --output none

echo ✅ Environment variables configured
echo.

REM Enable CORS
echo 🌐 Enabling CORS...
az webapp cors add ^
  --name "%APP_NAME%" ^
  --resource-group "%RESOURCE_GROUP%" ^
  --allowed-origins * ^
  --output none

echo ✅ CORS enabled
echo.

REM Get the URL
for /f "delims=" %%i in ('az webapp show --name "%APP_NAME%" --resource-group "%RESOURCE_GROUP%" --query defaultHostName --output tsv') do set APP_URL=%%i

echo ╔════════════════════════════════════════════════════════════╗
echo ║   ✅ DEPLOYMENT SUCCESSFUL!                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Your AutoML Platform is live at:
echo    https://%APP_URL%
echo.
echo 📊 View logs:
echo    az webapp log tail --name %APP_NAME% --resource-group %RESOURCE_GROUP%
echo.
echo 🔧 Manage your app:
echo    https://portal.azure.com
echo.
echo 🎉 Happy AutoML-ing!

endlocal
