# Design Gallery API Documentation

## Overview

The Design Gallery API is a FastAPI-based backend service that provides comprehensive functionality for managing a design gallery application. The API supports user authentication, design management, file uploads, and administrative features.

**Base URL**: `https://your-app.render.com`  
**API Version**: v1.0.0  
**Authentication**: JWT Bearer Token

## Authentication

### JWT Token Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Tokens expire after 7 days (configurable). Include the token in all authenticated requests.

### User Roles

- **User**: Regular user with basic permissions
- **Admin**: Administrator with full access to all features

## API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
```

Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-50 chars)",
  "password": "string (min 6 chars)"
}
```

**Response:**
```json
{
  "message": "Registration successful! Please wait for admin approval.",
  "success": true
}
```

**Status Codes:**
- `200`: Registration successful
- `400`: Username already exists or validation error
- `422`: Invalid request data

#### Login User
```http
POST /api/auth/login
```

Authenticate user and receive JWT token.

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
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 1,
    "username": "john_doe",
    "is_admin": false,
    "is_approved": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Status Codes:**
- `200`: Login successful
- `401`: Invalid credentials
- `403`: User not approved

#### Get Current User
```http
GET /api/auth/me
```
*Requires authentication*

Get current user information.

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "is_admin": false,
  "is_approved": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Logout User
```http
POST /api/auth/logout
```
*Requires authentication*

Logout user (client should discard token).

**Response:**
```json
{
  "message": "Logout successful. Please discard your access token.",
  "success": true
}
```

---

### Design Endpoints

#### List Designs
```http
GET /api/designs
```
*Requires authentication*

Get designs with pagination and filtering.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `q` (string): Search query
- `category` (string): Filter by category
- `style` (string): Filter by style
- `colour` (string): Filter by colour
- `fabric` (string): Filter by fabric
- `occasion` (string): Filter by occasion
- `featured` (boolean): Filter by featured status
- `designer_name` (string): Filter by designer
- `collection_name` (string): Filter by collection
- `season` (string): Filter by season

**Response:**
```json
{
  "designs": [
    {
      "id": 1,
      "title": "Elegant Saree",
      "description": "Beautiful traditional saree",
      "short_description": "Elegant saree for special occasions",
      "long_description": "Detailed description...",
      "image_url": "https://pub-account.r2.dev/designs/2024/01/image.jpg",
      "r2_object_key": "designs/2024/01/unique-id.jpg",
      "category": "saree",
      "style": "traditional",
      "colour": "red",
      "fabric": "silk",
      "occasion": "wedding",
      "size_available": "S,M,L,XL",
      "price_range": "5000-10000",
      "tags": "elegant,traditional,wedding",
      "featured": true,
      "status": "active",
      "view_count": 150,
      "like_count": 25,
      "designer_name": "Designer Name",
      "collection_name": "Wedding Collection",
      "season": "winter",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "total_pages": 5
}
```

#### Get Single Design
```http
GET /api/designs/{design_id}
```
*Requires authentication*

Get a specific design by ID. Increments view count.

**Response:**
```json
{
  "id": 1,
  "title": "Elegant Saree",
  // ... full design object
}
```

**Status Codes:**
- `200`: Design found
- `404`: Design not found

#### Get Featured Designs
```http
GET /api/designs/featured
```
*Requires authentication*

Get featured designs.

**Query Parameters:**
- `limit` (int): Number of designs to return (default: 10, max: 50)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Featured Design",
    // ... design object
  }
]
```

#### Create Design
```http
POST /api/designs
```
*Requires admin authentication*

Create a new design.

**Request Body:**
```json
{
  "title": "Design Title",
  "description": "Design description",
  "short_description": "Short description",
  "long_description": "Long description",
  "r2_object_key": "designs/2024/01/image.jpg",
  "category": "saree",
  "style": "traditional",
  "colour": "red",
  "fabric": "silk",
  "occasion": "wedding",
  "size_available": "S,M,L",
  "price_range": "5000-10000",
  "tags": "elegant,traditional",
  "featured": false,
  "designer_name": "Designer Name",
  "collection_name": "Collection Name",
  "season": "winter"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Design Title",
  // ... full design object
}
```

#### Update Design
```http
PUT /api/designs/{design_id}
```
*Requires admin authentication*

Update an existing design.

**Request Body:** (All fields optional)
```json
{
  "title": "Updated Title",
  "featured": true,
  "status": "active"
}
```

#### Delete Design
```http
DELETE /api/designs/{design_id}
```
*Requires admin authentication*

Delete a design and its associated image.

**Response:**
```json
{
  "message": "Design deleted successfully",
  "success": true
}
```

#### Add to Favorites
```http
POST /api/designs/{design_id}/favorite
```
*Requires authentication*

Add design to user's favorites.

**Response:**
```json
{
  "message": "Design added to favorites",
  "success": true
}
```

#### Remove from Favorites
```http
DELETE /api/designs/{design_id}/favorite
```
*Requires authentication*

Remove design from user's favorites.

**Response:**
```json
{
  "message": "Design removed from favorites",
  "success": true
}
```

#### Get User Favorites
```http
GET /api/designs/user/favorites
```
*Requires authentication*

Get user's favorite designs.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Favorite Design",
    // ... design object
  }
]
```

---

### Admin Endpoints

#### List All Users
```http
GET /api/admin/users
```
*Requires admin authentication*

Get all registered users.

**Response:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "is_admin": false,
    "is_approved": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Update User
```http
PUT /api/admin/users/{user_id}
```
*Requires admin authentication*

Update user status.

**Request Body:**
```json
{
  "is_approved": true,
  "is_admin": false
}
```

#### Delete User
```http
DELETE /api/admin/users/{user_id}
```
*Requires admin authentication*

Delete a user account.

**Response:**
```json
{
  "message": "User deleted successfully",
  "success": true
}
```

#### Get Analytics
```http
GET /api/admin/analytics
```
*Requires admin authentication*

Get dashboard analytics.

**Response:**
```json
{
  "total_users": 100,
  "total_designs": 500,
  "total_views": 10000,
  "total_likes": 2500,
  "active_users": 95,
  "featured_designs": 50,
  "pending_users": 5,
  "popular_categories": [
    {
      "category": "saree",
      "count": 200
    }
  ],
  "recent_activity": [
    {
      "title": "New Design",
      "created_at": "2024-01-01T00:00:00Z",
      "activity_type": "design_created"
    }
  ]
}
```

#### Get Pending Users
```http
GET /api/admin/users/pending
```
*Requires admin authentication*

Get users awaiting approval.

#### Approve User
```http
POST /api/admin/users/{user_id}/approve
```
*Requires admin authentication*

Approve a pending user.

#### Reject User
```http
POST /api/admin/users/{user_id}/reject
```
*Requires admin authentication*

Reject a pending user.

---

### Upload Endpoints

#### Upload Image
```http
POST /api/upload/image
```
*Requires admin authentication*

Upload an image to R2 storage.

**Request Body:** (multipart/form-data)
- `file`: Image file
- `category`: Image category (query parameter)

**Response:**
```json
{
  "object_key": "designs/2024/01/unique-id.jpg",
  "public_url": "https://pub-account.r2.dev/designs/2024/01/unique-id.jpg"
}
```

#### Get Presigned Upload URL
```http
GET /api/upload/presigned-url
```
*Requires admin authentication*

Get a presigned URL for direct upload to R2.

**Query Parameters:**
- `filename`: Original filename
- `category`: Image category

**Response:**
```json
{
  "object_key": "designs/2024/01/unique-id.jpg",
  "upload_url": "https://presigned-upload-url",
  "public_url": "https://pub-account.r2.dev/designs/2024/01/unique-id.jpg"
}
```

#### Delete Image
```http
DELETE /api/upload/image/{object_key}
```
*Requires admin authentication*

Delete an image from R2 storage.

#### List Images
```http
GET /api/upload/images
```
*Requires admin authentication*

List images in R2 storage.

**Query Parameters:**
- `prefix`: Filter by prefix
- `limit`: Maximum number of images (default: 50)

---

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Error Response Format

```json
{
  "error": "Error Type",
  "message": "Human readable error message",
  "success": false,
  "details": [] // Optional validation details
}
```

## Rate Limiting

- Standard endpoints: 100 requests per minute
- Upload endpoints: 10 requests per minute
- Authentication endpoints: 20 requests per minute

## File Upload Specifications

### Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

### File Size Limits
- Maximum file size: 10MB
- Recommended dimensions: 1920x1080 or higher

### Upload Process

1. **Direct Upload**: Use `/api/upload/image` endpoint
2. **Presigned Upload**: 
   - Get presigned URL from `/api/upload/presigned-url`
   - Upload directly to R2 using the presigned URL
   - Use the returned object key to create designs

## SDK Examples

### JavaScript/TypeScript

```javascript
// Authentication
const response = await fetch('https://api.example.com/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password123'
  })
});

const { access_token } = await response.json();

// Authenticated request
const designsResponse = await fetch('https://api.example.com/api/designs', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});

const designs = await designsResponse.json();
```

### Python

```python
import requests

# Authentication
auth_response = requests.post('https://api.example.com/api/auth/login', json={
    'username': 'user@example.com',
    'password': 'password123'
})

token = auth_response.json()['access_token']

# Authenticated request
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

designs_response = requests.get('https://api.example.com/api/designs', headers=headers)
designs = designs_response.json()
```

## Webhooks

Currently not implemented. Future versions may include webhook support for:
- New user registrations
- Design approvals
- File uploads

## API Versioning

The API uses URL path versioning. Current version is v1 (implicit in base path `/api/`). 

Future versions will be available at:
- `/api/v2/`
- `/api/v3/`

Legacy versions will be supported for a minimum of 12 months after new version release.

## Support

For API support:
1. Check this documentation
2. Review the OpenAPI spec at `/docs`
3. Contact the development team 