# 🚀 Deploy Your AutoML Platform

## 🏆 **Azure is Easier - Deploy in 5 Minutes!**

---

## ⚡ Quick Deploy (Windows)

```bash
cd automl-agent
deploy_azure_simple.bat
```

**That's it!** Your app will be live at `https://your-app.azurewebsites.net`

---

## 📊 Why Azure?

| Feature | Azure | AWS |
|---------|-------|-----|
| Setup Time | **5 min** | 30-60 min |
| Cost (Free) | **$0/month** | Not available |
| Cost (Prod) | **$13/month** | $50/month |
| Difficulty | **⭐ Easy** | ⭐⭐⭐⭐ Hard |
| Commands | **3** | 10+ |

**Azure is 5x faster and 50% cheaper!** ✅

---

## 📁 Deployment Guides

1. **DEPLOYMENT_GUIDE.md** - Start here! Complete overview
2. **DEPLOY_AZURE.md** - Detailed Azure instructions (recommended)
3. **DEPLOY_AWS.md** - Detailed AWS instructions (if needed)
4. **DEPLOYMENT_COMPARISON.md** - Full Azure vs AWS comparison

---

## 🎯 Three Ways to Deploy

### 1. One-Command Script (Easiest)

```bash
cd automl-agent
deploy_azure_simple.bat
```

### 2. Azure CLI (Simple)

```bash
az login
cd automl-agent
az webapp up --name your-automl-app --runtime "PYTHON:3.11"
```

### 3. AWS (Complex)

```bash
pip install awsebcli
cd automl-agent
eb init -p python-3.11 automl-platform
eb create automl-env
```

---

## 💰 Pricing

### Azure (Recommended)
- **Free Tier**: $0/month (perfect for testing)
- **Production**: $13/month (B1 tier)
- **High Performance**: $70/month (S1 tier)

### AWS
- **Minimum**: $50-60/month (no free tier)
- **Production**: $100+/month

**Azure saves you $37-47/month!** 💰

---

## ✅ What's Included

Your deployment includes:
- ✅ Backend API (FastAPI)
- ✅ Frontend (React)
- ✅ Database (SQLite)
- ✅ Kaggle integration
- ✅ AutoML engine (FLAML)
- ✅ Logging and monitoring
- ✅ Environment variables
- ✅ CORS configuration

---

## 🔧 Quick Commands

### Deploy
```bash
deploy_azure_simple.bat
```

### View Logs
```bash
az webapp log tail --name your-app
```

### Restart
```bash
az webapp restart --name your-app
```

### Scale Up
```bash
az appservice plan update --name your-plan --sku B1
```

---

## 📚 Next Steps

1. **Deploy**: Run `deploy_azure_simple.bat`
2. **Test**: Visit your deployed URL
3. **Configure**: Add custom domain (optional)
4. **Monitor**: Set up alerts
5. **Scale**: Upgrade tier as needed

---

## 🎉 Get Started Now!

```bash
# Install Azure CLI
winget install Microsoft.AzureCLI

# Deploy your app
cd automl-agent
deploy_azure_simple.bat
```

**Your AutoML platform will be live in 5 minutes!** 🚀

---

## 📞 Need Help?

- **Detailed Guide**: See `DEPLOYMENT_GUIDE.md`
- **Azure Specific**: See `DEPLOY_AZURE.md`
- **AWS Alternative**: See `DEPLOY_AWS.md`
- **Comparison**: See `DEPLOYMENT_COMPARISON.md`

**Happy deploying!** 🎊
