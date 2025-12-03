# 🔧 Fix Azure Quota Issue - Step by Step

## Problem
Your Azure account has **0 quota** for App Service. We need to request an increase.

---

## ✅ Solution: Request Quota Increase

### **Method 1: Azure Portal (Easiest)**

1. **Go to Azure Portal**
   - Visit: https://portal.azure.com
   - Sign in with: `harsh.mishra_cs.aiml23@gla.ac.in`

2. **Open Quotas**
   - Click the search bar at the top
   - Type: `Quotas`
   - Click on "Quotas" service

3. **Filter for App Service**
   - Provider: Select `Microsoft.Web`
   - Region: Select `East US`
   - Click "Apply"

4. **Request Increase**
   - Look for "Standard Small App Service Instances" or "Basic Small App Service Instances"
   - Click on it
   - Click "Request quota increase" button
   - Set new limit to: `1` or `2`
   - Add reason: "Student project deployment"
   - Click "Submit"

5. **Wait for Approval**
   - Usually approved in 5-15 minutes for students
   - You'll get an email notification
   - Check status in "My quotas" section

---

### **Method 2: Support Ticket (If Method 1 doesn't work)**

1. **Create Support Request**
   - Go to: https://portal.azure.com
   - Click "?" icon (top right)
   - Click "Help + support"
   - Click "Create a support request"

2. **Fill Details**
   - Issue type: `Service and subscription limits (quotas)`
   - Subscription: `Azure subscription 1`
   - Quota type: `App Service`
   - Click "Next"

3. **Problem Details**
   - Region: `East US`
   - SKU: `Basic (B1)` or `Free (F1)`
   - New limit: `1`
   - Click "Next"

4. **Contact Information**
   - Fill in your details
   - Click "Create"

5. **Wait**
   - Usually resolved in 1-2 hours
   - Check email for updates

---

## 🚀 Alternative: Deploy Without Quota Increase

While waiting for quota approval, you can use **Azure Container Instances** which doesn't need App Service quota:

### **Deploy with Container Instances**

```powershell
# Set variables
$RESOURCE_GROUP = "automl-container-rg"
$CONTAINER_NAME = "automl-app"
$LOCATION = "eastus"
$IMAGE = "python:3.11-slim"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Note: This requires building a Docker image first
# For now, use Render instead (easier and free)
```

---

## 💡 Recommended: Use Render While Waiting

Since Azure quota approval can take time, I recommend:

1. **Deploy to Render now** (free, no quota issues)
   - Follow: `RENDER_DEPLOY_FINAL.md`
   - Takes 10-15 minutes
   - Your app will be live immediately

2. **Request Azure quota in parallel**
   - Follow Method 1 above
   - Once approved, deploy to Azure too
   - You can have both running!

---

## 📊 Check Current Quota

Run this to see your current quotas:

```powershell
# Check subscription
az account show

# List all quotas for East US
az vm list-usage --location eastus --output table

# Check App Service plans
az appservice plan list --output table
```

---

## ✅ After Quota is Approved

Once you get approval email:

1. **Verify Quota**
   ```powershell
   az vm list-usage --location eastus --output table
   ```

2. **Deploy to Azure**
   ```powershell
   cd C:\Users\Dell\Desktop\Auto2\automl-agent
   .\deploy_azure_b1.ps1
   ```

3. **Your app will be live!**
   - URL: `https://automl-harsh-XXXX.azurewebsites.net`
   - Cost: ~$13/month (B1 tier)

---

## 🎯 Quick Decision Guide

**Need app live NOW?**
→ Use Render (free, instant)

**Want to use Azure for Students credit?**
→ Request quota increase (wait 15 min - 2 hours)

**Want both?**
→ Deploy to Render now, Azure later

---

## 📞 Support

**Azure Support:**
- Portal: https://portal.azure.com → Help + support
- Docs: https://docs.microsoft.com/azure/

**Render (Alternative):**
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs

---

## ✅ Summary

Your Azure account is active but needs quota increase for App Service. 

**Next steps:**
1. Request quota increase (Method 1 above)
2. While waiting, deploy to Render
3. Once quota approved, deploy to Azure too

**Both platforms are great - you can use either or both!** 🚀
