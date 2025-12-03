# 🔧 Fix Azure Quota Issue - Deploy with B1 Tier

## Problem
Your Azure for Students subscription has quota limit of 0 for Free (F1) VMs.

## Solution: Use B1 Basic Tier (Included in $100 Credit)

The B1 tier costs ~$13/month but you have $100 free credit, so it's effectively free for ~7 months.

---

## Option 1: Deploy with B1 Tier (Recommended)

```cmd
cd D:\Auto_Agent\AutoML-Agent-

az webapp up ^
  --name automl-harsh ^
  --resource-group automl-rg ^
  --location eastus ^
  --runtime "PYTHON:3.11" ^
  --sku B1 ^
  --logs
```

Then configure environment variables:
```cmd
az webapp config appsettings set ^
  --name automl-harsh ^
  --resource-group automl-rg ^
  --settings ^
    APP_ENV=production ^
    LOG_LEVEL=info ^
    KAGGLE_USERNAME=harsh83022 ^
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a ^
    LLM_MODE=none ^
    SYNTHETIC_DEFAULT_ROWS=1000
```

---

## Option 2: Use Azure Container Instances (No Quota Limits)

This is better for ML workloads and has no quota restrictions.

### Step 1: Create Container Registry
```cmd
az acr create ^
  --resource-group automl-rg ^
  --name automlharsh ^
  --sku Basic ^
  --location eastus
```

### Step 2: Build and Push Docker Image
```cmd
cd D:\Auto_Agent\AutoML-Agent-

az acr build ^
  --registry automlharsh ^
  --image automl-app:latest ^
  .
```

### Step 3: Get Registry Credentials
```cmd
az acr credential show --name automlharsh
```

### Step 4: Deploy Container
```cmd
az container create ^
  --resource-group automl-rg ^
  --name automl-container ^
  --image automlharsh.azurecr.io/automl-app:latest ^
  --cpu 2 ^
  --memory 4 ^
  --registry-login-server automlharsh.azurecr.io ^
  --registry-username automlharsh ^
  --registry-password [PASSWORD_FROM_STEP_3] ^
  --dns-name-label automl-harsh ^
  --ports 8000 ^
  --environment-variables ^
    PORT=8000 ^
    APP_ENV=production ^
    KAGGLE_USERNAME=harsh83022 ^
    KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a ^
    LLM_MODE=none ^
    SYNTHETIC_DEFAULT_ROWS=1000
```

Your app will be at: `http://automl-harsh.eastus.azurecontainer.io:8000`

---

## Option 3: Request Quota Increase (Takes 1-2 days)

1. Go to Azure Portal: https://portal.azure.com
2. Search for "Quotas"
3. Select "Compute"
4. Find "Free VMs" quota
5. Click "Request increase"
6. Request at least 1 Free VM
7. Wait for approval (usually 1-2 business days)

---

## Option 4: Use Railway (No Quota Issues)

Since Railway is already connected to your GitHub and has no quota limits:

1. Go to Railway dashboard: https://railway.app/dashboard
2. Your project should auto-deploy from the latest push
3. Check deployment logs
4. The PORT issue should be fixed with the `start.py` script

---

## Recommended: Option 1 (B1 Tier)

This is the easiest and fastest solution:

```cmd
cd D:\Auto_Agent\AutoML-Agent-

REM Deploy with B1 tier
az webapp up --name automl-harsh --resource-group automl-rg --location eastus --runtime "PYTHON:3.11" --sku B1 --logs

REM Configure environment
az webapp config appsettings set --name automl-harsh --resource-group automl-rg --settings APP_ENV=production LOG_LEVEL=info KAGGLE_USERNAME=harsh83022 KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a LLM_MODE=none SYNTHETIC_DEFAULT_ROWS=1000

REM Enable CORS
az webapp cors add --name automl-harsh --resource-group automl-rg --allowed-origins *
```

**Cost**: ~$13/month, but covered by your $100 credit for 7+ months

**Your app will be at**: `https://automl-harsh.azurewebsites.net`

---

## Check Your Credit Balance

```cmd
az consumption usage list --subscription 2fba2292-ebbf-41c2-9ced-3cff488ae048
```

Or check in Azure Portal:
https://portal.azure.com → Cost Management → Credits

---

## Which Option Should You Choose?

| Option | Time | Cost | Difficulty | Best For |
|--------|------|------|------------|----------|
| **B1 Tier** | 10 min | $13/mo (free credit) | Easy | Quick deployment |
| **Container Instances** | 20 min | ~$30/mo (free credit) | Medium | ML workloads |
| **Quota Increase** | 1-2 days | Free | Easy | If you want F1 |
| **Railway** | 5 min | $5/mo | Easy | Fastest option |

**My Recommendation**: Use **B1 Tier** (Option 1) - it's fast, easy, and covered by your credit.

---

## Need Help?

Run this command and let me know the output:
```cmd
az account show
```

This will confirm your subscription is active and ready.
