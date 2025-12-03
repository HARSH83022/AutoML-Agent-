# 🚀 Deploy Your AutoML Platform to Azure NOW!

## ✅ Step 1: Azure CLI Installed!

Azure CLI has been successfully installed on your system.

---

## 📋 Step 2: Login to Azure

**Open a NEW PowerShell window** (to refresh environment variables) and run:

```powershell
az login
```

This will:
1. Open your web browser
2. Ask you to sign in to your Azure account
3. If you don't have an Azure account, create one at: https://azure.microsoft.com/free/

**Note:** Azure offers a FREE tier with $200 credit for 30 days!

---

## 🚀 Step 3: Deploy Your App

After logging in, run these commands in PowerShell:

```powershell
# Navigate to your project
cd C:\Users\Dell\Desktop\Auto2\automl-agent

# Create a unique app name (or use your own)
$APP_NAME = "automl-platform-$(Get-Random -Maximum 9999)"

# Deploy the app
az webapp up `
  --name $APP_NAME `
  --resource-group automl-rg `
  --location eastus `
  --runtime "PYTHON:3.11" `
  --sku F1 `
  --logs

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
az webapp show `
  --name $APP_NAME `
  --resource-group automl-rg `
  --query defaultHostName `
  --output tsv
```

---

## 🎯 Alternative: Use the Deployment Script

Or simply run the deployment script:

```powershell
cd C:\Users\Dell\Desktop\Auto2\automl-agent
.\deploy_azure_simple.bat
```

---

## ⏱️ What to Expect

1. **Login** (30 seconds) - Browser will open for authentication
2. **Deployment** (3-5 minutes) - Azure will:
   - Create resource group
   - Create App Service plan
   - Deploy your code
   - Configure settings
3. **Done!** - Your app will be live

---

## 🌐 Your App URL

After deployment completes, you'll see:

```
Your app is running at: https://automl-platform-XXXX.azurewebsites.net
```

Visit this URL to access your AutoML platform!

---

## 📊 What Gets Deployed

✅ **Backend API** - FastAPI server
✅ **Database** - SQLite for storing runs
✅ **Kaggle Integration** - With your credentials
✅ **AutoML Engine** - FLAML for model training
✅ **Logging** - Full application logs
✅ **Environment Variables** - All configured

---

## 🔍 Verify Deployment

After deployment, test your app:

1. **Visit the URL**: `https://your-app.azurewebsites.net`
2. **Check API**: `https://your-app.azurewebsites.net/docs`
3. **Create a test run**: Use the API or frontend
4. **View logs**:
   ```powershell
   az webapp log tail --name $APP_NAME --resource-group automl-rg
   ```

---

## 🐛 Troubleshooting

### If deployment fails:

**Check logs:**
```powershell
az webapp log tail --name $APP_NAME --resource-group automl-rg
```

**Restart app:**
```powershell
az webapp restart --name $APP_NAME --resource-group automl-rg
```

**Check configuration:**
```powershell
az webapp config appsettings list --name $APP_NAME --resource-group automl-rg
```

### Common Issues:

**1. "App name already exists"**
- Solution: Use a different app name
- Try: `automl-platform-$(Get-Random -Maximum 9999)`

**2. "Deployment timeout"**
- Solution: Wait a bit longer, Azure can take 5-10 minutes
- Check status: `az webapp show --name $APP_NAME --resource-group automl-rg`

**3. "App won't start"**
- Solution: Check if all dependencies are in requirements.txt
- View logs: `az webapp log tail --name $APP_NAME --resource-group automl-rg`

---

## 💰 Cost

**Free Tier (F1):**
- **Cost**: $0/month
- **Limitations**: 
  - 60 minutes CPU/day
  - 1 GB RAM
  - 1 GB storage
- **Perfect for**: Testing and demos

**To upgrade later:**
```powershell
az appservice plan update --name automl-plan --resource-group automl-rg --sku B1
```

**Production Tier (B1):**
- **Cost**: $13/month
- **Features**:
  - Always on
  - 1.75 GB RAM
  - 10 GB storage
  - Custom domains

---

## 🎯 Next Steps After Deployment

1. ✅ **Test the API**: Visit `/docs` endpoint
2. ✅ **Create a test run**: Try the AutoML functionality
3. ✅ **Check Kaggle integration**: Verify data fetching works
4. ✅ **Monitor logs**: Watch for any errors
5. ✅ **Share the URL**: Your app is live!

---

## 📱 Manage Your App

**Azure Portal**: https://portal.azure.com
- View metrics
- Configure settings
- Monitor performance
- View logs
- Scale up/down

**CLI Commands**:
```powershell
# View app details
az webapp show --name $APP_NAME --resource-group automl-rg

# View logs
az webapp log tail --name $APP_NAME --resource-group automl-rg

# Restart app
az webapp restart --name $APP_NAME --resource-group automl-rg

# Stop app
az webapp stop --name $APP_NAME --resource-group automl-rg

# Start app
az webapp start --name $APP_NAME --resource-group automl-rg

# Delete app (if needed)
az webapp delete --name $APP_NAME --resource-group automl-rg
```

---

## 🎉 You're Ready!

**Now run these commands in a NEW PowerShell window:**

```powershell
# 1. Login to Azure
az login

# 2. Navigate to project
cd C:\Users\Dell\Desktop\Auto2\automl-agent

# 3. Run deployment script
.\deploy_azure_simple.bat
```

**Your AutoML platform will be live in 5 minutes!** 🚀

---

## 📞 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Review logs: `az webapp log tail --name $APP_NAME --resource-group automl-rg`
3. Visit Azure Portal: https://portal.azure.com
4. Check `DEPLOY_AZURE.md` for detailed instructions

**Good luck with your deployment!** 🎊
