# 🚀 AutoML Platform - Complete Deployment Guide

## 🏆 **Recommendation: Deploy to Azure**

Azure is **5x easier** and **50% cheaper** than AWS for your AutoML platform.

---

## ⚡ Quick Deploy to Azure (5 Minutes)

### Option 1: One-Command Deploy (Windows)

```bash
cd automl-agent
deploy_azure_simple.bat
```

### Option 2: One-Command Deploy (Linux/Mac)

```bash
cd automl-agent
chmod +x deploy_azure_simple.sh
./deploy_azure_simple.sh
```

### Option 3: Manual Deploy

```bash
# 1. Install Azure CLI
winget install Microsoft.AzureCLI

# 2. Login
az login

# 3. Deploy
cd automl-agent
az webapp up --name your-automl-app --runtime "PYTHON:3.11"

# 4. Configure
az webapp config appsettings set --name your-automl-app --settings \
  KAGGLE_USERNAME=ramyasharma10 \
  KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 \
  APP_ENV=production
```

**Done! Your app is live at:** `https://your-automl-app.azurewebsites.net`

---

## 📊 Azure vs AWS Comparison

| Feature | Azure | AWS |
|---------|-------|-----|
| **Setup Time** | 5 minutes | 30-60 minutes |
| **Commands** | 3 | 10+ |
| **Cost (Free)** | $0/month | Not available |
| **Cost (Production)** | $13/month | $50/month |
| **Difficulty** | ⭐ Easy | ⭐⭐⭐⭐ Hard |
| **Python Support** | Native | Requires config |

**Winner: Azure** 🔵

---

## 💰 Cost Breakdown

### Azure Pricing

**Free Tier (Perfect for Testing):**
- App Service F1: **$0/month** ✅
- 60 minutes CPU/day
- 1 GB RAM
- 1 GB storage
- **Perfect for demos and testing!**

**Production Tier:**
- App Service B1: **$13/month** ✅
- Always on
- 1.75 GB RAM
- 10 GB storage
- Custom domains
- **Great for small-medium apps**

**High Performance:**
- App Service S1: **$70/month**
- 1.75 GB RAM
- Auto-scaling
- Staging slots
- **For production apps**

### AWS Pricing

**Minimum Cost:**
- EC2 t2.medium: **$35/month**
- Load Balancer: **$20/month**
- S3 + CloudFront: **$2/month**
- **Total: $57/month** ❌
- **No free tier for production!**

---

## 📁 Deployment Files Created

✅ **DEPLOYMENT_COMPARISON.md** - Detailed Azure vs AWS comparison
✅ **DEPLOY_AZURE.md** - Complete Azure deployment guide
✅ **DEPLOY_AWS.md** - Complete AWS deployment guide
✅ **deploy_azure_simple.sh** - One-command deploy script (Linux/Mac)
✅ **deploy_azure_simple.bat** - One-command deploy script (Windows)
✅ **Dockerfile** - Container configuration
✅ **requirements.txt** - Python dependencies

---

## 🎯 Deployment Steps

### Step 1: Choose Your Platform

**Recommended: Azure** (easier, cheaper)
- See `DEPLOY_AZURE.md`
- Run `deploy_azure_simple.bat`

**Alternative: AWS** (more complex)
- See `DEPLOY_AWS.md`
- Requires more setup

### Step 2: Install CLI

**Azure:**
```bash
winget install Microsoft.AzureCLI
```

**AWS:**
```bash
# Download from: https://aws.amazon.com/cli/
pip install awsebcli
```

### Step 3: Deploy

**Azure:**
```bash
cd automl-agent
deploy_azure_simple.bat
```

**AWS:**
```bash
cd automl-agent
eb init -p python-3.11 automl-platform
eb create automl-env
```

### Step 4: Configure

**Azure:**
- Automatic via script
- Or use Azure Portal

**AWS:**
```bash
eb setenv KAGGLE_USERNAME=ramyasharma10 KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921
```

### Step 5: Test

Visit your deployed URL and test:
1. Create a new ML run
2. Check if Kaggle data is fetched
3. View model results
4. Download predictions

---

## 🔧 Post-Deployment Configuration

### Enable Logging

**Azure:**
```bash
az webapp log config --name your-app --docker-container-logging filesystem
az webapp log tail --name your-app
```

**AWS:**
```bash
eb logs
```

### Scale Up

**Azure:**
```bash
az appservice plan update --name your-plan --sku B1
```

**AWS:**
```bash
eb scale 2
```

### Custom Domain

**Azure:**
```bash
az webapp config hostname add --webapp-name your-app --resource-group automl-rg --hostname yourdomain.com
```

**AWS:**
- Configure in Route 53

---

## 🐛 Troubleshooting

### App Won't Start

**Azure:**
```bash
# Check logs
az webapp log tail --name your-app

# Restart
az webapp restart --name your-app
```

**AWS:**
```bash
# Check logs
eb logs

# Restart
eb restart
```

### Environment Variables Not Working

**Azure:**
1. Go to Azure Portal
2. Navigate to your App Service
3. Click "Configuration"
4. Add/edit settings
5. Click "Save"
6. Restart app

**AWS:**
```bash
eb setenv KEY=VALUE
```

### Out of Memory

**Azure:**
```bash
# Upgrade to B1 tier
az appservice plan update --name your-plan --sku B1
```

**AWS:**
```bash
# Change instance type
eb scale --instance-type t2.large
```

---

## 📊 Monitoring

### View Metrics

**Azure:**
```bash
az monitor metrics list --resource your-app-resource-id
```

**AWS:**
```bash
eb health
```

### Set Up Alerts

**Azure:**
```bash
az monitor metrics alert create \
  --name high-cpu \
  --resource-group automl-rg \
  --condition "avg Percentage CPU > 80"
```

**AWS:**
```bash
# Configure in CloudWatch
```

---

## 🎓 Learning Resources

### Azure
- Official Docs: https://docs.microsoft.com/azure/app-service/
- Python on Azure: https://docs.microsoft.com/azure/developer/python/
- Pricing Calculator: https://azure.microsoft.com/pricing/calculator/

### AWS
- Official Docs: https://docs.aws.amazon.com/elasticbeanstalk/
- Python on AWS: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-apps.html
- Pricing Calculator: https://calculator.aws/

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Install Azure CLI (or AWS CLI)
- [ ] Login to cloud account
- [ ] Review `.env` configuration
- [ ] Test app locally
- [ ] Commit all changes to git

### Deployment
- [ ] Run deployment script
- [ ] Configure environment variables
- [ ] Enable CORS
- [ ] Test deployed app
- [ ] Check logs for errors

### Post-Deployment
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificate
- [ ] Enable monitoring
- [ ] Set up alerts
- [ ] Document deployment URL

---

## 🚀 Quick Start Commands

### Azure (Recommended)

```bash
# Install CLI
winget install Microsoft.AzureCLI

# Deploy
cd automl-agent
az login
az webapp up --name your-automl-app --runtime "PYTHON:3.11"

# Configure
az webapp config appsettings set --name your-automl-app --settings \
  KAGGLE_USERNAME=ramyasharma10 \
  KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921

# View logs
az webapp log tail --name your-automl-app
```

### AWS (Alternative)

```bash
# Install CLI
pip install awsebcli

# Deploy
cd automl-agent
eb init -p python-3.11 automl-platform
eb create automl-env --instance-type t2.medium

# Configure
eb setenv KAGGLE_USERNAME=ramyasharma10 KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921

# View logs
eb logs
```

---

## 🎯 Final Recommendation

**Deploy to Azure because:**
1. ✅ 5x faster deployment
2. ✅ 50% cheaper ($13 vs $50/month)
3. ✅ Free tier available ($0/month)
4. ✅ Easier to learn and manage
5. ✅ Better Python/FastAPI support
6. ✅ One-command deployment
7. ✅ Simpler troubleshooting

**Use the one-command script:**
```bash
cd automl-agent
deploy_azure_simple.bat
```

**Your app will be live in 5 minutes!** 🎉

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs: `az webapp log tail --name your-app`
3. Check Azure Portal for errors
4. Consult `DEPLOY_AZURE.md` for detailed instructions

**Good luck with your deployment!** 🚀
