# Design Gallery Backend

This is the Cloudflare Workers backend for the Design Gallery Android App.

## Tech Stack
- Cloudflare Workers (Hono framework)
- Cloudflare D1 (SQLite database)
- Cloudflare Images (for image storage)
- TypeScript
- bcryptjs (password hashing)
- JWT authentication

## Setup Instructions

### Prerequisites
1. Install [Node.js](https://nodejs.org/) (v18 or later)
2. Install [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/)
   ```bash
   npm install -g wrangler
   ```
3. Authenticate with Cloudflare:
   ```bash
   wrangler login
   ```

### Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create D1 Database:**
   ```bash
   npm run db:create
   ```
   This will output a database ID. Copy it and update `wrangler.toml`:
   ```toml
   [[env.production.d1_databases]]
   binding = "DB"
   database_name = "design-gallery-db"
   database_id = "YOUR_DATABASE_ID_HERE"
   ```

3. **Set up secrets:**
   ```bash
   wrangler secret put JWT_SECRET
   # Enter a strong secret when prompted (e.g., generated UUID)
   
   # Optional: For Cloudflare Images integration
   wrangler secret put CLOUDFLARE_ACCOUNT_ID
   wrangler secret put CLOUDFLARE_API_TOKEN
   ```

4. **Initialize database schema:**
   ```bash
   npm run db:execute-local  # For local development
   npm run db:execute        # For production
   ```

5. **Start development server:**
   ```bash
   npm run dev
   ```

### API Endpoints

#### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login

#### Designs
- `GET /api/designs` - List designs (auth required)
- `GET /api/designs/:id` - Get design details (auth required)
- `POST /api/admin/designs` - Create design (admin only)

#### Admin
- `GET /api/admin/users` - List all users (admin only)
- `POST /api/admin/approve-user` - Approve/disapprove user (admin only)

#### Settings
- `GET /api/settings` - Get app settings (public)
- `PUT /api/admin/settings` - Update app settings (admin only)

#### Images
- `POST /api/upload-url` - Generate upload URL (admin only)

### Default Admin User
- Username: `admin`
- Password: `admin123`

**Important:** Change the admin password after first login!

### Deployment
```bash
npm run deploy
```

## Project Structure
```
backend/
├── src/
│   └── index.ts          # Main worker code
├── wrangler.toml         # Cloudflare Workers configuration
├── schema.sql           # Database schema
├── package.json         # Node.js dependencies
└── README.md           # This file
```

## Environment Variables
- `JWT_SECRET` - Secret for JWT token signing
- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID
- `CLOUDFLARE_API_TOKEN` - API token for Cloudflare Images

## Next Steps
1. Test authentication endpoints
2. Implement design management features
3. Add image upload functionality
4. Set up frontend integration 