# Azure Deployment Script - Try West US region

Write-Host "Deploying to West US (better quota availability)..." -ForegroundColor Cyan
Write-Host ""

$APP_NAME = "automl-harsh-$(Get-Random -Maximum 9999)"
$RESOURCE_GROUP = "automl-rg-west"
$LOCATION = "westus"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  App Name: $APP_NAME"
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  Location: $LOCATION (West US)"
Write-Host "  SKU: B1"
Write-Host ""

az webapp up --name $APP_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --runtime "PYTHON:3.11" --sku B1 --logs

if ($LASTEXITCODE -eq 0) {
    az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings APP_ENV=production KAGGLE_USERNAME=harsh83022 KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a LLM_MODE=none --output none
    az webapp cors add --name $APP_NAME --resource-group $RESOURCE_GROUP --allowed-origins '*' --output none
    $APP_URL = az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName --output tsv
    Write-Host ""
    Write-Host "SUCCESS! Your app: https://$APP_URL" -ForegroundColor Green
}
