# 🚀 Deploy to Azure NOW - Step by Step

## Your Azure Subscription
✅ **Subscription ID**: `2fba2292-ebbf-41c2-9ced-3cff488ae048`
✅ **Subscription**: Azure for Students
✅ **Role**: Owner
✅ **Status**: Active

---

## Step 1: Install Azure CLI (5 minutes)

### Option A: Using winget (Recommended)
Open PowerShell as Administrator and run:
```powershell
winget install Microsoft.AzureCLI
```

### Option B: Direct Download
Download and install from:
https://aka.ms/installazurecliwindows

### Verify Installation
Close and reopen PowerShell, then run:
```powershell
az --version
```

---

## Step 2: Login to Azure (1 minute)

```powershell
az login
```

This will open your browser. Login with your Azure account.

---

## Step 3: Set Your Subscription (1 minute)

```powershell
az account set --subscription 2fba2292-ebbf-41c2-9ced-3cff488ae048
```

Verify:
```powershell
az account show
```

---

## Step 4: Deploy Your App (10 minutes)

Navigate to your project:
```powershell
cd D:\Auto_Agent\AutoML-Agent-
```

### Option A: Using the Deployment Script (Easiest)
```powershell
.\deploy_azure_simple.bat automl-harsh
```

### Option B: Manual Commands
```powershell
# Create resource group
az group create --name automl-rg --location eastus

# Deploy app
az webapp up `
  --name automl-harsh `
  --resource-group automl-rg `
  --location eastus `
  --runtime "PYTHON:3.11" `
  --sku F1 `
  --logs

# Configure environment variables
az webapp config appsettings set `
  --name automl-harsh `
  --resource-group automl-rg `
  --settings `
    APP_ENV=production `
    LOG_LEVEL=info `
    KAGGLE_USERNAME=harsh83022 `
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a `
    LLM_MODE=none `
    SYNTHETIC_DEFAULT_ROWS=1000 `
  --output none

# Enable CORS
az webapp cors add `
  --name automl-harsh `
  --resource-group automl-rg `
  --allowed-origins '*' `
  --output none
```

---

## Step 5: Access Your App

Your app will be live at:
```
https://automl-harsh.azurewebsites.net
```

Dashboard:
```
https://automl-harsh.azurewebsites.net/dashboard
```

---

## Monitoring

### View Logs
```powershell
az webapp log tail --name automl-harsh --resource-group automl-rg
```

### Check Status
```powershell
az webapp show --name automl-harsh --resource-group automl-rg --query state
```

### Restart App
```powershell
az webapp restart --name automl-harsh --resource-group automl-rg
```

---

## Troubleshooting

### If deployment fails:

1. **Check logs**:
```powershell
az webapp log tail --name automl-harsh --resource-group automl-rg
```

2. **Verify subscription**:
```powershell
az account show
```

3. **Check resource group**:
```powershell
az group show --name automl-rg
```

4. **Redeploy**:
```powershell
az webapp up --name automl-harsh --resource-group automl-rg
```

---

## Cost (Azure for Students)

✅ **You have $100 free credit**
✅ **F1 Free Tier**: No cost for basic usage
✅ **Estimated cost**: $0-5/month with free tier

---

## Update Your App

After making code changes:

```powershell
cd D:\Auto_Agent\AutoML-Agent-
git add .
git commit -m "Update"
git push

# Redeploy
az webapp up --name automl-harsh --resource-group automl-rg
```

---

## Delete Resources (When Done)

To remove everything and stop any charges:
```powershell
az group delete --name automl-rg --yes --no-wait
```

---

## Quick Commands Reference

```powershell
# Login
az login

# Set subscription
az account set --subscription 2fba2292-ebbf-41c2-9ced-3cff488ae048

# Deploy
cd D:\Auto_Agent\AutoML-Agent-
az webapp up --name automl-harsh --resource-group automl-rg --runtime "PYTHON:3.11" --sku F1

# View logs
az webapp log tail --name automl-harsh --resource-group automl-rg

# Restart
az webapp restart --name automl-harsh --resource-group automl-rg

# Delete
az group delete --name automl-rg --yes
```

---

## Next Steps

1. ✅ Install Azure CLI (Step 1)
2. ✅ Login to Azure (Step 2)
3. ✅ Set subscription (Step 3)
4. ✅ Deploy app (Step 4)
5. ✅ Test your app (Step 5)

**Total time: ~15-20 minutes** 🚀

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. View Azure Portal: https://portal.azure.com
3. Check deployment logs in the portal

**Your Azure for Students subscription is perfect for this deployment!** 🎓
