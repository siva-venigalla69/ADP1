# Design Gallery Project - Comprehensive Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Setup & Deployment](#setup--deployment)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [Frontend Integration](#frontend-integration)
7. [Testing](#testing)
8. [Security & Best Practices](#security--best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

The Design Gallery is a mobile application for showcasing Indian traditional wear designs including sarees, lehengas, suits, and accessories. The project uses a modern cloud-first architecture with Cloudflare services.

### Technology Stack

**Backend:**
- Cloudflare Workers (Serverless Runtime)
- Cloudflare D1 (SQLite Database)
- Cloudflare R2 (Object Storage)
- Hono Framework (Web Framework)
- TypeScript

**Frontend:**
- React Native
- Expo
- TypeScript

### Key Features

- ✅ User authentication and authorization
- ✅ Design gallery with advanced filtering
- ✅ Image upload and management with R2
- ✅ Admin panel for content management
- ✅ Favorites and user preferences
- ✅ Analytics and reporting
- ✅ Search functionality
- ✅ Category management
- ✅ Screenshot prevention
- ✅ Responsive design

---

## Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Native  │────│ Cloudflare      │────│  Cloudflare D1  │
│   Mobile App    │    │    Workers      │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        
                                │                        
                       ┌─────────────────┐              
                       │  Cloudflare R2  │              
                       │ Object Storage  │              
                       └─────────────────┘              
```

### Data Flow

1. **Authentication**: JWT-based authentication with secure token storage
2. **Image Upload**: Direct upload to R2 with signed URLs
3. **Data Management**: CRUD operations through D1 database
4. **Content Delivery**: Optimized image delivery through R2 CDN

---

## Setup & Deployment

### Prerequisites

- Node.js 18+
- npm/yarn
- Cloudflare account
- Wrangler CLI

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   npm install
   ```

2. **Configure Cloudflare Services**
   ```bash
   # Create D1 database
   wrangler d1 create design-gallery-db
   
   # Create R2 bucket
   wrangler r2 bucket create design-gallery-images
   
   # Set environment secrets
   wrangler secret put JWT_SECRET
   # Enter a strong secret (32+ characters)
   ```

3. **Update wrangler.toml**
   ```toml
   name = "design-gallery-worker"
   main = "src/index.ts"
   compatibility_date = "2024-01-01"
   
   [[d1_databases]]
   binding = "DB"
   database_name = "design-gallery-db"
   database_id = "your-database-id"
   
   [[r2_buckets]]
   binding = "GALLERY_BUCKET"
   bucket_name = "design-gallery-images"
   ```

4. **Setup Database**
   ```bash
   # Run initial schema
   wrangler d1 execute design-gallery-db --file=schema.sql
   
   # Run migration (if updating existing database)
   wrangler d1 execute design-gallery-db --file=create-migration.sql
   ```

5. **Deploy Worker**
   ```bash
   # Development
   npm run dev
   
   # Production
   npm run deploy
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd AD-APP
   npm install
   ```

2. **Configure Environment**
   ```bash
   # Create .env file
   API_BASE_URL=https://your-worker.your-subdomain.workers.dev
   ```

3. **Start Development**
   ```bash
   npm start
   ```

---

## Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    is_approved INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### designs
```sql
CREATE TABLE designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    short_description TEXT,
    long_description TEXT,
    image_url TEXT NOT NULL,
    r2_object_key TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    style TEXT,
    colour TEXT,
    fabric TEXT,
    occasion TEXT,
    size_available TEXT,
    price_range TEXT,
    tags TEXT,
    featured INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    designer_name TEXT,
    collection_name TEXT,
    season TEXT,
    created_by INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### app_settings
```sql
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    allow_screenshots INTEGER DEFAULT 0,
    allow_downloads INTEGER DEFAULT 0,
    watermark_enabled INTEGER DEFAULT 1,
    max_upload_size INTEGER DEFAULT 10485760,
    supported_formats TEXT DEFAULT 'jpg,jpeg,png,webp',
    gallery_per_page INTEGER DEFAULT 20,
    featured_designs_count INTEGER DEFAULT 10,
    maintenance_mode INTEGER DEFAULT 0,
    app_version TEXT DEFAULT '1.0.0',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Additional Tables

- **user_favorites**: Track user preferences
- **design_views**: Analytics and view tracking
- **categories**: Dynamic category management

---

## API Documentation

### Authentication Endpoints

#### POST /api/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "User registered successfully and approved."
}
```

#### POST /api/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "jwt-token",
  "user": {
    "id": 1,
    "username": "string",
    "isAdmin": false
  }
}
```

### Design Endpoints

#### GET /api/designs
Retrieve paginated list of designs with filtering.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `category`: Filter by category
- `style`: Filter by style
- `colour`: Filter by color
- `fabric`: Filter by fabric
- `occasion`: Filter by occasion
- `featured`: Show only featured designs (true/false)
- `search`: Search in title, description, tags

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "designs": [...],
  "totalCount": 100,
  "page": 1,
  "limit": 20,
  "totalPages": 5
}
```

#### GET /api/designs/:id
Get single design details.

#### POST /api/designs
Create new design (Admin only).

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "short_description": "string",
  "long_description": "string",
  "r2_object_key": "string",
  "category": "string",
  "style": "string",
  "colour": "string",
  "fabric": "string",
  "occasion": "string",
  "size_available": "string",
  "price_range": "string",
  "tags": "string",
  "featured": 0,
  "designer_name": "string",
  "collection_name": "string",
  "season": "string"
}
```

#### PUT /api/designs/:id
Update existing design (Admin only).

#### DELETE /api/designs/:id
Delete design and associated R2 object (Admin only).

### Admin Endpoints

#### GET /api/admin/users
Get all users (Admin only).

#### POST /api/admin/approve-user
Approve or reject user (Admin only).

#### POST /api/admin/upload-url
Generate upload URL for R2 (Admin only).

#### GET /api/admin/analytics
Get analytics data (Admin only).

### Settings Endpoints

#### GET /api/settings
Get application settings (Public).

#### PUT /api/admin/settings
Update application settings (Admin only).

### Favorites Endpoints

#### GET /api/favorites
Get user's favorite designs.

#### POST /api/favorites/:id
Add design to favorites.

#### DELETE /api/favorites/:id
Remove design from favorites.

### Category & Search Endpoints

#### GET /api/categories
Get all active categories.

#### GET /api/search
Search designs with query string.

---

## Frontend Integration

### API Service Configuration

```typescript
// services/api.ts
const API_BASE_URL = 'https://your-worker.your-subdomain.workers.dev';

class ApiService {
  private baseURL = API_BASE_URL;
  private token: string | null = null;

  async setToken(token: string) {
    this.token = token;
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  // Authentication
  async login(username: string, password: string) {
    return this.request('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async register(username: string, password: string) {
    return this.request('/api/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  // Designs
  async getDesigns(params: any = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/api/designs?${query}`);
  }

  async getDesign(id: string) {
    return this.request(`/api/designs/${id}`);
  }

  // Favorites
  async getFavorites() {
    return this.request('/api/favorites');
  }

  async addToFavorites(designId: string) {
    return this.request(`/api/favorites/${designId}`, {
      method: 'POST',
    });
  }

  async removeFromFavorites(designId: string) {
    return this.request(`/api/favorites/${designId}`, {
      method: 'DELETE',
    });
  }

  // Settings
  async getSettings() {
    return this.request('/api/settings');
  }

  // Search
  async searchDesigns(query: string, category?: string) {
    const params = new URLSearchParams({ q: query });
    if (category) params.append('category', category);
    return this.request(`/api/search?${params}`);
  }
}

export const apiService = new ApiService();
```

### Authentication Hook

```typescript
// hooks/useAuth.ts
import { useState, useEffect, createContext, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/api';

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const userData = await AsyncStorage.getItem('user_data');
      
      if (token && userData) {
        await apiService.setToken(token);
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Error loading auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const response = await apiService.login(username, password);
    
    await AsyncStorage.setItem('auth_token', response.token);
    await AsyncStorage.setItem('user_data', JSON.stringify(response.user));
    await apiService.setToken(response.token);
    
    setUser(response.user);
  };

  const logout = async () => {
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('user_data');
    await apiService.setToken('');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

## Testing

### Backend API Testing

Run the comprehensive test suite:

```bash
cd backend
npm install axios  # Install testing dependency
node test-api.js   # Run all tests

# Run specific test suites
node test-api.js --auth      # Authentication tests
node test-api.js --designs   # Design endpoints
node test-api.js --admin     # Admin endpoints
node test-api.js --settings  # Settings endpoints

# Test against production
node test-api.js --url https://your-worker.your-subdomain.workers.dev
```

### Manual Testing Checklist

#### Authentication
- [ ] User registration
- [ ] User login
- [ ] Token validation
- [ ] Admin login
- [ ] Unauthorized access handling

#### Design Management
- [ ] Create design (admin)
- [ ] List designs with pagination
- [ ] Get single design
- [ ] Update design (admin)
- [ ] Delete design (admin)
- [ ] Search and filter designs

#### User Features
- [ ] Add to favorites
- [ ] Remove from favorites
- [ ] View favorites list
- [ ] Record design views

#### Admin Features
- [ ] User approval
- [ ] Upload URL generation
- [ ] Settings management
- [ ] Analytics dashboard

---

## Security & Best Practices

### Security Measures

1. **JWT Security**
   - Strong secret key (32+ characters)
   - Token expiration (24 hours)
   - Secure storage on client

2. **Password Security**
   - bcrypt hashing (10 rounds)
   - Minimum 6 character requirement
   - No password in logs/responses

3. **API Security**
   - Role-based access control
   - Input validation
   - SQL injection prevention
   - CORS configuration

4. **R2 Security**
   - Signed upload URLs
   - File type validation
   - Size limits
   - Clean filename generation

### Performance Optimizations

1. **Database**
   - Proper indexing
   - Efficient queries
   - Pagination
   - Connection pooling

2. **Image Delivery**
   - R2 CDN integration
   - Optimized image URLs
   - Lazy loading
   - Caching headers

3. **API Design**
   - Proper HTTP status codes
   - Consistent error handling
   - Response compression
   - Request debouncing

---

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check D1 configuration
wrangler d1 info design-gallery-db

# Verify schema
wrangler d1 execute design-gallery-db --command="SELECT name FROM sqlite_master WHERE type='table';"
```

#### R2 Upload Issues
```bash
# Check R2 bucket
wrangler r2 bucket list

# Test upload
wrangler r2 object put design-gallery-images/test.txt --file=test.txt
```

#### Authentication Problems
```bash
# Check JWT secret
wrangler secret list

# Re-set JWT secret if needed
wrangler secret put JWT_SECRET
```

#### CORS Issues
- Verify CORS configuration in worker
- Check request headers
- Test with different origins

### Debugging

1. **Worker Logs**
   ```bash
   wrangler tail
   ```

2. **Local Development**
   ```bash
   npm run dev
   # Test against localhost:8787
   ```

3. **Production Testing**
   ```bash
   node test-api.js --url https://your-worker.workers.dev
   ```

### Environment Variables

Make sure these are properly set:

- `JWT_SECRET`: Strong random string
- `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID
- `CLOUDFLARE_API_TOKEN`: API token with proper permissions

### Database Migration

If you need to migrate existing data:

```bash
# Backup existing data
wrangler d1 execute design-gallery-db --command="SELECT * FROM designs;" --output=backup.json

# Run migration
wrangler d1 execute design-gallery-db --file=create-migration.sql

# Verify migration
wrangler d1 execute design-gallery-db --command="PRAGMA table_info(designs);"
```

---

## Deployment Checklist

### Before Deployment

- [ ] Update production URLs in wrangler.toml
- [ ] Set all required secrets
- [ ] Run database migrations
- [ ] Test all API endpoints
- [ ] Configure R2 bucket policies
- [ ] Set up custom domain (optional)

### Production Deployment

```bash
# Deploy worker
npm run deploy

# Verify deployment
curl https://your-worker.workers.dev/health

# Run production tests
node test-api.js --url https://your-worker.workers.dev
```

### Post-Deployment

- [ ] Monitor worker logs
- [ ] Check database connections
- [ ] Verify image uploads
- [ ] Test frontend integration
- [ ] Monitor performance metrics

---

## Support & Maintenance

### Regular Tasks

1. **Database Maintenance**
   - Monitor database size
   - Clean up old view records
   - Optimize queries

2. **Storage Management**
   - Monitor R2 storage usage
   - Clean up orphaned objects
   - Implement retention policies

3. **Security Updates**
   - Rotate JWT secrets
   - Update dependencies
   - Review access logs

### Monitoring

Set up monitoring for:
- API response times
- Error rates
- Database query performance
- Storage usage
- User activity

---

This comprehensive guide provides everything needed to understand, deploy, and maintain the Design Gallery project. For specific implementation details, refer to the respective source files in the project repository. 