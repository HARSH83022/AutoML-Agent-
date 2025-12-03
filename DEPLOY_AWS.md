# 🟠 Deploy to AWS (More Complex)

## Prerequisites
- AWS account
- AWS CLI installed: https://aws.amazon.com/cli/
- Docker installed

## Step 1: Install AWS CLI

**Windows:**
```bash
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

**Or download from:** https://aws.amazon.com/cli/

## Step 2: Configure AWS

```bash
aws configure
```

Enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

## Step 3: Deploy Using Elastic Beanstalk (Easier)

### Install EB CLI

```bash
pip install awsebcli
```

### Initialize and Deploy

```bash
cd automl-agent

# Initialize Elastic Beanstalk
eb init -p python-3.11 automl-platform --region us-east-1

# Create environment and deploy
eb create automl-env --instance-type t2.medium

# Set environment variables
eb setenv \
  KAGGLE_USERNAME=ramyasharma10 \
  KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 \
  APP_ENV=production \
  LLM_MODE=ollama

# Open in browser
eb open
```

### Update Deployment

```bash
# After making changes
eb deploy
```

---

## Step 4: Deploy Using ECS (Docker - More Control)

### Create ECR Repository

```bash
# Create repository
aws ecr create-repository --repository-name automl-app --region us-east-1

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### Build and Push Docker Image

```bash
cd automl-agent

# Build image
docker build -t automl-app .

# Tag image
docker tag automl-app:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/automl-app:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/automl-app:latest
```

### Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name automl-cluster --region us-east-1

# Create task definition (see task-definition.json below)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster automl-cluster \
  --service-name automl-service \
  --task-definition automl-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

### task-definition.json

```json
{
  "family": "automl-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "automl-container",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/automl-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KAGGLE_USERNAME",
          "value": "ramyasharma10"
        },
        {
          "name": "KAGGLE_KEY",
          "value": "820ef1deeb71e11c4494e16cd071e921"
        },
        {
          "name": "APP_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/automl",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## Step 5: Deploy Frontend to S3 + CloudFront

### Build Frontend

```bash
cd automl-agent/frontend
npm run build
```

### Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://your-automl-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://your-automl-frontend --index-document index.html --error-document index.html

# Upload files
aws s3 sync dist/ s3://your-automl-frontend --acl public-read

# Set bucket policy
aws s3api put-bucket-policy --bucket your-automl-frontend --policy file://bucket-policy.json
```

### bucket-policy.json

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-automl-frontend/*"
    }
  ]
}
```

### Create CloudFront Distribution (Optional - for HTTPS)

```bash
aws cloudfront create-distribution --origin-domain-name your-automl-frontend.s3-website-us-east-1.amazonaws.com
```

---

## Step 6: Set Up Load Balancer (for ECS)

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name automl-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx \
  --scheme internet-facing \
  --type application

# Create target group
aws elbv2 create-target-group \
  --name automl-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --target-type ip

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## 💰 Cost Estimate

**Elastic Beanstalk:**
- EC2 t2.medium: ~$35/month
- Load Balancer: ~$20/month
- **Total: ~$55/month**

**ECS Fargate:**
- Fargate (1 vCPU, 2GB): ~$30/month
- Load Balancer: ~$20/month
- **Total: ~$50/month**

**S3 + CloudFront:**
- S3 storage: ~$1/month
- CloudFront: ~$1/month (low traffic)
- **Total: ~$2/month**

**Grand Total: ~$52-57/month**

---

## 🚀 Quick Deploy Script (Elastic Beanstalk)

Create `deploy_aws.sh`:

```bash
#!/bin/bash

echo "🚀 Deploying AutoML Platform to AWS..."

cd automl-agent

# Initialize EB
eb init -p python-3.11 automl-platform --region us-east-1

# Create environment
eb create automl-env --instance-type t2.medium

# Set environment variables
eb setenv \
  KAGGLE_USERNAME=ramyasharma10 \
  KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921 \
  APP_ENV=production

echo "✅ Deployment complete!"
eb open
```

Run:
```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

---

## 🔍 Troubleshooting

### Check Logs (Elastic Beanstalk)
```bash
eb logs
```

### Check Logs (ECS)
```bash
aws logs tail /ecs/automl --follow
```

### Update Environment Variables
```bash
eb setenv KEY=VALUE
```

### Restart Application
```bash
eb restart
```

---

## 📊 Monitoring

### CloudWatch Logs
```bash
# View logs
aws logs tail /aws/elasticbeanstalk/automl-env --follow

# Create alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## ⚠️ AWS is More Complex

**Challenges:**
- More services to configure (VPC, subnets, security groups)
- Higher costs
- Steeper learning curve
- More maintenance required

**Recommendation: Use Azure instead for easier deployment!**

---

## 🎯 AWS vs Azure Comparison

| Feature | AWS | Azure |
|---------|-----|-------|
| **Ease of Setup** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost** | $50-60/month | $13-30/month |
| **Python Support** | Good | Excellent |
| **ML Support** | Excellent | Excellent |
| **Learning Curve** | Steep | Gentle |
| **Free Tier** | Limited | Better |

**Winner: Azure** ✅
