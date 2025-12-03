# 🚀 Deploy to Azure - Quick Guide

## ✅ Prerequisites Check
- [x] Azure CLI installed (v2.80.0)
- [ ] Azure account (free tier or student account)
- [ ] Logged into Azure

---

## 📝 Step 1: Login to Azure

Open PowerShell and run:

```powershell
az login
```

This will open your browser. Sign in with your Azure account.

---

## 🎓 For Students: Get Free $100 Credit

If you're a student:
1. Go to: https://azure.microsoft.com/free/students/
2. Click "Activate Now"
3. Verify with student email or ID
4. Get $100 free credit (no credit card needed!)

---

## 🚀 Step 2: Deploy Your App

Run this simple command:

```powershell
cd automl-agent
.\deploy_azure_simple.bat
```

**Or manually:**

```powershell
# Set unique app name
$APP_NAME = "automl-harsh-$(Get-Random -Maximum 9999)"

# Deploy everything in one command
az webapp up `
  --name $APP_NAME `
  --resource-group automl-rg `
  --location eastus `
  --runtime "PYTHON:3.11" `
  --sku F1

# Configure environment variables
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group automl-rg `
  --settings `
    APP_ENV=production `
    LOG_LEVEL=info `
    KAGGLE_USERNAME=harsh83022 `
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a `
    LLM_MODE=none `
    SYNTHETIC_DEFAULT_ROWS=1000

# Enable CORS
az webapp cors add `
  --name $APP_NAME `
  --resource-group automl-rg `
  --allowed-origins '*'

# Get your app URL
Write-Host "`n✅ Your app is live at:"
$url = az webapp show --name $APP_NAME --resource-group automl-rg --query defaultHostName -o tsv
Write-Host "https://$url" -ForegroundColor Green
```

---

## ⏱️ Deployment Time

- Creating resources: 2-3 minutes
- Uploading code: 1-2 minutes  
- Building app: 2-3 minutes
- **Total: 5-8 minutes**

---

## 🌐 Step 3: Access Your App

After deployment completes, you'll see:

```
Your app is running at: https://automl-harsh-XXXX.azurewebsites.net
```

**Test these endpoints:**
- Main app: `https://your-app.azurewebsites.net`
- API docs: `https://your-app.azurewebsites.net/docs`
- Health check: `https://your-app.azurewebsites.net/health`

---

## 💰 Cost

**Free Tier (F1):**
- Cost: $0/month
- 60 CPU minutes/day
- 1 GB RAM
- 1 GB storage
- Perfect for testing!

**Basic Tier (B1) - If you need more:**
- Cost: ~$13/month
- Always-on
- 1.75 GB RAM
- Better performance

---

## 🔧 Manage Your App

### View Logs
```powershell
az webapp log tail --name $APP_NAME --resource-group automl-rg
```

### Restart App
```powershell
az webapp restart --name $APP_NAME --resource-group automl-rg
```

### Stop App (save resources)
```powershell
az webapp stop --name $APP_NAME --resource-group automl-rg
```

### Start App
```powershell
az webapp start --name $APP_NAME --resource-group automl-rg
```

### Delete Everything
```powershell
az group delete --name automl-rg --yes
```

---

## 🐛 Troubleshooting

### Issue: "No subscription found"

**Solution:**
```powershell
az login
az account list
```

If you see no subscriptions, you need to:
1. Create an Azure account at https://azure.microsoft.com/free/
2. Or activate Azure for Students

### Issue: "Deployment failed"

**Solution:**
```powershell
# Check logs
az webapp log tail --name $APP_NAME --resource-group automl-rg

# Try redeploying
az webapp up --name $APP_NAME --resource-group automl-rg --runtime "PYTHON:3.11"
```

### Issue: "App shows error page"

**Solution:**
1. Wait 2-3 minutes for app to fully start
2. Check logs for errors
3. Restart the app

---

## 📊 Monitor in Azure Portal

1. Go to: https://portal.azure.com
2. Search for your app name
3. View:
   - Metrics (CPU, memory, requests)
   - Logs
   - Settings
   - Scale options

---

## 🎯 Quick Commands Reference

```powershell
# Login
az login

# Deploy
az webapp up --name automl-harsh-1234 --resource-group automl-rg --runtime "PYTHON:3.11" --sku F1

# View logs
az webapp log tail --name automl-harsh-1234 --resource-group automl-rg

# Restart
az webapp restart --name automl-harsh-1234 --resource-group automl-rg

# Get URL
az webapp show --name automl-harsh-1234 --resource-group automl-rg --query defaultHostName -o tsv

# Delete
az group delete --name automl-rg --yes
```

---

## ✅ Success Checklist

- [ ] Azure CLI installed
- [ ] Logged into Azure (`az login`)
- [ ] Ran deployment command
- [ ] Waited 5-8 minutes
- [ ] Tested app URL
- [ ] Checked `/docs` endpoint
- [ ] Viewed logs
- [ ] App is working!

---

## 🚀 Ready to Deploy?

**Just run:**

```powershell
cd C:\Users\Dell\Desktop\Auto2\automl-agent
az login
.\deploy_azure_simple.bat
```

**That's it!** Your app will be live in 5-8 minutes! 🎉
