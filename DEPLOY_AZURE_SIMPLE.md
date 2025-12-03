# 🔵 Deploy to Azure - Simple Guide

## Quick Deploy (One Command)

### For Windows:
```cmd
deploy_azure_simple.bat
```

### For Linux/Mac:
```bash
chmod +x deploy_azure_simple.sh
./deploy_azure_simple.sh
```

---

## Manual Deployment Steps

### 1. Install Azure CLI

**Windows:**
```cmd
winget install Microsoft.AzureCLI
```

Or download: https://aka.ms/installazurecliwindows

**Verify installation:**
```cmd
az --version
```

### 2. Login to Azure

```cmd
az login
```

This opens your browser for authentication.

### 3. Deploy with One Command

```cmd
cd AutoML-Agent-

az webapp up ^
  --name automl-platform-harsh ^
  --resource-group automl-rg ^
  --location eastus ^
  --runtime PYTHON:3.11 ^
  --sku F1 ^
  --logs
```

### 4. Configure Environment Variables

```cmd
az webapp config appsettings set ^
  --name automl-platform-harsh ^
  --resource-group automl-rg ^
  --settings ^
    APP_ENV=production ^
    LOG_LEVEL=info ^
    KAGGLE_USERNAME=harsh83022 ^
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a ^
    LLM_MODE=none ^
    SYNTHETIC_DEFAULT_ROWS=1000 ^
  --output none
```

### 5. Enable CORS

```cmd
az webapp cors add ^
  --name automl-platform-harsh ^
  --resource-group automl-rg ^
  --allowed-origins * ^
  --output none
```

### 6. Access Your App

Your app will be available at:
```
https://automl-platform-harsh.azurewebsites.net
```

Dashboard:
```
https://automl-platform-harsh.azurewebsites.net/dashboard
```

---

## View Logs

```cmd
az webapp log tail --name automl-platform-harsh --resource-group automl-rg
```

---

## Update Deployment

After making code changes:

```cmd
cd AutoML-Agent-
git add .
git commit -m "Update"
git push

az webapp up --name automl-platform-harsh --resource-group automl-rg
```

---

## Troubleshooting

### Check if app is running:
```cmd
az webapp show --name automl-platform-harsh --resource-group automl-rg --query state
```

### Restart app:
```cmd
az webapp restart --name automl-platform-harsh --resource-group automl-rg
```

### View configuration:
```cmd
az webapp config appsettings list --name automl-platform-harsh --resource-group automl-rg
```

---

## Cost

**Free Tier (F1):**
- ✅ Free for 60 minutes/day
- ✅ 1 GB RAM
- ✅ 1 GB storage
- ✅ Perfect for testing

**Basic Tier (B1) - $13/month:**
- ✅ Always on
- ✅ 1.75 GB RAM
- ✅ 10 GB storage
- ✅ Better for production

To upgrade:
```cmd
az appservice plan update --name automl-plan --resource-group automl-rg --sku B1
```

---

## Delete Resources

To remove everything:
```cmd
az group delete --name automl-rg --yes --no-wait
```

---

## Next Steps

1. ✅ Deploy using the command above
2. ✅ Wait 5-10 minutes for deployment
3. ✅ Access your app at the Azure URL
4. ✅ Test the dashboard
5. ✅ Run a sample ML pipeline

**Your Azure subscription makes this the best option!** 🎉
