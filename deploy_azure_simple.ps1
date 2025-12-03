# Azure Deployment Script for AutoML Platform

Write-Host "Deploying AutoML Platform to Azure..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NAME = "automl-harsh-$(Get-Random -Maximum 9999)"
$RESOURCE_GROUP = "automl-rg"
$LOCATION = "eastus"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  App Name: $APP_NAME"
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  Location: $LOCATION"
Write-Host ""

# Check Azure login
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    az login
}
Write-Host ""

# Deploy
Write-Host "Deploying application (this takes 5-8 minutes)..." -ForegroundColor Yellow
Write-Host ""

az webapp up --name $APP_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --runtime "PYTHON:3.11" --sku F1 --logs

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Configuring environment variables..." -ForegroundColor Yellow

az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings APP_ENV=production LOG_LEVEL=info KAGGLE_USERNAME=harsh83022 KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a LLM_MODE=none SYNTHETIC_DEFAULT_ROWS=1000 --output none

Write-Host "Enabling CORS..." -ForegroundColor Yellow
az webapp cors add --name $APP_NAME --resource-group $RESOURCE_GROUP --allowed-origins '*' --output none

# Get URL
$APP_URL = az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName --output tsv

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your app is live at:" -ForegroundColor Cyan
Write-Host "https://$APP_URL" -ForegroundColor Green
Write-Host ""
Write-Host "Test endpoints:" -ForegroundColor Yellow
Write-Host "  Main:   https://$APP_URL"
Write-Host "  Docs:   https://$APP_URL/docs"
Write-Host "  Health: https://$APP_URL/health"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
Write-Host "  Restart:     az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP"
Write-Host "  Delete all:  az group delete --name $RESOURCE_GROUP --yes"
Write-Host ""
