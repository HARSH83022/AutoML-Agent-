#!/bin/bash

# 🔵 Simple Azure Deployment Script for AutoML Platform
# This script deploys your AutoML platform to Azure in one command

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🚀 AutoML Platform - Azure Deployment                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
APP_NAME="${1:-automl-platform-$(date +%s)}"
RESOURCE_GROUP="automl-rg"
LOCATION="eastus"
RUNTIME="PYTHON:3.11"

echo "📋 Configuration:"
echo "   App Name: $APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Runtime: $RUNTIME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found!"
    echo "   Install from: https://aka.ms/installazurecliwindows"
    exit 1
fi

echo "✅ Azure CLI found"

# Check if logged in
echo "🔐 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "   Please login to Azure..."
    az login
fi

echo "✅ Logged in to Azure"
echo ""

# Navigate to app directory
cd "$(dirname "$0")"

echo "📦 Deploying application..."
echo ""

# Deploy using az webapp up (simplest method)
az webapp up \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --runtime "$RUNTIME" \
  --sku F1 \
  --logs

echo ""
echo "⚙️  Configuring environment variables..."

# Set environment variables
az webapp config appsettings set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --settings \
    APP_ENV=production \
    LOG_LEVEL=info \
    KAGGLE_USERNAME=ramyasharma10 \
    KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 \
    LLM_MODE=ollama \
    OLLAMA_URL=http://localhost:11434/api/generate \
  --output none

echo "✅ Environment variables configured"
echo ""

# Enable CORS
echo "🌐 Enabling CORS..."
az webapp cors add \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --allowed-origins '*' \
  --output none

echo "✅ CORS enabled"
echo ""

# Get the URL
APP_URL=$(az webapp show \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query defaultHostName \
  --output tsv)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   ✅ DEPLOYMENT SUCCESSFUL!                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your AutoML Platform is live at:"
echo "   https://$APP_URL"
echo ""
echo "📊 View logs:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🔧 Manage your app:"
echo "   https://portal.azure.com"
echo ""
echo "🎉 Happy AutoML-ing!"
