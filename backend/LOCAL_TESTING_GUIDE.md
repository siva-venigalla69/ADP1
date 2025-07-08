# Local Testing Guide - Design Gallery FastAPI Backend

## 🎯 **Overview**

This guide provides comprehensive instructions for our **streamlined local testing strategy** before deploying to Render. Our testing approach focuses on:

✅ **Cloudflare R2 Storage** - For image uploads and file management  
✅ **Cloudflare D1 Database** - For data persistence and queries  
✅ **Local FastAPI Development** - For rapid API development and testing  
✅ **Comprehensive API Testing** - Before deploying to Render  

## 🚀 **Our Testing Strategy**

### **Why This Approach?**

1. **🔄 Production Parity**: Using the same D1 database and R2 storage as production
2. **⚡ Fast Development**: Local FastAPI server for quick iteration
3. **🧪 Thorough Testing**: Test all APIs locally before deployment
4. **🚀 Confident Deployment**: Deploy to Render only after complete validation

### **Testing Workflow**
```
Local Development → API Testing → Deploy to Render
      ↓                ↓              ↓
   FastAPI        All Endpoints    Production
   + D1 + R2      Validated        Ready
```

---

## 🔧 **Environment Setup**

### **1. Create Environment File**

Create `.env` file in the `backend/` directory with **Cloudflare-focused** configuration:

```bash
# Application Settings
APP_NAME="Design Gallery API"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG=true

# Security Settings (REQUIRED)
JWT_SECRET="your-super-secret-jwt-key-minimum-32-characters-long-for-testing"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=168

# Cloudflare D1 Database (PRIMARY - REQUIRED)
CLOUDFLARE_ACCOUNT_ID="your-cloudflare-account-id"
CLOUDFLARE_D1_DATABASE_ID="your-d1-database-id"
CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"

# Cloudflare R2 Storage (PRIMARY - REQUIRED)
CLOUDFLARE_R2_ACCOUNT_ID="your-r2-account-id"
CLOUDFLARE_R2_ACCESS_KEY="your-r2-access-key"
CLOUDFLARE_R2_SECRET_KEY="your-r2-secret-key"
CLOUDFLARE_R2_BUCKET_NAME="design-gallery-images-test"
CLOUDFLARE_R2_PUBLIC_URL="https://pub-your-account-id.r2.dev"

# CORS Settings (for local frontend testing)
CORS_ORIGINS="http://localhost:3000,http://localhost:8081,http://localhost:19006"
CORS_ALLOW_CREDENTIALS=true

# File Upload Settings
MAX_FILE_SIZE=10485760  # 10MB
```

### **2. Generate Strong JWT Secret**

```bash
# Generate a secure JWT secret for testing
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🗄️ **Cloudflare D1 Database Setup**

### **Step 1: Install Wrangler CLI**
```bash
# Install Wrangler globally
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

### **Step 2: Create Test Database**
```bash
# Create a dedicated test database
wrangler d1 create design-gallery-test-db

# Copy the database ID from output and add to .env
# CLOUDFLARE_D1_DATABASE_ID="your-test-database-id"
```

### **Step 3: Apply Database Schema**
```bash
# Apply the database schema to your test database
wrangler d1 execute design-gallery-test-db --file=schema.sql

# Verify tables were created successfully
wrangler d1 execute design-gallery-test-db --command="SELECT name FROM sqlite_master WHERE type='table';"
```

### **Step 4: Create Test Data**
```bash
# Create an admin user for testing
wrangler d1 execute design-gallery-test-db --command="
INSERT INTO users (username, password_hash, is_admin, is_approved) 
VALUES ('admin', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewqeJG/mGOFSCy32', 1, 1);
"

# Add sample designs for testing
wrangler d1 execute design-gallery-test-db --command="
INSERT INTO designs (title, description, r2_object_key, category, style, colour, fabric, occasion, featured) 
VALUES 
('Test Saree Collection', 'Beautiful traditional saree for testing', 'test/saree1.jpg', 'saree', 'traditional', 'red', 'silk', 'wedding', 1),
('Test Lehenga Design', 'Elegant party lehenga for testing', 'test/lehenga1.jpg', 'lehenga', 'modern', 'blue', 'cotton', 'party', 0),
('Test Kurti Style', 'Casual daily wear kurti for testing', 'test/kurti1.jpg', 'kurti', 'casual', 'green', 'cotton', 'daily', 0);
"

# Verify test data
wrangler d1 execute design-gallery-test-db --command="SELECT COUNT(*) as total_designs FROM designs;"
```

---

## 🪣 **Cloudflare R2 Storage Setup**

### **Step 1: Create Test Bucket**
```bash
# Create a dedicated test R2 bucket
wrangler r2 bucket create design-gallery-images-test

# Verify bucket creation
wrangler r2 bucket list
```

### **Step 2: Configure R2 API Access**
1. Go to [Cloudflare R2 Dashboard](https://dash.cloudflare.com/profile/api-tokens)
2. Create API token with **R2:Edit** permissions for your test bucket
3. Generate R2 API keys:
   - Account ID
   - Access Key ID  
   - Secret Access Key
4. Add all credentials to your `.env` file

### **Step 3: Test R2 Connection**
```bash
# Test uploading a file
echo "test upload" | wrangler r2 object put design-gallery-images-test/test.txt

# List objects in bucket
wrangler r2 object list design-gallery-images-test

# Delete test object
wrangler r2 object delete design-gallery-images-test/test.txt
```

---

## 🚀 **Local FastAPI Development**

### **Step 1: Python Environment Setup**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Start FastAPI Development Server**
```bash
# Start with hot reload (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Start with Python module
python -m uvicorn app.main:app --reload --port 8000
```

### **Step 3: Verify Local Server**
```bash
# Health check
curl http://localhost:8000/health

# API documentation (open in browser)
# http://localhost:8000/docs

# API info
curl http://localhost:8000/info
```

---

## 🧪 **Comprehensive API Testing Strategy**

### **Phase 1: Core Functionality Testing**

#### **1. Health & Info Endpoints**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test app info
curl http://localhost:8000/info

# Expected: Both should return 200 status
```

#### **2. Authentication Flow**
```bash
# Test admin login (using test data)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Save the access_token for subsequent requests
export TOKEN="your-jwt-token-here"

# Test protected endpoint
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### **Phase 2: Design Management Testing**

#### **1. Design Retrieval**
```bash
# Get all designs
curl http://localhost:8000/api/designs \
  -H "Authorization: Bearer $TOKEN"

# Test filtering
curl "http://localhost:8000/api/designs?category=saree&style=traditional" \
  -H "Authorization: Bearer $TOKEN"

# Test search
curl "http://localhost:8000/api/designs?q=test" \
  -H "Authorization: Bearer $TOKEN"

# Test pagination
curl "http://localhost:8000/api/designs?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### **2. Design Creation & Management**
```bash
# Create new design (admin only)
curl -X POST http://localhost:8000/api/designs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Local Test Design",
    "description": "Testing design creation locally",
    "r2_object_key": "test/local-design.jpg",
    "category": "saree",
    "style": "traditional",
    "colour": "purple",
    "fabric": "silk",
    "occasion": "festival",
    "featured": true
  }'

# Update design
curl -X PUT http://localhost:8000/api/designs/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Test Design",
    "featured": false
  }'
```

### **Phase 3: File Upload Testing**

#### **1. Test Image Upload to R2**
```bash
# Create test image
echo "test image data" > test_image.jpg

# Upload image
curl -X POST http://localhost:8000/api/upload/image \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_image.jpg" \
  -F "category=designs"

# Test presigned URL generation
curl "http://localhost:8000/api/upload/presigned-url?filename=test.jpg&category=designs" \
  -H "Authorization: Bearer $TOKEN"
```

### **Phase 4: Admin Functions Testing**

#### **1. User Management**
```bash
# Get all users
curl http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer $TOKEN"

# Test user registration (from user perspective)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser1",
    "password": "password123"
  }'

# Approve user (admin action)
curl -X POST http://localhost:8000/api/admin/users/2/approve \
  -H "Authorization: Bearer $TOKEN"
```

#### **2. Analytics & Monitoring**
```bash
# Get analytics data
curl http://localhost:8000/api/admin/analytics \
  -H "Authorization: Bearer $TOKEN"

# Get system status
curl http://localhost:8000/api/admin/status \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🤖 **Automated Testing Script**

### **Create Comprehensive Test Script**

```bash
# Create test_all_endpoints.py
cat > test_all_endpoints.py << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive API testing script for Design Gallery backend
Run this to test all endpoints systematically
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USERNAME = "testuser_" + str(int(time.time()))
TEST_PASSWORD = "testpass123"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
    
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     headers: Dict = None, data: Any = None, 
                     expected_status: int = 200) -> bool:
        """Test a single endpoint and record results."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(
                method=method,
                url=url,
                headers=headers or {},
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None
            )
            
            success = response.status_code == expected_status
            result = {
                "test": name,
                "status": "✅ PASS" if success else "❌ FAIL",
                "expected": expected_status,
                "actual": response.status_code,
                "response": response.text[:200] if not success else "OK"
            }
            
            self.test_results.append(result)
            print(f"{result['status']} {name} ({response.status_code})")
            
            return success, response
            
        except Exception as e:
            result = {
                "test": name,
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.test_results.append(result)
            print(f"❌ ERROR {name}: {e}")
            return False, None
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🚀 Starting API Test Suite")
        print(f"Testing API: {self.base_url}")
        print("-" * 50)
        
        # 1. Health checks
        self.test_basic_endpoints()
        
        # 2. Authentication tests
        self.test_authentication()
        
        # 3. Design management tests
        if self.admin_token:
            self.test_design_management()
        
        # 4. Admin function tests
        if self.admin_token:
            self.test_admin_functions()
        
        # 5. Print summary
        self.print_summary()
    
    def test_basic_endpoints(self):
        """Test basic health and info endpoints."""
        print("\n📋 Testing Basic Endpoints...")
        
        self.test_endpoint("Health Check", "GET", "/health")
        self.test_endpoint("App Info", "GET", "/info")
        self.test_endpoint("Root Endpoint", "GET", "/")
    
    def test_authentication(self):
        """Test authentication endpoints."""
        print("\n🔐 Testing Authentication...")
        
        # Test user registration
        success, response = self.test_endpoint(
            "User Registration", "POST", "/api/auth/register",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
        )
        
        # Test admin login
        success, response = self.test_endpoint(
            "Admin Login", "POST", "/api/auth/login",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        
        if success and response:
            data = response.json()
            self.admin_token = data.get("access_token")
            print(f"   🔑 Admin token obtained")
        
        # Test protected endpoint
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.test_endpoint("Get Current User", "GET", "/api/auth/me", headers=headers)
    
    def test_design_management(self):
        """Test design management endpoints."""
        print("\n🎨 Testing Design Management...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # List designs
        self.test_endpoint("List Designs", "GET", "/api/designs", headers=headers)
        
        # Create design
        design_data = {
            "title": "Test API Design",
            "description": "Created via API test",
            "r2_object_key": "test/api-test.jpg",
            "category": "kurti",
            "style": "modern",
            "colour": "purple",
            "fabric": "cotton",
            "occasion": "casual"
        }
        
        success, response = self.test_endpoint(
            "Create Design", "POST", "/api/designs", 
            headers=headers, data=design_data, expected_status=201
        )
        
        # Get design details
        if success and response:
            design = response.json()
            design_id = design.get("id")
            if design_id:
                self.test_endpoint(
                    "Get Design Details", "GET", f"/api/designs/{design_id}", 
                    headers=headers
                )
        
        # Search designs
        self.test_endpoint(
            "Search Designs", "GET", "/api/designs?q=test", 
            headers=headers
        )
        
        # Filter designs
        self.test_endpoint(
            "Filter Designs", "GET", "/api/designs?category=kurti&style=modern", 
            headers=headers
        )
    
    def test_admin_functions(self):
        """Test admin-only functions."""
        print("\n👨‍💼 Testing Admin Functions...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get all users
        self.test_endpoint("List All Users", "GET", "/api/admin/users", headers=headers)
        
        # Get analytics
        self.test_endpoint("Get Analytics", "GET", "/api/admin/analytics", headers=headers)
        
        # Get pending users
        self.test_endpoint("Get Pending Users", "GET", "/api/admin/users/pending", headers=headers)
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*50)
        print("📊 TEST RESULTS SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "✅ PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] != "✅ PASS":
                    print(f"   - {result['test']}: {result.get('response', result.get('error', 'Unknown error'))}")
        
        print("\n🎉 Testing completed!")
        if failed_tests == 0:
            print("🌟 All tests passed! Your API is ready for production.")
        else:
            print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    tester = APITester(API_BASE_URL)
    tester.run_all_tests()
EOF

# Make it executable and run
chmod +x test_all_endpoints.py
python test_all_endpoints.py
```

### **Create Quick Test Script**

```bash
# Create quick_test.sh for rapid testing
cat > quick_test.sh << 'EOF'
#!/bin/bash

# Quick API test script
API_URL="http://localhost:8000"

echo "🚀 Quick API Test for Design Gallery Backend"
echo "Testing: $API_URL"
echo ""

# Test 1: Health check
echo "1️⃣ Health Check..."
curl -s "$API_URL/health" | jq '.' 2>/dev/null || echo "❌ Health check failed"
echo ""

# Test 2: App info
echo "2️⃣ App Info..."
curl -s "$API_URL/info" | jq '.app_name, .version' 2>/dev/null || echo "❌ App info failed"
echo ""

# Test 3: API Documentation
echo "3️⃣ API Documentation..."
if curl -s "$API_URL/docs" | grep -q "FastAPI"; then
    echo "✅ API docs accessible at $API_URL/docs"
else
    echo "❌ API docs not accessible"
fi
echo ""

# Test 4: Registration (should work)
echo "4️⃣ User Registration..."
RESPONSE=$(curl -s -X POST "$API_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "quicktest", "password": "test123"}')

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Registration endpoint working"
else
    echo "❌ Registration failed: $RESPONSE"
fi
echo ""

echo "🎯 Quick test completed!"
echo "For full testing, run: python test_all_endpoints.py"
echo "View API docs at: $API_URL/docs"
EOF

chmod +x quick_test.sh
```

---

## 🛠️ **Development Tools & Tips**

### **1. API Documentation**

When your server is running with `DEBUG=true`, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### **2. Database Management**

#### **View Database Contents**
```bash
# For Cloudflare D1
wrangler d1 execute design-gallery-test-db --command="SELECT * FROM users;"
wrangler d1 execute design-gallery-test-db --command="SELECT * FROM designs LIMIT 5;"

# For local SQLite
sqlite3 test_local.db "SELECT * FROM users;"
sqlite3 test_local.db "SELECT * FROM designs LIMIT 5;"
```

#### **Reset Database**
```bash
# Reset D1 database
wrangler d1 execute design-gallery-test-db --command="DROP TABLE IF EXISTS users;"
wrangler d1 execute design-gallery-test-db --command="DROP TABLE IF EXISTS designs;"
wrangler d1 execute design-gallery-test-db --file=schema.sql

# Reset local database
rm test_local.db
python setup_local_db.py
```

### **3. Log Monitoring**

#### **View Application Logs**
```bash
# When running with uvicorn
uvicorn app.main:app --reload --log-level debug

# Filter logs
uvicorn app.main:app --reload 2>&1 | grep ERROR
```

#### **Enable Request Logging**
```python
# Add to .env for detailed request logging
LOG_LEVEL=DEBUG
```

### **4. Hot Reloading for Development**

The `--reload` flag enables automatic restart when code changes:

```bash
# Development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With custom port
uvicorn app.main:app --reload --port 8080
```

---

## 🐛 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **1. Server Won't Start**

**Error**: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Make sure you're in the backend directory
cd backend
python -m uvicorn app.main:app --reload
```

**Error**: `Port already in use`
```bash
# Solution: Use a different port or kill existing process
lsof -ti:8000 | xargs kill -9
# Or use different port
uvicorn app.main:app --reload --port 8001
```

#### **2. Database Connection Issues**

**Error**: `Failed to connect to D1 database`
```bash
# Check environment variables
env | grep CLOUDFLARE

# Test D1 connection
wrangler d1 execute your-db-id --command="SELECT 1;"

# Verify API token permissions
wrangler whoami
```

**Error**: `Table doesn't exist`
```bash
# Apply database schema
wrangler d1 execute your-db-id --file=schema.sql

# Verify tables exist
wrangler d1 execute your-db-id --command="SELECT name FROM sqlite_master WHERE type='table';"
```

#### **3. Authentication Issues**

**Error**: `JWT token invalid`
```bash
# Check JWT secret length (minimum 32 characters)
echo $JWT_SECRET | wc -c

# Generate new secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Error**: `User not approved`
```bash
# Approve user manually
wrangler d1 execute your-db-id --command="UPDATE users SET is_approved = 1 WHERE username = 'testuser';"
```

#### **4. File Upload Issues**

**Error**: `R2 bucket not accessible`
```bash
# Test R2 connection
wrangler r2 bucket list

# Check R2 credentials
env | grep CLOUDFLARE_R2

# Test upload manually
echo "test" | wrangler r2 object put your-bucket/test.txt
```

#### **5. CORS Issues**

**Error**: `CORS policy blocked`
```bash
# Add your frontend URL to CORS_ORIGINS in .env
CORS_ORIGINS="http://localhost:3000,http://localhost:8081,http://localhost:19006"

# For React Native/Expo
CORS_ORIGINS="http://localhost:19006,http://192.168.1.100:19006"
```

### **Performance Issues**

#### **Slow API Responses**
```bash
# Enable query logging
DEBUG=true

# Check database indexes
wrangler d1 execute your-db-id --command="EXPLAIN QUERY PLAN SELECT * FROM designs WHERE category = 'saree';"
```

#### **Memory Issues**
```bash
# Monitor memory usage
ps aux | grep uvicorn

# Reduce worker processes if needed
uvicorn app.main:app --workers 1
```

### **Cloudflare Service Verification**

#### **Verify D1 Database Connection**
```bash
# Test database connectivity
wrangler d1 execute design-gallery-test-db --command="SELECT COUNT(*) FROM users;"

# Check recent designs
wrangler d1 execute design-gallery-test-db --command="SELECT title, created_at FROM designs ORDER BY created_at DESC LIMIT 3;"
```

#### **Verify R2 Storage Connection**
```bash
# Test file upload capability
echo "connection test" | wrangler r2 object put design-gallery-images-test/connection-test.txt

# Verify upload worked
wrangler r2 object list design-gallery-images-test | grep connection-test

# Clean up test file
wrangler r2 object delete design-gallery-images-test/connection-test.txt
```

---

## 🎯 **Integration with Frontend**

### **Frontend Configuration**

Update your React Native app configuration:

```typescript
// In your React Native app config
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Local development
  : 'https://your-app.onrender.com';  // Production

// For Android emulator, use:
const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8000'  // Android emulator
  : 'https://your-app.onrender.com';

// For device testing, use your computer's IP:
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.100:8000'  // Replace with your IP
  : 'https://your-app.onrender.com';
```

### **Test Frontend Integration**

```bash
# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start React Native (in another terminal)
cd ../AD-APP
npm start

# Test authentication flow
# 1. Register user via app
# 2. Approve user via API or admin panel
# 3. Login via app
# 4. Browse designs
```

---

## ✅ **Pre-Deployment Checklist**

**Our Testing Strategy**: Complete local testing with D1 + R2 + FastAPI, then deploy to Render with confidence.

### **🔧 Infrastructure Setup**
- [ ] Cloudflare D1 test database created and schema applied
- [ ] Cloudflare R2 test bucket created with proper permissions
- [ ] Local FastAPI development environment running smoothly
- [ ] All environment variables configured correctly

### **🧪 API Testing Complete**
- [ ] **Phase 1**: Health & Info endpoints responding (200 status)
- [ ] **Phase 2**: Authentication flow working (admin login, protected routes)
- [ ] **Phase 3**: Design management fully functional (CRUD operations)
- [ ] **Phase 4**: File upload to R2 storage working
- [ ] **Phase 5**: Admin functions tested (user management, analytics)
- [ ] **Phase 6**: Search and filtering operations validated
- [ ] **Comprehensive**: Automated test script passes all endpoints

### **🎯 Production Readiness**
- [ ] Create production D1 database (separate from test)
- [ ] Create production R2 bucket (separate from test)
- [ ] Production environment variables documented
- [ ] Admin user ready for production database
- [ ] Frontend configuration updated for production API URL

### **🚀 Code Quality & Security**
- [ ] No hardcoded credentials or test data in production code
- [ ] JWT secrets are production-strength (32+ characters)
- [ ] Error handling covers edge cases
- [ ] CORS origins configured for production domains
- [ ] File upload limits and validation implemented

---

## 🚀 **Deployment Workflow**

Follow this sequence after completing all local testing:

### **Step 1: Prepare Production Infrastructure**
```bash
# Create production D1 database
wrangler d1 create design-gallery-production-db

# Create production R2 bucket
wrangler r2 bucket create design-gallery-images-production

# Apply schema to production database
wrangler d1 execute design-gallery-production-db --file=schema.sql
```

### **Step 2: Deploy to Render**
1. **Push your tested code** to your Git repository
2. **Deploy to Render** using production environment variables
3. **Update frontend** with production API URL: `https://your-app.onrender.com`

### **Step 3: Post-Deployment Validation**
```bash
# Test production health
curl https://your-app.onrender.com/health

# Test production API docs
# Visit: https://your-app.onrender.com/docs

# Create production admin user
curl -X POST https://your-app.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "production-secure-password"}'
```

### **Step 4: Frontend Integration**
- Update React Native app configuration with production URL
- Test complete user flow from mobile app
- Verify image uploads work end-to-end

---

## 📞 **Support**

If you encounter issues:

1. **Check logs** for specific error messages
2. **Verify environment variables** are correctly set
3. **Test individual components** (database, storage, auth)
4. **Use the troubleshooting guide** above
5. **Check API documentation** at `/docs` endpoint

---

**🎉 You're ready to test your API locally! Start with the quick test script, then run the comprehensive test suite.** 