# Design Gallery Project

A modern React Native application for showcasing Indian traditional wear designs, built with Cloudflare services.

## 🚀 Quick Start

### Automated Setup
```bash
# Full setup with all services
./setup.sh

# Backend only
./setup.sh --backend-only

# Frontend only  
./setup.sh --frontend-only

# Deploy after setup
./setup.sh --deploy

# Get help
./setup.sh --help
```

### Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   npm install
   wrangler d1 create design-gallery-db
   wrangler r2 bucket create design-gallery-images
   wrangler secret put JWT_SECRET
   npm run deploy
   ```

2. **Frontend Setup**
   ```bash
   cd AD-APP
   npm install
   npm start
   ```

## 📚 Documentation

**📖 [COMPREHENSIVE_PROJECT_GUIDE.md](./COMPREHENSIVE_PROJECT_GUIDE.md)** - Complete project documentation

This guide contains everything you need:
- Project architecture
- Setup instructions
- API documentation
- Frontend integration
- Testing procedures
- Troubleshooting
- Best practices

## 🏗️ Architecture

- **Backend**: Cloudflare Workers + D1 + R2
- **Frontend**: React Native + Expo
- **Database**: Cloudflare D1 (SQLite)
- **Storage**: Cloudflare R2
- **Authentication**: JWT

## 🧪 Testing

```bash
cd backend
npm test                    # Run all tests
npm run test:auth          # Auth tests only
npm run test:designs       # Design tests only
npm run test:admin         # Admin tests only
```

## 📱 Features

- ✅ User authentication
- ✅ Design gallery with filtering
- ✅ Image upload to R2
- ✅ Admin management
- ✅ Favorites system
- ✅ Analytics tracking
- ✅ Search functionality
- ✅ Screenshot prevention

## 🔧 Development

```bash
# Backend development
cd backend && npm run dev

# Frontend development  
cd AD-APP && npm start

# Database migration
cd backend && npm run db:migrate
```

## 📂 Project Structure

```
├── backend/                 # Cloudflare Workers API
│   ├── src/index.ts        # Main worker code
│   ├── schema.sql          # Database schema
│   ├── create-migration.sql # Database migration
│   ├── test-api.js         # API testing script
│   └── wrangler.toml       # Cloudflare config
├── AD-APP/                 # React Native frontend
├── setup.sh                # Automated setup script
├── COMPREHENSIVE_PROJECT_GUIDE.md # Complete documentation
└── README.md               # This file
```

## 🆘 Support

For detailed information, troubleshooting, and advanced configuration, see the [Comprehensive Project Guide](./COMPREHENSIVE_PROJECT_GUIDE.md).

---

**Happy coding! 🎨** 