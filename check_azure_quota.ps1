# Check Azure Quota Status

Write-Host "Checking Azure quota status..." -ForegroundColor Cyan
Write-Host ""

# Check if logged in
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "Subscription: $($account.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in. Please run: az login" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Checking App Service quota..." -ForegroundColor Yellow
Write-Host ""

# Try to create a test app service plan to check quota
$TEST_RG = "quota-test-rg"
$TEST_PLAN = "quota-test-plan"

Write-Host "Testing quota by creating a test App Service Plan..." -ForegroundColor Yellow

# Create resource group
az group create --name $TEST_RG --location eastus --output none 2>$null

# Try to create app service plan
$result = az appservice plan create `
    --name $TEST_PLAN `
    --resource-group $TEST_RG `
    --sku B1 `
    --is-linux `
    --output json 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! You have quota available!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now deploy your app!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Run this command to deploy:" -ForegroundColor Yellow
    Write-Host "  .\deploy_azure_b1.ps1" -ForegroundColor White
    Write-Host ""
    
    # Clean up test resources
    Write-Host "Cleaning up test resources..." -ForegroundColor Yellow
    az group delete --name $TEST_RG --yes --no-wait --output none
    
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "NO QUOTA AVAILABLE" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    
    if ($result -match "quota") {
        Write-Host "You need to request a quota increase." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Follow these steps:" -ForegroundColor Cyan
        Write-Host "1. Go to: https://portal.azure.com" -ForegroundColor White
        Write-Host "2. Search for 'Quotas'" -ForegroundColor White
        Write-Host "3. Filter: Provider = Microsoft.Web, Region = East US" -ForegroundColor White
        Write-Host "4. Request increase for 'Basic Small App Service Instances'" -ForegroundColor White
        Write-Host "5. Set new limit to: 1 or 2" -ForegroundColor White
        Write-Host "6. Submit request" -ForegroundColor White
        Write-Host ""
        Write-Host "Approval usually takes 5-15 minutes for students." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "See full guide: AZURE_QUOTA_FIX.md" -ForegroundColor Cyan
    } else {
        Write-Host "Error: $result" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Alternative: Deploy to Render (free, no quota needed)" -ForegroundColor Cyan
    Write-Host "  See: RENDER_DEPLOY_FINAL.md" -ForegroundColor White
    Write-Host ""
    
    # Clean up test resources
    az group delete --name $TEST_RG --yes --no-wait --output none 2>$null
}
