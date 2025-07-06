# Deployment Guide

This guide covers deploying the Design Gallery FastAPI backend to various platforms, with detailed instructions for Render (recommended), Docker, and other cloud providers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Render Deployment (Recommended)](#render-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Alternative Platforms](#alternative-platforms)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Storage Setup](#storage-setup)
8. [Production Considerations](#production-considerations)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

- **Cloudflare Account** with:
  - D1 database created
  - R2 bucket created
  - API token with D1 and R2 permissions
- **GitHub Repository** with your code
- **Deployment Platform Account** (Render, Railway, etc.)
- **Domain Name** (optional, for custom domain)

## Render Deployment

Render is the recommended platform for its simplicity and excellent support for Python applications.

### Step 1: Prepare Your Repository

1. **Ensure files are in place:**
   ```
   backend/
   ├── app/
   ├── requirements.txt
   ├── render.yaml
   ├── .env.example
   └── README.md
   ```

2. **Verify render.yaml configuration:**
   ```yaml
   services:
     - type: web
       name: design-gallery-api
       env: python
       plan: starter
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
       healthCheckPath: /health
       autoDeploy: true
   ```

### Step 2: Create Render Service

1. **Connect Repository:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository and branch

2. **Configure Service:**
   - **Name**: `design-gallery-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: Start with "Starter" plan

### Step 3: Configure Environment Variables

In Render dashboard, add these environment variables:

#### Required Variables
```
ENVIRONMENT=production
DEBUG=false
JWT_SECRET=your-super-secret-jwt-key-32-chars-minimum
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
CLOUDFLARE_D1_DATABASE_ID=your-d1-database-id
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
CLOUDFLARE_R2_ACCOUNT_ID=your-r2-account-id
CLOUDFLARE_R2_ACCESS_KEY=your-r2-access-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret-key
CLOUDFLARE_R2_BUCKET_NAME=your-bucket-name
CLOUDFLARE_R2_PUBLIC_URL=https://pub-your-account-id.r2.dev
```

#### Optional Variables
```
CORS_ORIGINS=https://yourapp.com,https://api.yourapp.com
MAX_FILE_SIZE=10485760
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Monitor the build logs for any errors
4. Access your API at the provided Render URL

### Step 5: Verify Deployment

Test your deployment:

```bash
# Health check
curl https://your-app.onrender.com/health

# API info
curl https://your-app.onrender.com/info

# API documentation (if debug enabled)
curl https://your-app.onrender.com/docs
```

## Docker Deployment

For containerized deployments, use the provided Dockerfile.

### Build Image

```bash
# Build the Docker image
docker build -t design-gallery-api .

# Tag for registry
docker tag design-gallery-api your-registry/design-gallery-api:latest
```

### Run Locally

```bash
# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Run container
docker run -p 8000:8000 --env-file .env design-gallery-api
```

### Deploy to Container Registry

```bash
# Push to Docker Hub
docker push your-registry/design-gallery-api:latest

# Or push to GitHub Container Registry
docker tag design-gallery-api ghcr.io/username/design-gallery-api:latest
docker push ghcr.io/username/design-gallery-api:latest
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DEBUG=true
    volumes:
      - ./app:/app/app
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

## Alternative Platforms

### Railway

1. **Connect repository** to Railway
2. **Set environment variables** in Railway dashboard
3. **Deploy** using Railway's Python buildpack

```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
```

### Fly.io

1. **Install flyctl** CLI
2. **Initialize Fly app:**
   ```bash
   fly launch
   ```
3. **Configure fly.toml:**
   ```toml
   [build]
   dockerfile = "Dockerfile"

   [[services]]
   http_checks = []
   internal_port = 8000
   protocol = "tcp"
   
   [services.concurrency]
   hard_limit = 25
   soft_limit = 20
   ```

### Google Cloud Run

1. **Build and push image:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/design-gallery-api
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy --image gcr.io/PROJECT-ID/design-gallery-api --platform managed
   ```

### AWS ECS/Fargate

1. **Create task definition** with your Docker image
2. **Configure environment variables** in task definition
3. **Create ECS service** with load balancer
4. **Set up CloudWatch** for logging

## Environment Configuration

### Production Environment Variables

```bash
# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME="Design Gallery API"
APP_VERSION="1.0.0"

# Security
JWT_SECRET=your-super-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# Cloudflare D1
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_D1_DATABASE_ID=your-database-id
CLOUDFLARE_API_TOKEN=your-api-token

# Cloudflare R2
CLOUDFLARE_R2_ACCOUNT_ID=your-r2-account-id
CLOUDFLARE_R2_ACCESS_KEY=your-access-key
CLOUDFLARE_R2_SECRET_KEY=your-secret-key
CLOUDFLARE_R2_BUCKET_NAME=design-gallery-images
CLOUDFLARE_R2_PUBLIC_URL=https://pub-your-account-id.r2.dev

# CORS (comma-separated)
CORS_ORIGINS=https://yourapp.com,https://admin.yourapp.com

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=["image/jpeg","image/png","image/webp"]

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Environment Variable Security

- **Never commit** `.env` files to version control
- **Use secrets management** in production platforms
- **Rotate secrets** regularly
- **Use least privilege** for API tokens

## Database Setup

### Cloudflare D1 Configuration

1. **Create D1 Database:**
   ```bash
   wrangler d1 create design-gallery-db
   ```

2. **Get Database ID:**
   ```bash
   wrangler d1 list
   ```

3. **Run Schema:**
   ```bash
   wrangler d1 execute design-gallery-db --file=schema.sql
   ```

4. **Verify Setup:**
   ```bash
   wrangler d1 execute design-gallery-db --command="SELECT name FROM sqlite_master WHERE type='table';"
   ```

### Database Schema Migration

For schema updates:

1. **Create migration script:**
   ```sql
   -- migration-001.sql
   ALTER TABLE designs ADD COLUMN new_field TEXT;
   ```

2. **Test migration locally:**
   ```bash
   wrangler d1 execute design-gallery-db --local --file=migration-001.sql
   ```

3. **Apply to production:**
   ```bash
   wrangler d1 execute design-gallery-db --file=migration-001.sql
   ```

## Storage Setup

### Cloudflare R2 Configuration

1. **Create R2 Bucket:**
   ```bash
   wrangler r2 bucket create design-gallery-images
   ```

2. **Configure CORS (optional):**
   ```json
   {
     "CORSRules": [
       {
         "AllowedOrigins": ["https://yourapp.com"],
         "AllowedMethods": ["GET", "PUT", "POST"],
         "AllowedHeaders": ["*"]
       }
     ]
   }
   ```

3. **Set up public access:**
   - Enable public read access in R2 dashboard
   - Configure custom domain (optional)

### R2 API Keys

1. **Create R2 API keys** in Cloudflare dashboard
2. **Set permissions** for your bucket
3. **Store securely** in environment variables

## Production Considerations

### Performance Optimization

1. **Worker Configuration:**
   ```bash
   # Gunicorn with multiple workers
   gunicorn app.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --max-requests 1000 \
     --max-requests-jitter 100 \
     --timeout 30
   ```

2. **Resource Limits:**
   - Set appropriate memory limits
   - Configure CPU allocation
   - Monitor resource usage

### Security Hardening

1. **HTTPS Only:**
   - Force HTTPS redirects
   - Set secure headers
   - Use HSTS

2. **CORS Configuration:**
   ```python
   CORS_ORIGINS=["https://yourapp.com", "https://admin.yourapp.com"]
   CORS_ALLOW_CREDENTIALS=true
   ```

3. **Rate Limiting:**
   - Implement rate limiting
   - Monitor for abuse
   - Set up alerting

### Logging and Monitoring

1. **Structured Logging:**
   ```python
   import logging
   import json

   formatter = logging.Formatter(
       '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
   )
   ```

2. **Health Checks:**
   - Configure platform health checks
   - Monitor database connectivity
   - Check external service dependencies

3. **Error Tracking:**
   - Integrate with Sentry or similar
   - Set up error alerting
   - Monitor error rates

### Backup and Recovery

1. **Database Backups:**
   - Regular D1 exports
   - Test restore procedures
   - Document recovery process

2. **File Storage:**
   - R2 versioning enabled
   - Cross-region replication
   - Regular backup verification

## Monitoring and Maintenance

### Application Monitoring

1. **Key Metrics:**
   - Response times
   - Error rates
   - Request volume
   - Database query performance

2. **Alerting:**
   - High error rates
   - Slow response times
   - Service downtime
   - Resource usage spikes

3. **Logging:**
   - Request/response logging
   - Error tracking
   - Performance metrics
   - Security events

### Maintenance Tasks

1. **Regular Updates:**
   - Security patches
   - Dependency updates
   - Performance optimizations

2. **Data Cleanup:**
   - Remove old logs
   - Clean up unused files
   - Archive old data

3. **Performance Tuning:**
   - Query optimization
   - Caching strategies
   - Resource scaling

## Troubleshooting

### Common Issues

#### Build Failures

```bash
# Check Python version
python --version

# Verify requirements.txt
pip install -r requirements.txt

# Check for missing dependencies
pip check
```

#### Runtime Errors

```bash
# Check logs
docker logs container-name

# Verify environment variables
env | grep CLOUDFLARE

# Test database connection
python -c "from app.core.database import db_manager; print('DB OK')"
```

#### Performance Issues

1. **Check resource usage:**
   - CPU utilization
   - Memory consumption
   - Database query times

2. **Optimize queries:**
   - Add database indexes
   - Implement caching
   - Optimize N+1 queries

#### Storage Issues

1. **R2 Connection:**
   ```python
   # Test R2 connectivity
   from app.core.storage import storage_manager
   result = storage_manager.list_files(max_keys=1)
   print(f"R2 connection: {'OK' if result else 'Failed'}")
   ```

2. **Upload Failures:**
   - Check file size limits
   - Verify content types
   - Check R2 permissions

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Environment variable
DEBUG=true

# Check debug endpoints
curl https://your-app.com/docs
curl https://your-app.com/info
```

### Log Analysis

```bash
# Filter error logs
grep "ERROR" application.log

# Check API performance
grep "Response:" application.log | grep -E "([5-9][0-9]{2,}ms|[0-9]+\.[0-9]+s)"

# Monitor authentication
grep "auth" application.log
```

### Getting Help

1. **Check documentation**
2. **Review error logs**
3. **Test with minimal configuration**
4. **Contact platform support**
5. **Create GitHub issue** with:
   - Error logs
   - Configuration (sanitized)
   - Steps to reproduce

## Deployment Checklist

Before going live:

- [ ] Environment variables configured
- [ ] Database schema deployed
- [ ] R2 bucket configured and accessible
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Authentication working
- [ ] File uploads functional
- [ ] Admin features tested
- [ ] Error handling verified
- [ ] Monitoring configured
- [ ] Backup procedures in place
- [ ] SSL certificate configured
- [ ] Custom domain configured (if applicable)
- [ ] Performance testing completed
- [ ] Security review completed

## Post-Deployment

After successful deployment:

1. **Test all endpoints**
2. **Verify monitoring**
3. **Set up alerting**
4. **Document any customizations**
5. **Train team on monitoring tools**
6. **Schedule regular maintenance** 