Understood! You want to combine the initial comprehensive Technical Specification with the new additions for enabling/disabling screenshot and download prevention into one cohesive document.
Here's the fully combined and updated Technical Specification Document:

Technical Specification Document: Design Gallery Android App


1. Introduction

This document outlines the technical design and implementation details for the Design Gallery Android App, as defined by the accompanying functional requirements. The goal is to build a secure, performant, and scalable application using React Native for the frontend and Cloudflare Workers, D1, and Images for the backend.

2. Architecture Overview

The system employs a client-server architecture:
Frontend (Client): React Native Android application.
Backend (Serverless API & Data): Cloudflare Workers (Hono), Cloudflare D1 (SQLite-compatible), Cloudflare Images.
Admin Tool (External Script): Python script for bulk image and metadata upload.



+-------------------+           +-------------------+
|                   |           |                   |
|  Android App      | <-------> | Cloudflare Worker |
|  (React Native)   |           |    (Hono)         |
|                   |           |                   |
+-------------------+           +--------^----------+
         ^                              |
         | (Secure Storage)             | (DB Queries)
         v                              |
+-------------------+                   |
| Device Keychain   |                   | (Image Mgmt)
| (JWT Storage)     |                   |
+-------------------+                   |
                                        |
                                        v
                            +-------------------+    +-------------------+
                            |  Cloudflare D1    |    |  Cloudflare Images|
                            | (SQLite Database) |    |                   |
                            +-------------------+    +-------------------+
                                   ^
                                   | (Admin Tool)
                                   |
                                   v
                            +-------------------+
                            |  Python Script    |
                            | (Bulk Upload)     |
                            +-------------------+



3. Data Models (Cloudflare D1)


3.1. users Table

Purpose: Stores user authentication and authorization information.
Schema (SQL):
SQL
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0, -- 0 for false, 1 for true
    is_approved INTEGER DEFAULT 0, -- 0 for false, 1 for true (awaiting admin approval)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


Constraints:
username is UNIQUE to prevent duplicate registrations.
username and password_hash are NOT NULL.
Indexing: username (implicit primary key index on id, explicit on username for quick lookups).

3.2. designs Table

Purpose: Stores metadata for each design and its associated Cloudflare Image ID.
Schema (SQL):
SQL
CREATE TABLE IF NOT EXISTS designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    designname TEXT NOT NULL,
    style TEXT,
    colour TEXT,
    short_description TEXT,
    long_description TEXT,
    categories TEXT, -- Comma-separated string for simplicity within 3-day scope
    cloudflare_image_id TEXT UNIQUE NOT NULL, -- ID from Cloudflare Images service
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


Constraints:
designname and cloudflare_image_id are NOT NULL.
cloudflare_image_id is UNIQUE.
Indexing: id (implicit primary key index), cloudflare_image_id, and potentially combined indexes for style, colour, categories to optimize filtering and searching.

3.3. app_settings Table

Purpose: Stores global application settings, including the state of screenshot and download prevention. This table will typically have only one row.
Schema (SQL):
SQL
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY DEFAULT 1, -- Ensure only one row
    allow_screenshots INTEGER DEFAULT 0, -- 0 for false (prevent), 1 for true (allow)
    allow_downloads INTEGER DEFAULT 0, -- 0 for false (prevent), 1 for true (allow)
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


Constraints:
id default to 1 ensures a single row. Updates will always target this row.

4. Backend API Specification (Cloudflare Workers)

All API endpoints will be served from a Cloudflare Worker using the Hono framework.
Base URL: https://[YOUR_WORKER_SUBDOMAIN].workers.dev

4.1. Authentication & Authorization


4.1.1. POST /api/register

Description: Registers a new user.
Authentication: None (public endpoint).
Request Body (JSON):
JSON
{
    "username": "string",
    "password": "string"
}


Response:
Success (201 Created):
JSON
{
    "message": "User registered successfully. Awaiting admin approval."
}


Error (409 Conflict): If username already exists.
JSON
{
    "error": "Username already taken."
}


Error (400 Bad Request): If username or password are missing.

4.1.2. POST /api/login

Description: Authenticates a user and issues a JWT.
Authentication: None (public endpoint).
Request Body (JSON):
JSON
{
    "username": "string",
    "password": "string"
}


Response:
Success (200 OK):
JSON
{
    "token": "string" // JWT
}


Error (401 Unauthorized): For invalid credentials or unapproved users.
JSON
{
    "error": "Invalid credentials or user not approved."
}


Error (400 Bad Request): If username or password are missing.

4.1.3. POST /api/admin/approve-user

Description: Approves or disapproves a user.
Authentication: Required (Bearer Token) & Admin-only.
Request Body (JSON):
JSON
{
    "userId": 123,
    "approved": true // boolean
}


Response:
Success (200 OK):
JSON
{
    "message": "User approval status updated successfully."
}


Error (401 Unauthorized): Invalid/missing token.
Error (403 Forbidden): Non-admin user.
Error (404 Not Found): User ID not found.

4.1.4. GET /api/admin/users

Description: Retrieves a list of all registered users for admin approval management.
Authentication: Required (Bearer Token) & Admin-only.
Response (200 OK):
JSON
[
    {
        "id": 1,
        "username": "admin",
        "is_admin": 1,
        "is_approved": 1
    },
    {
        "id": 2,
        "username": "testuser",
        "is_admin": 0,
        "is_approved": 0
    }
]


Error (401 Unauthorized): Invalid/missing token.
Error (403 Forbidden): Non-admin user.

4.1.5. GET /api/settings

Description: Retrieves global application settings.
Authentication: None (public endpoint, as app needs settings before login).
Response (200 OK):
JSON
{
    "allow_screenshots": 0, // 0 for false, 1 for true
    "allow_downloads": 0    // 0 for false, 1 for true
}



4.1.6. PUT /api/admin/settings

Description: Updates global application settings.
Authentication: Required (Bearer Token) & Admin-only.
Request Body (JSON):
JSON
{
    "allow_screenshots": 1, // Optional: 0 to prevent, 1 to allow
    "allow_downloads": 0    // Optional: 0 to prevent, 1 to allow
}


Response:
Success (200 OK):
JSON
{
    "message": "App settings updated successfully."
}


Error (401 Unauthorized): Invalid/missing token.
Error (403 Forbidden): Non-admin user.
Error (400 Bad Request): Invalid input.

4.2. Design Management


4.2.1. POST /api/admin/designs

Description: Adds new design metadata to the database.
Authentication: Required (Bearer Token) & Admin-only.
Request Body (JSON):
JSON
{
    "designname": "string",
    "style": "string",
    "colour": "string",
    "short_description": "string",
    "long_description": "string",
    "categories": "string", // Comma-separated
    "cloudflare_image_id": "string"
}


Response:
Success (201 Created):
JSON
{
    "message": "Design added successfully.",
    "designId": 123
}


Error (401 Unauthorized): Invalid/missing token.
Error (403 Forbidden): Non-admin user.
Error (400 Bad Request): Missing required fields.

4.2.2. GET /api/designs

Description: Retrieves a list of designs with optional filters, search, and pagination.
Authentication: Required (Bearer Token) (any logged-in user).
Query Parameters:
limit (integer, default: 20): Number of designs to return.
offset (integer, default: 0): Number of designs to skip.
style (string): Filter by design style.
colour (string): Filter by design colour.
categories (string): Filter by design categories (exact match, supports partial string in comma-separated field for simplicity).
q (string): Search query for designname, short_description, long_description, style, colour, categories.
Response (200 OK):
JSON
{
    "designs": [
        {
            "id": 1,
            "designname": "Abstract Flow",
            "style": "Abstract",
            "colour": "Blue",
            "short_description": "A vibrant piece.",
            "long_description": "Detailed description...",
            "categories": "Digital,Abstract",
            "cloudflare_image_id": "manual_image_id_1",
            "uploaded_at": "DATETIME_STRING",
            "cloudflare_image_url_thumbnail": "https://imagedelivery.net/[ACCOUNT_HASH]/manual_image_id_1/thumbnail",
            "cloudflare_image_url_medium": "https://imagedelivery.net/[ACCOUNT_HASH]/manual_image_id_1/medium",
            "cloudflare_image_url_original": "https://imagedelivery.net/[ACCOUNT_HASH]/manual_image_id_1/public"
        }
    ],
    "totalCount": 100 // Total designs matching filters, for pagination
}


Error (401 Unauthorized): Invalid/missing token.

4.2.3. GET /api/designs/:id

Description: Retrieves details for a single design.
Authentication: Required (Bearer Token) (any logged-in user).
Path Parameter: :id (integer) - The ID of the design.
Response (200 OK):
JSON
{
    "id": 1,
    "designname": "Abstract Flow",
    "style": "Abstract",
    "colour": "Blue",
    "short_description": "A vibrant piece.",
    "long_description": "Detailed description...",
    "categories": "Digital,Abstract",
    "cloudflare_image_id": "manual_image_id_1",
    "uploaded_at": "DATETIME_STRING",
    "cloudflare_image_url_thumbnail": "https://imagedelivery.net/[ACCOUNT_HASH]/manual_image_id_1/thumbnail",
    "cloudflare_image_url_medium": "https://imagedelivery.net/[ACCOUNT_HASH]/manual_image_id_1/medium",
    "cloudflare_image_url_original": "https://imagedelivery.net/[ACCOUNT_HASH]/manual_image_id_1/public"
}


Error (401 Unauthorized): Invalid/missing token.
Error (404 Not Found): Design ID not found.

4.2.4. POST /api/upload-url

Description: Generates a Cloudflare Images direct upload URL.
Authentication: Optional (Bearer Token, Admin-only - Recommended).
Request Body (JSON): Optional, can be empty or include metadata if required by Cloudflare Images API directly.
Response (200 OK):
JSON
{
    "id": "cloudflare_image_id",
    "uploadURL": "https://api.cloudflare.com/client/v4/accounts/.../images/v2/direct_upload"
}


Error (401 Unauthorized / 403 Forbidden): If admin protection is enabled and violated.

4.3. Backend Helper Functions & Middleware

hashPassword(password: string): Uses bcryptjs to generate a hash of the input password.
comparePassword(password: string, hash: string): Uses bcryptjs to compare a plain password with a hash.
signToken(payload: object, secret: string): Uses @tsndr/cloudflare-worker-jwt to sign a JWT with a given payload and secret. Payload will include userId, username, isAdmin.
verifyToken(token: string, secret: string): Uses @tsndr/cloudflare-worker-jwt to verify and decode a JWT.
authMiddleware(c: HonoContext, next: Next):
Extracts Bearer token from Authorization header.
Verifies the token using c.env.JWT_SECRET.
If valid, stores decoded payload in c.set('jwtPayload', payload).
If invalid/missing, returns 401 Unauthorized.
adminAuthMiddleware(c: HonoContext, next: Next):
Runs authMiddleware first.
If authentication is successful, checks c.get('jwtPayload').isAdmin.
If isAdmin is not 1, returns 403 Forbidden.

5. Frontend Application Design (React Native)


5.1. Global State Management & API Integration

API Service Layer (src/services/authApi.js, src/services/galleryApi.js):
Uses axios for HTTP requests.
authApi.js: Handles register, login, storeToken, getToken, removeToken.
galleryApi.js:
Configures axios interceptor to automatically add JWT from react-native-keychain to Authorization header for all requests.
Includes getDesigns, getDesignById, getAdminUsers, approveUser functions.
New: getAppSettings(): Calls GET ${WORKER_BASE_URL}/api/settings.
New: updateAppSettings(settings: object): Calls PUT ${WORKER_BASE_URL}/api/admin/settings (requires admin JWT).
Secure Token Storage: react-native-keychain will be used to securely store the JWT on the device's keychain/keystore.
Global App Settings State:
Introduce a global state (e.g., using React Context or a simple useState in App.js and passing down) to store allow_screenshots and allow_downloads values.
This state should be initialized by calling getAppSettings() on app launch.

5.2. Navigation Structure

react-navigation/stack will be used for screen navigation.
Root Navigator Logic:
Upon app launch, a useEffect hook will check for an existing JWT using authApi.getToken().
While checking, a loading/splash screen will be displayed (isLoadingInitialAuth state).
If a token exists, navigate to GalleryScreen (replacing the stack).
If no token, navigate to LoginScreen (as the initial route).

5.3. Screen-Specific Designs


5.3.1. Login Screen

UI Elements: Username TextInput, Password TextInput, Login Button.
Functionality:
handleLogin function: Calls authApi.login.
On success: authApi.storeToken then navigation.navigate('GalleryScreen').
On failure: Alert.alert with error message.
ActivityIndicator for loading state during API call.

5.3.2. Registration Screen

UI Elements: Username TextInput, Password TextInput, Register Button.
Functionality:
handleRegister function: Calls authApi.register.
On success: Alert.alert ("Registration successful! Please wait for admin approval.").
On failure: Alert.alert with error message.
ActivityIndicator for loading state during API call.

5.3.3. Gallery Screen

UI Elements: Search TextInput, Filter buttons/pickers (Style, Colour, Categories), FlatList (or FlashList) to display designs.
Functionality:
Data Fetching: useEffect to call galleryApi.getDesigns with current filters, search query, and pagination parameters.
Pagination: onEndReached handler for FlatList to load more designs by incrementing offset.
Image Display: FastImage component for rendering item.image_url_thumbnail.
Search Debouncing: useEffect with setTimeout/clearTimeout (e.g., 500ms) to trigger search only after user stops typing.
Filtering: Update state variables for selectedStyle, selectedColor, selectedCategory; trigger re-fetch of designs, resetting pagination to page 1.
Navigation: Tapping a design item navigates to DesignDetailScreen, passing item.id as a route parameter.
Screenshot Prevention (Updated):
Modify the useEffect hook to dynamically enable/disable react-native-prevent-screenshot based on the global allow_screenshots setting.
JavaScript
import preventScreenshot from 'react-native-prevent-screenshot';
// ...
useEffect(() => {
    if (!globalAppSettings.allow_screenshots) {
        preventScreenshot.enabled(true);
    } else {
        preventScreenshot.enabled(false);
    }
    return () => {
        preventScreenshot.enabled(false); // Always disable on unmount for safety
    };
}, [globalAppSettings.allow_screenshots]);


Download/Share UI (Updated):
Any template UI elements for download/share that were previously removed/disabled (as per FR-3.4) should now be conditionally rendered or enabled/disabled based on the globalAppSettings.allow_downloads boolean.
Example: A download button would only be visible/active if globalAppSettings.allow_downloads is true.

5.3.4. Design Detail Screen

UI Elements: FastImage for item.image_url_original, Text components for designname, style, colour, short_description, long_description, categories. ScrollView for scrollable content.
Functionality:
Receives designId from route parameters.
useEffect to call galleryApi.getDesignById(designId) and display data.
ActivityIndicator for loading state.
Screenshot Prevention (Updated): Similar to the Gallery Screen, adapt the useEffect to enable/disable react-native-prevent-screenshot based on globalAppSettings.allow_screenshots.
Download/Share UI (Updated): Conditionally render/enable download/share UI elements based on globalAppSettings.allow_downloads.

5.3.5. Admin User Management Screen

UI Elements: FlatList to display users with username and is_approved status. Buttons for "Approve," "Disapprove."
Functionality:
Fetches all users using galleryApi.getAdminUsers().
Buttons call galleryApi.approveUser(userId, status).
Conditionally renders "Approve" button if user is_approved=0, and "Disapprove" if is_approved=1.
Only visible if the logged-in user's JWT payload isAdmin: true.

5.3.6. Admin Settings Screen (New)

UI Elements:
Toggle switches or checkboxes for "Allow Screenshots" and "Allow Downloads."
A "Save Settings" button.
Loading indicator and success/error messages.
Functionality:
Fetches current settings on mount using galleryApi.getAppSettings().
useState hooks to manage the local state of the toggles.
handleSaveSettings function:
Calls galleryApi.updateAppSettings() with the new allow_screenshots and allow_downloads values.
On success, updates the global app settings state and shows a success message.
On failure, shows an error message.
Navigation:
Add AdminSettingsScreen to the React Navigation stack.
Add a conditional button/menu item in the AdminScreen (or GalleryScreen if an admin dashboard exists) that navigates to AdminSettingsScreen, visible only if the logged-in user is an admin.

6. Bulk Image & Metadata Upload Tool (Python Script)

Technology: Python (3.x), pandas (for CSV), requests (for HTTP).
Workflow:
Read design_metadata.csv using pandas.read_csv().
Iterate through each row (design).
For each design:
Get Upload URL: Make POST request to https://[YOUR_WORKER_SUBDOMAIN].workers.dev/api/upload-url.
Upload Image: Make PUT request with multipart/form-data to the uploadURL received.
Save Metadata: Make POST request to https://[YOUR_WORKER_SUBDOMAIN].workers.dev/api/admin/designs including the cloudflare_image_id from the upload URL response and other metadata from CSV.
Authorization: Include Authorization: Bearer [YOUR_ADMIN_JWT_TOKEN] header.
Error Handling: Implement try...except blocks for network errors, API response errors, and file I/O. Consider simple retry logic for transient network issues.
Progress Reporting: Print messages indicating progress (e.g., "Uploading design X of 1000...").

7. Deployment & Release

Backend Deployment:
Cloudflare Worker will be deployed using wrangler deploy.
Initial D1 schema must include the app_settings table.
D1 database and schema managed via wrangler d1 commands.
Secrets (JWT_SECRET, Cloudflare API tokens) will be managed via wrangler secret put.
Deployment will include the new /api/settings and /api/admin/settings endpoints.
Frontend Deployment (Android):
Build System: eas build for Expo templates, or official gradlew assembleRelease for bare React Native.
Artifact: Signed Android App Bundle (AAB).
Distribution: Google Play Console submission. Includes keystore management, app signing, and release track configuration.

