@echo off
REM Deploy to Azure with B1 tier (no quota issues)

echo ╔════════════════════════════════════════════════════════════╗
echo ║   🚀 AutoML Platform - Azure B1 Deployment                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set APP_NAME=automl-harsh
set RESOURCE_GROUP=automl-rg
set LOCATION=eastus

echo 📋 Configuration:
echo    App Name: %APP_NAME%
echo    Resource Group: %RESOURCE_GROUP%
echo    Location: %LOCATION%
echo    SKU: B1 (Basic - $13/month, covered by your $100 credit)
echo.

echo 📦 Deploying application with B1 tier...
echo.

az webapp up ^
  --name %APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --location %LOCATION% ^
  --runtime "PYTHON:3.11" ^
  --sku B1 ^
  --logs

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deployment failed!
    pause
    exit /b 1
)

echo.
echo ⚙️  Configuring environment variables...

az webapp config appsettings set ^
  --name %APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --settings ^
    APP_ENV=production ^
    LOG_LEVEL=info ^
    KAGGLE_USERNAME=harsh83022 ^
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a ^
    LLM_MODE=none ^
    SYNTHETIC_DEFAULT_ROWS=1000 ^
  --output none

echo ✅ Environment variables configured
echo.

echo 🌐 Enabling CORS...
az webapp cors add ^
  --name %APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --allowed-origins * ^
  --output none

echo ✅ CORS enabled
echo.

for /f "delims=" %%i in ('az webapp show --name %APP_NAME% --resource-group %RESOURCE_GROUP% --query defaultHostName --output tsv') do set APP_URL=%%i

echo ╔════════════════════════════════════════════════════════════╗
echo ║   ✅ DEPLOYMENT SUCCESSFUL!                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Your AutoML Platform is live at:
echo    https://%APP_URL%
echo.
echo 📊 Dashboard:
echo    https://%APP_URL%/dashboard
echo.
echo 📊 View logs:
echo    az webapp log tail --name %APP_NAME% --resource-group %RESOURCE_GROUP%
echo.
echo 💰 Cost: ~$13/month (covered by your $100 Azure credit)
echo.
echo 🎉 Happy AutoML-ing!
echo.

pause
