# 🔵 Deploy to Azure App Service (EASIEST)

## Prerequisites
- Azure account (free tier available)
- Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

## Step 1: Install Azure CLI

**Windows:**
```bash
winget install Microsoft.AzureCLI
```

**Or download from:** https://aka.ms/installazurecliwindows

## Step 2: Login to Azure

```bash
az login
```

This will open your browser for authentication.

## Step 3: Create Deployment Files

Already created! You have:
- `Dockerfile` ✅
- `requirements.txt` ✅
- `.env` configuration ✅

## Step 4: Deploy Backend

### Option A: Using Azure App Service (Recommended)

```bash
cd automl-agent

# Create resource group
az group create --name automl-rg --location eastus

# Create App Service plan (Free tier)
az appservice plan create --name automl-plan --resource-group automl-rg --sku F1 --is-linux

# Create web app
az webapp create --resource-group automl-rg --plan automl-plan --name your-automl-app --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set --resource-group automl-rg --name your-automl-app --settings \
  APP_ENV=production \
  LOG_LEVEL=info \
  LLM_MODE=ollama \
  KAGGLE_USERNAME=ramyasharma10 \
  KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 \
  OLLAMA_URL=http://localhost:11434/api/generate

# Deploy code
az webapp up --resource-group automl-rg --name your-automl-app --runtime "PYTHON:3.11"
```

### Option B: Using Docker Container (Better for ML)

```bash
cd automl-agent

# Build and push to Azure Container Registry
az acr create --resource-group automl-rg --name yourautomlregistry --sku Basic

# Login to registry
az acr login --name yourautomlregistry

# Build and push image
az acr build --registry yourautomlregistry --image automl-app:latest .

# Create container app
az container create \
  --resource-group automl-rg \
  --name automl-container \
  --image yourautomlregistry.azurecr.io/automl-app:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server yourautomlregistry.azurecr.io \
  --registry-username $(az acr credential show --name yourautomlregistry --query username -o tsv) \
  --registry-password $(az acr credential show --name yourautomlregistry --query passwords[0].value -o tsv) \
  --dns-name-label your-automl-app \
  --ports 8000 \
  --environment-variables \
    APP_ENV=production \
    KAGGLE_USERNAME=ramyasharma10 \
    KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921
```

## Step 5: Deploy Frontend

### Option 1: Azure Static Web Apps (Free)

```bash
cd automl-agent/frontend

# Build frontend
npm run build

# Install Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Deploy
az staticwebapp create \
  --name automl-frontend \
  --resource-group automl-rg \
  --source ./dist \
  --location eastus \
  --branch main \
  --app-location "/" \
  --output-location "dist"
```

### Option 2: Same App Service

```bash
# Add frontend to backend deployment
cd automl-agent/frontend
npm run build

# Copy build to backend static folder
mkdir -p ../static
cp -r dist/* ../static/

# Redeploy backend (will serve frontend too)
cd ..
az webapp up --resource-group automl-rg --name your-automl-app
```

## Step 6: Configure CORS

```bash
az webapp cors add --resource-group automl-rg --name your-automl-app --allowed-origins '*'
```

## Step 7: View Your App

```bash
# Get URL
az webapp show --resource-group automl-rg --name your-automl-app --query defaultHostName -o tsv
```

Visit: `https://your-automl-app.azurewebsites.net`

---

## 🔧 Configuration

### Environment Variables in Azure Portal

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to your App Service
3. Click "Configuration" → "Application settings"
4. Add:
   - `KAGGLE_USERNAME` = `ramyasharma10`
   - `KAGGLE_KEY` = `820ef1deeb71e11c4494e16cd071e921`
   - `LLM_MODE` = `ollama` or `none`
   - `APP_ENV` = `production`

### Enable Logging

```bash
az webapp log config --resource-group automl-rg --name your-automl-app --docker-container-logging filesystem
az webapp log tail --resource-group automl-rg --name your-automl-app
```

---

## 💰 Cost Estimate

**Free Tier:**
- App Service: Free (F1 tier)
- Static Web Apps: Free
- **Total: $0/month** (with limitations)

**Production Tier:**
- App Service: ~$13/month (B1 Basic)
- Container Instances: ~$30/month
- Static Web Apps: Free
- **Total: ~$13-30/month**

---

## 🚀 One-Command Deploy Script

Create `deploy_azure.sh`:

```bash
#!/bin/bash

# Configuration
RESOURCE_GROUP="automl-rg"
APP_NAME="your-automl-app"
LOCATION="eastus"

echo "🚀 Deploying AutoML Platform to Azure..."

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create and deploy app
cd automl-agent
az webapp up --resource-group $RESOURCE_GROUP --name $APP_NAME --runtime "PYTHON:3.11" --sku F1

# Configure environment
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings \
  KAGGLE_USERNAME=ramyasharma10 \
  KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 \
  APP_ENV=production

echo "✅ Deployment complete!"
echo "🌐 Your app: https://$APP_NAME.azurewebsites.net"
```

Run:
```bash
chmod +x deploy_azure.sh
./deploy_azure.sh
```

---

## 🔍 Troubleshooting

### App won't start
```bash
# Check logs
az webapp log tail --resource-group automl-rg --name your-automl-app

# Restart app
az webapp restart --resource-group automl-rg --name your-automl-app
```

### Environment variables not working
- Check in Azure Portal → Configuration
- Make sure to restart after changes

### Out of memory
- Upgrade to B1 tier: `az appservice plan update --name automl-plan --resource-group automl-rg --sku B1`

---

## 📊 Monitoring

```bash
# View metrics
az monitor metrics list --resource /subscriptions/{subscription-id}/resourceGroups/automl-rg/providers/Microsoft.Web/sites/your-automl-app

# Set up alerts
az monitor metrics alert create --name high-cpu --resource-group automl-rg --scopes /subscriptions/{subscription-id}/resourceGroups/automl-rg/providers/Microsoft.Web/sites/your-automl-app --condition "avg Percentage CPU > 80"
```

---

## 🎯 Next Steps

1. ✅ Deploy backend to Azure App Service
2. ✅ Deploy frontend to Static Web Apps
3. ✅ Configure custom domain (optional)
4. ✅ Set up CI/CD with GitHub Actions
5. ✅ Enable Application Insights for monitoring

**Azure is the easiest option for your AutoML platform!** 🎉
