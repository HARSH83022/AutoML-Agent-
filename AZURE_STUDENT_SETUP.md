# 🎓 Azure for Students - Setup & Deployment

## ✅ **Perfect Choice!**

Azure for Students gives you:
- ✅ **$100 free credit** (valid for 12 months)
- ✅ **No credit card required**
- ✅ **Free services** even after credit expires
- ✅ **Perfect for learning and projects**

---

## 📝 **Step 1: Activate Azure for Students**

### **1. Go to Azure for Students Page**
```
https://azure.microsoft.com/free/students/
```

### **2. Click "Activate Now"**

### **3. Sign In**
- Use your **student email** (if you have one)
- Or use: `harshmishra83022@gmail.com`

### **4. Verify Student Status**

**Option A: With Student Email**
- If you have a `.edu` email, use it
- Azure will automatically verify

**Option B: Without Student Email**
- Upload student ID or enrollment letter
- Wait for verification (usually instant)

### **5. Complete Profile**
- Country: India
- Phone number: Your number
- Verify phone with code

### **6. Accept Terms**
- Read and accept terms
- Click "Sign up"

### **7. Wait for Activation**
- Takes 1-2 minutes
- You'll see "Your subscription is ready"

---

## 🔍 **Step 2: Verify Subscription**

Open PowerShell and run:

```powershell
az login
az account list
```

You should see:
```json
[
  {
    "cloudName": "AzureCloud",
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "isDefault": true,
    "name": "Azure for Students",
    "state": "Enabled"
  }
]
```

✅ **If you see this, you're ready to deploy!**

---

## 🚀 **Step 3: Deploy Your App**

Now run the deployment script:

```powershell
cd C:\Users\Dell\Desktop\Auto2\automl-agent
.\deploy_azure_simple.bat
```

**Or manually:**

```powershell
# Set app name
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
Write-Host "`nYour app URL:"
az webapp show --name $APP_NAME --resource-group automl-rg --query defaultHostName -o tsv
```

---

## ⏱️ **What to Expect**

1. **Deployment starts** (you'll see progress)
2. **Creating resources** (2-3 minutes)
   - Resource group
   - App Service plan
   - Web app
3. **Uploading code** (1-2 minutes)
4. **Building app** (2-3 minutes)
   - Installing dependencies
   - Setting up Python
5. **Starting app** (30 seconds)
6. **Done!** ✅

**Total time: 5-8 minutes**

---

## 🌐 **Step 4: Access Your App**

After deployment, you'll see:

```
Your app is running at: https://automl-harsh-XXXX.azurewebsites.net
```

**Test it:**
1. **Main page**: `https://your-app.azurewebsites.net`
2. **API docs**: `https://your-app.azurewebsites.net/docs`
3. **Health check**: `https://your-app.azurewebsites.net/health`

---

## 💰 **Azure for Students Benefits**

### **What You Get:**
- **$100 credit** for 12 months
- **Free services** including:
  - App Service (F1 tier) - FREE forever
  - 750 hours/month compute
  - 5 GB storage
  - 15 GB bandwidth

### **Cost for Your App:**
- **F1 tier**: $0/month (FREE)
- **B1 tier**: ~$13/month (if you upgrade)

**Your app will run on F1 (FREE) tier by default!**

---

## 📊 **Monitor Your Credit**

**Check remaining credit:**
1. Go to: https://portal.azure.com
2. Click "Cost Management + Billing"
3. View "Credits" section

**You'll see:**
- Total credit: $100
- Used: $X
- Remaining: $Y
- Expiry date

---

## 🔧 **Manage Your App**

### **View Logs**
```powershell
az webapp log tail --name $APP_NAME --resource-group automl-rg
```

### **Restart App**
```powershell
az webapp restart --name $APP_NAME --resource-group automl-rg
```

### **Update Environment Variables**
```powershell
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group automl-rg `
  --settings KEY=VALUE
```

### **Scale Up (if needed)**
```powershell
# Upgrade to B1 tier ($13/month)
az appservice plan update `
  --name automl-plan `
  --resource-group automl-rg `
  --sku B1
```

---

## 🐛 **Troubleshooting**

### **Issue: "No subscription found"**

**Solution:** Activate Azure for Students first
1. Go to: https://azure.microsoft.com/free/students/
2. Click "Activate Now"
3. Verify student status
4. Wait for activation
5. Run `az login` again

### **Issue: "Student verification failed"**

**Solution:** Try these options
1. Use your school email (.edu)
2. Upload student ID
3. Upload enrollment letter
4. Contact Azure support

### **Issue: "Deployment failed"**

**Solution:** Check logs
```powershell
az webapp log tail --name $APP_NAME --resource-group automl-rg
```

### **Issue: "App won't start"**

**Solution:** 
1. Wait 2-3 minutes for startup
2. Check logs for errors
3. Restart app:
```powershell
az webapp restart --name $APP_NAME --resource-group automl-rg
```

---

## 📱 **Azure Portal**

**Manage everything visually:**
1. Go to: https://portal.azure.com
2. Sign in with your account
3. Navigate to "App Services"
4. Click your app name
5. View metrics, logs, settings

**You can:**
- View real-time metrics
- Check logs
- Update settings
- Scale up/down
- Configure custom domains
- Set up SSL certificates

---

## 🎯 **Next Steps After Deployment**

1. ✅ **Test your app** - Visit the URL
2. ✅ **Check API docs** - Visit `/docs` endpoint
3. ✅ **Create test run** - Try the AutoML functionality
4. ✅ **Monitor logs** - Watch for any errors
5. ✅ **Share URL** - Your app is live!

---

## 💡 **Tips for Students**

### **Save Your Credit:**
- Use F1 (Free) tier for testing
- Stop app when not in use:
  ```powershell
  az webapp stop --name $APP_NAME --resource-group automl-rg
  ```
- Delete unused resources
- Monitor your spending

### **Learn More:**
- Azure documentation: https://docs.microsoft.com/azure/
- Azure for Students: https://azure.microsoft.com/free/students/
- Free training: https://docs.microsoft.com/learn/

---

## ✅ **Quick Checklist**

- [ ] Activate Azure for Students
- [ ] Verify subscription with `az account list`
- [ ] Run deployment script
- [ ] Wait for deployment (5-8 minutes)
- [ ] Test app URL
- [ ] Check API docs
- [ ] Monitor logs
- [ ] Share your app!

---

## 🎉 **You're Ready!**

**Now run:**

```powershell
# 1. Verify subscription
az login
az account list

# 2. Deploy
cd C:\Users\Dell\Desktop\Auto2\automl-agent
.\deploy_azure_simple.bat

# 3. Wait 5-8 minutes

# 4. Your app is live!
```

**Your AutoML platform will be deployed with $100 free credit!** 🚀

---

## 📞 **Support**

- **Azure for Students**: https://azure.microsoft.com/free/students/
- **Azure Support**: https://azure.microsoft.com/support/
- **Student Help**: https://aka.ms/azureforstudents

**Good luck with your deployment!** 🎓
