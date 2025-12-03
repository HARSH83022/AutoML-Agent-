# 🚀 Complete Azure Deployment - Step by Step

## ❌ **What Happened:**

The `az webapp up` command failed because:
1. Microsoft.Web provider was being registered (first-time setup)
2. The command timed out or failed during registration
3. The web app was not created

## ✅ **Solution: Complete the Deployment**

Run these commands in your PowerShell window:

---

## **Step 1: Wait for Provider Registration (if needed)**

```powershell
# Check if Microsoft.Web is registered
az provider show --namespace Microsoft.Web --query "registrationState"
```

If it shows "Registering", wait 1-2 minutes and check again.

If it shows "NotRegistered", register it:
```powershell
az provider register --namespace Microsoft.Web
```

---

## **Step 2: Deploy Using az webapp up (Retry)**

```powershell
cd C:\Users\Dell\Desktop\Auto2\automl-agent

az webapp up `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --location eastus `
  --runtime "PYTHON:3.11" `
  --sku F1 `
  --logs
```

**This will:**
- Use the existing resource group
- Create the App Service Plan (if not exists)
- Create the Web App
- Upload your code
- Build and deploy

**Wait 5-8 minutes for completion.**

---

## **Step 3: Configure Environment Variables**

After deployment succeeds:

```powershell
az webapp config appsettings set `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --settings `
    APP_ENV=production `
    LOG_LEVEL=info `
    KAGGLE_USERNAME=harsh83022 `
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a `
    LLM_MODE=none `
    SYNTHETIC_DEFAULT_ROWS=1000 `
    PYTHON_VERSION=3.11
```

---

## **Step 4: Configure Startup Command**

```powershell
az webapp config set `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --timeout 600"
```

---

## **Step 5: Enable CORS**

```powershell
az webapp cors add `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --allowed-origins '*'
```

---

## **Step 6: Get Your App URL**

```powershell
az webapp show `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --query defaultHostName `
  --output tsv
```

Your app will be at: `https://automl-harsh-platform.azurewebsites.net`

---

## **Alternative: Use Azure Portal**

If commands keep failing, use the Azure Portal:

### **1. Go to Azure Portal**
```
https://portal.azure.com
```

### **2. Create Web App Manually**

1. Click "Create a resource"
2. Search for "Web App"
3. Click "Create"
4. Fill in:
   - **Resource Group**: automl-rg (select existing)
   - **Name**: automl-harsh-platform
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Region**: East US
   - **Pricing plan**: F1 (Free)
5. Click "Review + Create"
6. Click "Create"

### **3. Deploy Code**

After web app is created:

1. Go to your web app in portal
2. Click "Deployment Center"
3. Choose "Local Git" or "GitHub"
4. Follow instructions to push code

**Or use VS Code Azure extension:**
1. Install "Azure App Service" extension
2. Right-click on `automl-agent` folder
3. Select "Deploy to Web App"
4. Choose your subscription and app

---

## **Quick Fix: Try Simpler Deployment**

If `az webapp up` keeps failing, try step-by-step:

```powershell
# 1. Create App Service Plan
az appservice plan create `
  --name automl-plan `
  --resource-group automl-rg `
  --sku F1 `
  --is-linux

# 2. Create Web App
az webapp create `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --plan automl-plan `
  --runtime "PYTHON:3.11"

# 3. Deploy code (create a zip first)
Compress-Archive -Path * -DestinationPath deploy.zip -Force

az webapp deployment source config-zip `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --src deploy.zip

# 4. Configure settings (from Step 3 above)
```

---

## **Check Deployment Status**

```powershell
# View deployment logs
az webapp log tail `
  --name automl-harsh-platform `
  --resource-group automl-rg

# Check app status
az webapp show `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --query state
```

---

## **Troubleshooting**

### **Issue: Provider still registering**

**Solution:** Wait 2-3 minutes, then retry deployment

```powershell
# Check status
az provider show --namespace Microsoft.Web --query "registrationState"

# If "Registering", wait and check again
# If "Registered", proceed with deployment
```

### **Issue: Deployment fails with timeout**

**Solution:** Use the step-by-step approach above or Azure Portal

### **Issue: App created but not starting**

**Solution:** Check logs

```powershell
az webapp log tail --name automl-harsh-platform --resource-group automl-rg
```

---

## **Summary of Commands**

**Complete deployment in one go:**

```powershell
# Navigate to project
cd C:\Users\Dell\Desktop\Auto2\automl-agent

# Deploy
az webapp up `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --location eastus `
  --runtime "PYTHON:3.11" `
  --sku F1

# Configure
az webapp config appsettings set `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --settings `
    APP_ENV=production `
    KAGGLE_USERNAME=harsh83022 `
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a `
    LLM_MODE=none

# Enable CORS
az webapp cors add `
  --name automl-harsh-platform `
  --resource-group automl-rg `
  --allowed-origins '*'

# Get URL
az webapp show --name automl-harsh-platform --resource-group automl-rg --query defaultHostName -o tsv
```

---

## **Your App URL**

Once deployed successfully:
```
https://automl-harsh-platform.azurewebsites.net
```

Test it:
- Main page: https://automl-harsh-platform.azurewebsites.net
- API docs: https://automl-harsh-platform.azurewebsites.net/docs
- Health: https://automl-harsh-platform.azurewebsites.net/health

---

**Try the deployment again with the commands above!** 🚀
