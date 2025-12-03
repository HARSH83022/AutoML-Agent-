# 🔵 Azure Deployment Script for AutoML Platform (PowerShell)
# This script deploys your AutoML platform to Azure

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🚀 AutoML Platform - Azure Deployment                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NAME = "automl-harsh-$(Get-Random -Maximum 9999)"
$RESOURCE_GROUP = "automl-rg"
$LOCATION = "eastus"
$RUNTIME = "PYTHON:3.11"
$SKU = "F1"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   App Name: $APP_NAME"
Write-Host "   Resource Group: $RESOURCE_GROUP"
Write-Host "   Location: $LOCATION"
Write-Host "   Runtime: $RUNTIME"
Write-Host "   SKU: $SKU (Free Tier)"
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>$null
    Write-Host "✅ Azure CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found!" -ForegroundColor Red
    Write-Host "   Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
Write-Host "🔐 Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "   Please login to Azure..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Login failed!" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Navigate to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📦 Deploying application..." -ForegroundColor Yellow
Write-Host "   This will take 5-8 minutes..." -ForegroundColor Cyan
Write-Host ""

# Deploy using az webapp up
Write-Host "🚀 Creating resources and deploying code..." -ForegroundColor Yellow
az webapp up `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --runtime $RUNTIME `
  --sku $SKU `
  --logs

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "⚙️  Configuring environment variables..." -ForegroundColor Yellow

# Set environment variables
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings `
    APP_ENV=production `
    LOG_LEVEL=info `
    KAGGLE_USERNAME=harsh83022 `
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a `
    LLM_MODE=none `
    SYNTHETIC_DEFAULT_ROWS=1000 `
  --output none

Write-Host "✅ Environment variables configured" -ForegroundColor Green
Write-Host ""

# Enable CORS
Write-Host "🌐 Enabling CORS..." -ForegroundColor Yellow
az webapp cors add `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --allowed-origins '*' `
  --output none

Write-Host "✅ CORS enabled" -ForegroundColor Green
Write-Host ""

# Get the URL
$APP_URL = az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName --output tsv

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ DEPLOYMENT SUCCESSFUL!                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Your AutoML Platform is live at:" -ForegroundColor Cyan
Write-Host "   https://$APP_URL" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Test these endpoints:" -ForegroundColor Yellow
Write-Host "   Main app:     https://$APP_URL"
Write-Host "   API docs:     https://$APP_URL/docs"
Write-Host "   Health check: https://$APP_URL/health"
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Yellow
Write-Host "   View logs:    az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
Write-Host "   Restart app:  az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
Write-Host "   Stop app:     az webapp stop --name $APP_NAME --resource-group $RESOURCE_GROUP"
Write-Host "   Delete all:   az group delete --name $RESOURCE_GROUP --yes"
Write-Host ""
Write-Host "🔧 Manage in Azure Portal:" -ForegroundColor Yellow
Write-Host "   https://portal.azure.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 Happy AutoML-ing!" -ForegroundColor Green
