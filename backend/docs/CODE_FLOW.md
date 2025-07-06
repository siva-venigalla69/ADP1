# Code Flow and Architecture

This document explains the application architecture, request flow, and code organization of the Design Gallery FastAPI backend.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Native  │────│   FastAPI API   │────│  Cloudflare D1  │
│   Mobile App    │    │   (Render)      │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        
                                │                        
                       ┌─────────────────┐              
                       │  Cloudflare R2  │              
                       │ Object Storage  │              
                       └─────────────────┘              
```

## Application Layers

### 1. API Layer (`app/api/`)
- **Purpose**: Handle HTTP requests and responses
- **Components**: Route handlers, request validation, response formatting
- **Files**: `auth.py`, `designs.py`, `admin.py`, `upload.py`

### 2. Service Layer (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Components**: User management, design operations, data validation
- **Files**: `user_service.py`, `design_service.py`

### 3. Core Layer (`app/core/`)
- **Purpose**: Infrastructure and cross-cutting concerns
- **Components**: Database clients, authentication, storage, configuration
- **Files**: `database.py`, `security.py`, `storage.py`, `config.py`

### 4. Model Layer (`app/models/`)
- **Purpose**: Data structures and validation
- **Components**: Pydantic models for request/response
- **Files**: `user.py`, `design.py`, `common.py`

## Request Flow

### Authentication Flow

```
Client Request → API Router → Security Middleware → Service Layer → Database
      ↓              ↓              ↓                   ↓            ↓
   Validate      Extract JWT    Verify Token      Business      Store/Retrieve
   Input         from Header    & Permissions     Logic         User Data
```

#### 1. User Registration
```python
POST /api/auth/register
├── api/auth.py:register_user()
├── services/user_service.py:create_user()
├── core/security.py:hash_password()
├── core/database.py:create()
└── models/user.py:UserCreate/UserResponse
```

#### 2. User Login
```python
POST /api/auth/login
├── api/auth.py:login_user()
├── services/user_service.py:authenticate_user()
├── core/security.py:verify_password()
├── core/security.py:create_access_token()
└── models/common.py:Token
```

### Design Management Flow

```
Client Request → Authentication → Service Layer → Database + Storage
      ↓               ↓              ↓               ↓         ↓
   Validate        Check JWT     Business Logic   Store     Upload
   Input          & Permissions   + Validation    Metadata   Files
```

#### 1. Create Design
```python
POST /api/designs
├── api/designs.py:create_design()
├── core/security.py:get_admin_user()
├── services/design_service.py:create_design()
├── core/storage.py:file_exists()
├── core/database.py:create()
└── models/design.py:DesignCreate/DesignResponse
```

#### 2. Get Designs with Filters
```python
GET /api/designs?category=saree&page=1
├── api/designs.py:get_designs()
├── core/security.py:get_current_active_user()
├── services/design_service.py:get_designs()
├── core/database.py:count() + execute_query()
└── models/design.py:DesignListResponse
```

### File Upload Flow

```
Client → API → Validation → R2 Storage → Database Update
   ↓      ↓         ↓           ↓             ↓
 Select  Validate  Check      Upload      Store Object
 File    Type/Size Permissions File        Key + URL
```

#### Upload Process
```python
POST /api/upload/image
├── api/upload.py:upload_image()
├── core/security.py:get_admin_user()
├── core/storage.py:generate_object_key()
├── core/storage.py:upload_file()
└── models/common.py:ImageUploadResponse
```

## Database Layer

### CloudflareD1Client
```python
class CloudflareD1Client:
    def __init__(self):
        # Initialize HTTP client for D1 REST API
        
    async def execute_query(self, query, params):
        # Execute SQL via REST API
        # Handle errors and retries
        # Return structured results
```

### DatabaseManager
```python
class DatabaseManager:
    def __init__(self):
        self.client = CloudflareD1Client()
    
    async def get_by_id(self, table, id):
        # Generic CRUD operations
    
    async def create(self, table, data):
        # Generic create with validation
    
    async def search(self, table, fields, term):
        # Full-text search across fields
```

## Storage Layer

### R2StorageManager
```python
class R2StorageManager:
    def __init__(self):
        # Initialize boto3 S3 client for R2
        
    def generate_object_key(self, filename, category):
        # Create organized file paths
        # Format: category/year/month/timestamp_uuid.ext
        
    async def upload_file(self, data, key, content_type):
        # Upload to R2 with metadata
        # Set public read permissions
        
    def get_public_url(self, key):
        # Generate public URLs for files
```

## Security Implementation

### JWT Authentication
```python
# Token creation
payload = {
    "user_id": user.id,
    "username": user.username,
    "is_admin": user.is_admin,
    "exp": expiration_time
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Token verification
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
return TokenData(**payload)
```

### Password Security
```python
# Hash password on registration
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verify password on login
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
```

### Role-Based Access Control
```python
# Dependency injection for route protection
async def get_admin_user(current_user: TokenData = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

## Error Handling

### Exception Hierarchy
```
HTTPException (FastAPI)
├── 400 Bad Request → Validation errors, bad input
├── 401 Unauthorized → Missing/invalid token
├── 403 Forbidden → Insufficient permissions
├── 404 Not Found → Resource not found
├── 422 Unprocessable Entity → Pydantic validation
└── 500 Internal Server Error → Unexpected errors
```

### Error Response Format
```python
{
    "error": "Error Type",
    "message": "Human readable message",
    "success": false,
    "details": []  # Optional validation details
}
```

## Configuration Management

### Environment-Based Config
```python
class Settings(BaseSettings):
    # Application settings with environment variable mapping
    app_name: str = Field(env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Cloudflare integration
    cloudflare_account_id: str = Field(env="CLOUDFLARE_ACCOUNT_ID")
    cloudflare_api_token: str = Field(env="CLOUDFLARE_API_TOKEN")
    
    class Config:
        env_file = ".env"
```

## Dependency Injection

### FastAPI Dependencies
```python
# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify JWT token and return user data

# Database dependency
def get_db_manager():
    return db_manager

# Route with dependencies
@router.get("/designs")
async def get_designs(
    current_user: TokenData = Depends(get_current_active_user),
    db: DatabaseManager = Depends(get_db_manager)
):
    # Route logic with injected dependencies
```

## Data Validation

### Pydantic Models
```python
class DesignCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., description="Design category")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### Request/Response Flow
```
Raw Request → Pydantic Model → Validation → Service Logic → Response Model → JSON
```

## Logging and Monitoring

### Structured Logging
```python
import logging

logger = logging.getLogger(__name__)

# Request logging
logger.info(f"API Call - {method} {endpoint} - User: {user_id} - Status: {status}")

# Error logging
logger.error(f"Database error: {str(e)}", exc_info=True)
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }
```

## Testing Architecture

### Test Layers
```
Unit Tests → Service Layer Tests → Integration Tests → E2E Tests
     ↓              ↓                    ↓              ↓
   Models      Business Logic      API + Database   Full Workflow
   Utilities   Service Methods     Storage Tests    User Journeys
```

### Mock Strategy
```python
# Mock external services in tests
@patch('app.core.database.CloudflareD1Client.execute_query')
@patch('app.core.storage.R2StorageManager.upload_file')
async def test_design_creation(mock_upload, mock_query):
    # Test business logic without external dependencies
```

## Performance Considerations

### Database Optimization
- **Indexing**: Key fields for search and filtering
- **Query Optimization**: Efficient SQL with proper pagination
- **Connection Pooling**: Reuse HTTP connections for D1 API

### Caching Strategy
- **Static Data**: App settings, categories
- **User Data**: User profiles, permissions
- **File URLs**: R2 public URLs

### Async Processing
```python
# Async database operations
async def get_designs_concurrently():
    tasks = [
        get_featured_designs(),
        get_popular_categories(),
        get_recent_designs()
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## Deployment Pipeline

### Build Process
```
Code → Lint/Test → Build → Deploy → Health Check
 ↓         ↓        ↓       ↓         ↓
Git    Pytest   Docker  Render   Verify
Push   Coverage  Image   Deploy   Status
```

### Environment Promotion
```
Development → Staging → Production
     ↓           ↓          ↓
   Local      Preview    Live API
   Testing    Testing    Monitoring
```

## Scalability Design

### Horizontal Scaling
- **Stateless Design**: No server-side session storage
- **Database**: Cloudflare D1 auto-scaling
- **Storage**: Cloudflare R2 global distribution
- **API**: Multiple Render instances behind load balancer

### Performance Monitoring
- **Response Times**: Track API endpoint performance
- **Error Rates**: Monitor for service degradation
- **Resource Usage**: CPU, memory, database queries
- **External Services**: D1 and R2 response times

## Security Architecture

### Defense in Depth
1. **Input Validation**: Pydantic models
2. **Authentication**: JWT tokens
3. **Authorization**: Role-based access
4. **Data Protection**: Encrypted storage
5. **Network Security**: HTTPS, CORS
6. **Monitoring**: Error tracking, audit logs

This architecture provides a robust, scalable foundation for the Design Gallery application with clear separation of concerns and comprehensive error handling. 