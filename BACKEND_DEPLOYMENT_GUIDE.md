# Backend Deployment Guide - Step by Step

## 📋 **ANALYSIS & DOCUMENT PRIORITY**

### **Which Document to Follow First:**
1. **START HERE** ➜ This document (complete step-by-step process)
2. **REFERENCE** ➜ `backend/docs/DEPLOYMENT_GUIDE.md` (detailed technical reference)
3. **BACKUP** ➜ `COMPREHENSIVE_PROJECT_GUIDE.md` (full project context)

### **Current Project Status:**
- ✅ **Backend Code**: 100% Complete (FastAPI with comprehensive APIs)
- ✅ **Database Schema**: Ready (`backend/schema.sql`)
- ✅ **Deployment Config**: Ready (`backend/render.yaml`)
- ✅ **Documentation**: Comprehensive and up-to-date
- ⏳ **Infrastructure**: Needs setup (Cloudflare D1 + R2)
- ⏳ **Deployment**: Needs execution (Render platform)

---

## 🎯 **DEPLOYMENT OVERVIEW**

### **Technology Stack:**
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Cloudflare D1 (SQLite-based)
- **Storage**: Cloudflare R2 (S3-compatible)
- **Deployment**: Render (Cloud platform)
- **Authentication**: JWT with bcrypt

### **Architecture:**
```
React Native App → Render (FastAPI) → Cloudflare D1 (Database)
                                   → Cloudflare R2 (Images)
```

---

## 🚀 **STEP-BY-STEP DEPLOYMENT**

### **PHASE 1: CLOUDFLARE SETUP** (30 minutes)

#### **Step 1.1: Create Cloudflare D1 Database**
```bash
# Install Wrangler CLI (if not installed)
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create D1 database
wrangler d1 create design-gallery-db
```

**Expected Output:**
```
✅ Successfully created DB 'design-gallery-db'!

[[d1_databases]]
binding = "DB"
database_name = "design-gallery-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**⚠️ IMPORTANT:** Copy the `database_id` - you'll need it for environment variables.

#### **Step 1.2: Setup Database Schema**
```bash
# Navigate to backend directory
cd backend

# Run the database schema
wrangler d1 execute design-gallery-db --file=schema.sql
```

**Verify Database:**
```bash
# Check tables were created
wrangler d1 execute design-gallery-db --command="SELECT name FROM sqlite_master WHERE type='table';"
```

#### **Step 1.3: Create Cloudflare R2 Bucket**
```bash
# Create R2 bucket for image storage
wrangler r2 bucket create design-gallery-images
```

#### **Step 1.4: Generate API Token**
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
2. Click "Create Token"
3. Use "Custom token" template
4. **Permissions:**
   - `Cloudflare D1:Edit`
   - `Cloudflare R2:Edit`
5. **Account Resources:** Include All accounts
6. **Zone Resources:** Include All zones
7. Click "Continue to summary" → "Create Token"

**⚠️ IMPORTANT:** Copy the API token - you'll need it for deployment.

#### **Step 1.5: Get Your Account Information**
```bash
# Get account ID
wrangler whoami

# Get R2 credentials
# Go to R2 dashboard → Manage R2 API tokens → Create API token
```

**You need these values:**
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_D1_DATABASE_ID` (from Step 1.1)
- `CLOUDFLARE_API_TOKEN` (from Step 1.4)
- `CLOUDFLARE_R2_ACCOUNT_ID` (same as account ID)
- `CLOUDFLARE_R2_ACCESS_KEY` (from R2 API token)
- `CLOUDFLARE_R2_SECRET_KEY` (from R2 API token)

---

### **PHASE 2: RENDER DEPLOYMENT** (20 minutes)

#### **Step 2.1: Prepare Repository**
Ensure your repository has these files:
```
backend/
├── app/                 # ✅ FastAPI application
├── requirements.txt     # ✅ Python dependencies
├── render.yaml         # ✅ Deployment configuration
├── schema.sql          # ✅ Database schema
├── Dockerfile          # ✅ Container configuration
└── docs/              # ✅ Documentation
```

#### **Step 2.2: Create Render Account**
1. Go to [Render](https://render.com)
2. Sign up/login with GitHub
3. Connect your GitHub account

#### **Step 2.3: Deploy Web Service**
1. **Create New Web Service:**
   - Dashboard → "New" → "Web Service"
   - Connect your repository
   - Select branch (usually `main`)

2. **Configure Service:**
   - **Name**: `design-gallery-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: Start with "Starter" ($7/month)

#### **Step 2.4: Configure Environment Variables**
In Render dashboard, add these environment variables:

**Required Variables:**
```bash
# Application Settings
ENVIRONMENT=production
DEBUG=false
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters-long

# Cloudflare D1
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
CLOUDFLARE_D1_DATABASE_ID=your-d1-database-id
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token

# Cloudflare R2
CLOUDFLARE_R2_ACCOUNT_ID=your-r2-account-id
CLOUDFLARE_R2_ACCESS_KEY=your-r2-access-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret-key
CLOUDFLARE_R2_BUCKET_NAME=design-gallery-images
CLOUDFLARE_R2_PUBLIC_URL=https://pub-your-account-id.r2.dev
```

**Optional Variables:**
```bash
CORS_ORIGINS=*
MAX_FILE_SIZE=10485760
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

#### **Step 2.5: Deploy**
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Monitor the build logs
4. Wait for deployment to complete

---

### **PHASE 3: VERIFICATION & TESTING** (15 minutes)

#### **Step 3.1: Test Health Check**
```bash
# Replace with your actual Render URL
curl https://your-app-name.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

#### **Step 3.2: Test API Info**
```bash
curl https://your-app-name.onrender.com/info
```

#### **Step 3.3: Test API Documentation**
Visit: `https://your-app-name.onrender.com/docs`

You should see the interactive API documentation.

#### **Step 3.4: Test User Registration**
```bash
curl -X POST https://your-app-name.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

---

## 🔧 **ENVIRONMENT VARIABLES REFERENCE**

### **Required Variables (Must Set):**
| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET` | JWT signing secret (32+ chars) | `super-secret-jwt-key-32-characters-long` |
| `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare account ID | `abc123def456...` |
| `CLOUDFLARE_D1_DATABASE_ID` | D1 database ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token | `token-from-cloudflare-dashboard` |
| `CLOUDFLARE_R2_ACCOUNT_ID` | R2 account ID (same as account ID) | `abc123def456...` |
| `CLOUDFLARE_R2_ACCESS_KEY` | R2 access key | `r2-access-key` |
| `CLOUDFLARE_R2_SECRET_KEY` | R2 secret key | `r2-secret-key` |
| `CLOUDFLARE_R2_BUCKET_NAME` | R2 bucket name | `design-gallery-images` |
| `CLOUDFLARE_R2_PUBLIC_URL` | R2 public URL | `https://pub-account-id.r2.dev` |

### **Optional Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Environment name |
| `DEBUG` | `false` | Debug mode |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `MAX_FILE_SIZE` | `10485760` | Max file size (10MB) |

---

## 📝 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment:**
- [ ] Repository pushed to GitHub
- [ ] Cloudflare account created
- [ ] D1 database created and schema applied
- [ ] R2 bucket created
- [ ] API token generated with proper permissions
- [ ] Render account created

### **During Deployment:**
- [ ] Render service created
- [ ] Environment variables configured
- [ ] Build completed successfully
- [ ] Service started without errors

### **Post-Deployment:**
- [ ] Health check endpoint working
- [ ] API documentation accessible
- [ ] User registration working
- [ ] Database queries working
- [ ] File upload working (if testing)

---

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: Build Fails**
**Error:** `Module not found` or dependency issues
**Solution:**
```bash
# Check requirements.txt exists
cat backend/requirements.txt

# Verify Python version
python --version  # Should be 3.11+
```

### **Issue 2: Database Connection Error**
**Error:** `Failed to connect to D1 database`
**Solution:**
- Verify `CLOUDFLARE_D1_DATABASE_ID` is correct
- Check API token has D1 permissions
- Ensure schema.sql was applied

### **Issue 3: R2 Storage Error**
**Error:** `R2 bucket not accessible`
**Solution:**
- Verify R2 credentials are correct
- Check bucket name matches environment variable
- Ensure API token has R2 permissions

### **Issue 4: JWT Secret Error**
**Error:** `JWT_SECRET too short`
**Solution:**
- Use a secret key with at least 32 characters
- Generate with: `openssl rand -hex 32`

---

## 🎯 **NEXT STEPS AFTER DEPLOYMENT**

### **Immediate Actions:**
1. **Test all endpoints** using the API documentation
2. **Create admin user** through the API
3. **Upload test images** to verify R2 integration
4. **Set up monitoring** (optional)

### **For Frontend Integration:**
1. **Copy your API URL** from Render dashboard
2. **Update frontend configuration** with the API URL
3. **Test authentication** from the mobile app

### **Production Readiness:**
1. **Set up custom domain** (optional)
2. **Configure SSL certificate** (automatic with Render)
3. **Set up backup procedures**
4. **Configure monitoring and alerting**

---

## 🔗 **USEFUL LINKS**

- **Render Dashboard**: https://dashboard.render.com
- **Cloudflare Dashboard**: https://dash.cloudflare.com
- **API Documentation**: `https://your-app.onrender.com/docs`
- **Health Check**: `https://your-app.onrender.com/health`

---

## 💡 **TIPS FOR SUCCESS**

1. **Start Small**: Deploy with minimal configuration first
2. **Test Locally**: Run `python -m app.main` locally before deploying
3. **Monitor Logs**: Use Render dashboard to monitor deployment logs
4. **Environment Variables**: Double-check all environment variables are set
5. **Security**: Use strong secrets and rotate them regularly

---

## 📞 **GETTING HELP**

If you encounter issues:
1. Check the build logs in Render dashboard
2. Review the detailed documentation in `backend/docs/DEPLOYMENT_GUIDE.md`
3. Test individual components (database, storage) separately
4. Verify all environment variables are correctly set

---

**🎉 Once deployed, your API will be live and ready for frontend integration!** 