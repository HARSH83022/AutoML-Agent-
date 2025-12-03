# 🚀 Deploy to Azure - Follow These Steps

## ✅ Prerequisites Complete
- ✅ Azure CLI installed
- ✅ Project files ready
- ✅ Requirements.txt configured
- ✅ Startup script created

---

## 📝 **STEP-BY-STEP DEPLOYMENT**

### **Step 1: Open a NEW PowerShell Window**

**Important:** Close this PowerShell and open a NEW one to refresh environment variables.

Press `Windows + X` → Select "Windows PowerShell" or "Terminal"

---

### **Step 2: Login to Azure**

```powershell
az login
```

**What happens:**
- Your browser will open
- Sign in with your Microsoft account
- If you don't have Azure account, create one (FREE with $200 credit!)
- After login, close browser and return to PowerShell

---

### **Step 3: Navigate to Project**

```powershell
cd C:\Users\Dell\Desktop\Auto2\automl-agent
```

---

### **Step 4: Deploy Your App**

**Option A: Use the Automated Script (Easiest)**

```powershell
.\deploy_azure_simple.bat
```

**Option B: Manual Commands**

```powershell
# Set app name (change if you want)
$APP_NAME = "automl-harsh-$(Get-Random -Maximum 9999)"

# Deploy
az webapp up `
  --name $APP_NAME `
  --resource-group automl-rg `
  --location eastus `
  --runtime "PYTHON:3.11" `
  --sku F1

# Configure environment
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group automl-rg `
  --settings `
    APP_ENV=production `
    KAGGLE_USERNAME=harsh83022 `
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a `
    LLM_MODE=none

# Enable CORS
az webapp cors add `
  --name $APP_NAME `
  --resource-group automl-rg `
  --allowed-origins '*'

# Get URL
Write-Host "Your app URL:"
az webapp show --name $APP_NAME --resource-group automl-rg --query defaultHostName -o tsv
```

---

### **Step 5: Wait for Deployment**

**This will take 3-5 minutes. You'll see:**
- Creating resource group...
- Creating App Service plan...
- Deploying code...
- Configuring settings...
- ✅ Deployment complete!

---

### **Step 6: Get Your App URL**

After deployment, you'll see:

```
Your app is running at: https://automl-harsh-XXXX.azurewebsites.net
```

**Copy this URL!**

---

### **Step 7: Test Your App**

Open your browser and visit:

1. **Main URL**: `https://your-app.azurewebsites.net`
2. **API Docs**: `https://your-app.azurewebsites.net/docs`
3. **Health Check**: `https://your-app.azurewebsites.net/health`

---

## 🎯 **Quick Commands Reference**

### View Logs
```powershell
az webapp log tail --name $APP_NAME --resource-group automl-rg
```

### Restart App
```powershell
az webapp restart --name $APP_NAME --resource-group automl-rg
```

### View App Details
```powershell
az webapp show --name $APP_NAME --resource-group automl-rg
```

### Update Environment Variables
```powershell
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group automl-rg `
  --settings KEY=VALUE
```

---

## 🐛 **Troubleshooting**

### Problem: "az: command not found"
**Solution:** 
1. Close PowerShell
2. Open a NEW PowerShell window
3. Try again

### Problem: "Not logged in"
**Solution:**
```powershell
az login
```

### Problem: "App name already exists"
**Solution:** Use a different name:
```powershell
$APP_NAME = "automl-harsh-$(Get-Random -Maximum 9999)"
```

### Problem: "Deployment failed"
**Solution:** Check logs:
```powershell
az webapp log tail --name $APP_NAME --resource-group automl-rg
```

### Problem: "App shows error page"
**Solution:** 
1. Wait 2-3 minutes for app to fully start
2. Check logs for errors
3. Restart app:
```powershell
az webapp restart --name $APP_NAME --resource-group automl-rg
```

---

## 💰 **Cost Information**

**Free Tier (F1):**
- Cost: **$0/month**
- Perfect for testing
- Limitations: 60 min CPU/day, 1GB RAM

**To upgrade to production (B1 - $13/month):**
```powershell
az appservice plan update `
  --name automl-plan `
  --resource-group automl-rg `
  --sku B1
```

---

## 🎉 **Success Checklist**

After deployment, verify:

- [ ] App URL is accessible
- [ ] API docs load at `/docs`
- [ ] Can create a new ML run
- [ ] Logs show no errors
- [ ] Kaggle integration works

---

## 📱 **Manage Your App**

**Azure Portal:** https://portal.azure.com

In the portal you can:
- View metrics and performance
- Configure settings
- Scale up/down
- View detailed logs
- Set up custom domains
- Configure SSL certificates

---

## 🚀 **Ready to Deploy?**

**Run these 3 commands:**

```powershell
# 1. Login
az login

# 2. Navigate
cd C:\Users\Dell\Desktop\Auto2\automl-agent

# 3. Deploy
.\deploy_azure_simple.bat
```

**That's it! Your app will be live in 5 minutes!** 🎊

---

## 📞 **Need Help?**

- **Logs**: `az webapp log tail --name $APP_NAME --resource-group automl-rg`
- **Portal**: https://portal.azure.com
- **Documentation**: See `DEPLOY_AZURE.md`

**Good luck!** 🚀
