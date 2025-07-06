# Design Gallery FastAPI Backend

A modern, scalable FastAPI backend for the Design Gallery Android App, deployed on Render with Cloudflare R2 storage and D1 database.

## 🏗️ Architecture

### Technology Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Deployment Platform**: Render
- **Database**: Cloudflare D1 (SQLite)
- **File Storage**: Cloudflare R2 (S3-compatible)
- **Authentication**: JWT with bcrypt password hashing
- **API Documentation**: Automatic OpenAPI/Swagger docs

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Cloudflare D1 client
│   │   ├── security.py         # Authentication & authorization
│   │   └── storage.py          # Cloudflare R2 storage manager
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py             # User-related models
│   │   ├── design.py           # Design-related models
│   │   └── common.py           # Common/shared models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py     # User operations
│   │   └── design_service.py   # Design operations
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── designs.py          # Design management endpoints
│   │   ├── admin.py            # Admin endpoints
│   │   └── upload.py           # File upload endpoints
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── helpers.py          # Helper functions
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── render.yaml                # Render deployment config
├── Dockerfile                 # Container configuration
└── docs/                      # Documentation
    ├── API_DOCUMENTATION.md
    ├── DEPLOYMENT_GUIDE.md
    ├── TESTING_GUIDE.md
    └── CODE_FLOW.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Cloudflare account with R2 and D1 enabled
- Render account (for deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Cloudflare credentials
   ```

5. **Run the application**
   ```bash
   python -m app.main
   ```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

#### Required Variables
- `JWT_SECRET`: Strong secret key for JWT tokens (32+ characters)
- `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID
- `CLOUDFLARE_D1_DATABASE_ID`: D1 database ID
- `CLOUDFLARE_API_TOKEN`: Cloudflare API token with D1 and R2 permissions
- `CLOUDFLARE_R2_ACCOUNT_ID`: R2 account ID
- `CLOUDFLARE_R2_ACCESS_KEY`: R2 access key
- `CLOUDFLARE_R2_SECRET_KEY`: R2 secret key
- `CLOUDFLARE_R2_BUCKET_NAME`: R2 bucket name
- `CLOUDFLARE_R2_PUBLIC_URL`: R2 public URL (e.g., `https://pub-{account-id}.r2.dev`)

#### Optional Variables
- `DEBUG`: Enable debug mode (default: false)
- `ENVIRONMENT`: Environment name (default: production)
- `CORS_ORIGINS`: Allowed CORS origins (default: *)
- `MAX_FILE_SIZE`: Maximum upload file size in bytes (default: 10MB)

### Cloudflare Setup

1. **D1 Database**: Create a D1 database and run the schema
2. **R2 Bucket**: Create an R2 bucket for image storage
3. **API Token**: Create an API token with D1 and R2 permissions

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### Designs
- `GET /api/designs` - List designs with filters and pagination
- `GET /api/designs/{id}` - Get single design
- `GET /api/designs/featured` - Get featured designs
- `POST /api/designs` - Create design (admin only)
- `PUT /api/designs/{id}` - Update design (admin only)
- `DELETE /api/designs/{id}` - Delete design (admin only)
- `POST /api/designs/{id}/favorite` - Add to favorites
- `DELETE /api/designs/{id}/favorite` - Remove from favorites
- `GET /api/designs/user/favorites` - Get user favorites

### Admin
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/analytics` - Get analytics data
- `GET /api/admin/users/pending` - Get pending users
- `POST /api/admin/users/{id}/approve` - Approve user
- `POST /api/admin/users/{id}/reject` - Reject user

### Upload
- `POST /api/upload/image` - Upload image to R2
- `GET /api/upload/presigned-url` - Get presigned upload URL
- `DELETE /api/upload/image/{key}` - Delete image
- `GET /api/upload/images` - List images

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **User Approval**: Admin approval required for new users
- **Role-based Access**: Admin and user roles with proper permissions
- **Input Validation**: Comprehensive request validation with Pydantic
- **CORS Configuration**: Configurable CORS for secure cross-origin requests
- **File Upload Security**: File type and size validation

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app
```

See [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for detailed testing documentation.

## 🚢 Deployment

### Render Deployment

1. **Connect Repository**: Connect your GitHub repository to Render
2. **Environment Variables**: Set all required environment variables in Render dashboard
3. **Deploy**: Render will automatically deploy using `render.yaml` configuration

### Manual Deployment

1. **Build Docker Image**
   ```bash
   docker build -t design-gallery-api .
   ```

2. **Run Container**
   ```bash
   docker run -p 8000:8000 --env-file .env design-gallery-api
   ```

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## 📊 Monitoring

- **Health Check**: `GET /health` endpoint for monitoring
- **Logging**: Structured logging with configurable levels
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Request Tracking**: Request/response logging for debugging

## 🔧 Development

### Code Quality

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

```bash
# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

### Database Migrations

When updating the database schema:

1. Update `schema.sql`
2. Create migration script
3. Test locally
4. Deploy to production

## 📚 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Deployment instructions
- [Testing Guide](docs/TESTING_GUIDE.md) - Testing documentation
- [Code Flow](docs/CODE_FLOW.md) - Application architecture and flow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and linting
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔄 Version History

- **v1.0.0**: Initial release with modular FastAPI architecture
  - User authentication and authorization
  - Design management with R2 storage
  - Admin panel with analytics
  - File upload and management
  - Comprehensive API documentation 