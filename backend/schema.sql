-- Users table for authentication and authorization
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0, -- 0 for false, 1 for true
    is_approved INTEGER DEFAULT 0, -- 0 for false, 1 for true (awaiting admin approval)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced Designs table for storing design metadata with R2 integration
CREATE TABLE IF NOT EXISTS designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    short_description TEXT, -- Brief description for cards
    long_description TEXT, -- Detailed description for detail view
    image_url TEXT NOT NULL, -- URL for the design image (R2 public URL)
    r2_object_key TEXT UNIQUE NOT NULL, -- R2 object key for the stored image
    category TEXT NOT NULL, -- Single category (sarees, lehengas, suits, etc.)
    style TEXT, -- Style type (traditional, modern, fusion, etc.)
    colour TEXT, -- Primary color of the design
    fabric TEXT, -- Fabric type (silk, cotton, chiffon, etc.)
    occasion TEXT, -- Occasion (wedding, party, casual, formal, etc.)
    size_available TEXT, -- Available sizes (S,M,L,XL or custom)
    price_range TEXT, -- Price range (budget, mid-range, premium)
    tags TEXT, -- Comma-separated tags for additional categorization
    featured INTEGER DEFAULT 0, -- 0 for normal, 1 for featured designs
    status TEXT DEFAULT 'active', -- active, inactive, draft
    view_count INTEGER DEFAULT 0, -- Track popularity
    like_count INTEGER DEFAULT 0, -- Track user engagement
    designer_name TEXT, -- Designer or brand name
    collection_name TEXT, -- Collection or series name
    season TEXT, -- Season (spring, summer, monsoon, winter, festival)
    created_by INTEGER DEFAULT 1, -- User ID who created this design
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Enhanced App settings table for global application settings
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY DEFAULT 1, -- Ensure only one row
    allow_screenshots INTEGER DEFAULT 0, -- 0 for false (prevent), 1 for true (allow)
    allow_downloads INTEGER DEFAULT 0, -- 0 for false (prevent), 1 for true (allow)
    watermark_enabled INTEGER DEFAULT 1, -- Enable watermark on images
    max_upload_size INTEGER DEFAULT 10485760, -- Max upload size in bytes (10MB)
    supported_formats TEXT DEFAULT 'jpg,jpeg,png,webp', -- Supported image formats
    gallery_per_page INTEGER DEFAULT 20, -- Items per page in gallery
    featured_designs_count INTEGER DEFAULT 10, -- Number of featured designs to show
    maintenance_mode INTEGER DEFAULT 0, -- 0 for normal, 1 for maintenance
    app_version TEXT DEFAULT '1.0.0', -- Current app version
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User favorites table for tracking user preferences
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    design_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE,
    UNIQUE(user_id, design_id) -- Prevent duplicate favorites
);

-- Design views table for analytics
CREATE TABLE IF NOT EXISTS design_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_id INTEGER NOT NULL,
    user_id INTEGER, -- NULL for anonymous views
    ip_address TEXT, -- Track unique views
    viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Categories table for dynamic category management
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon_url TEXT, -- Icon for the category
    sort_order INTEGER DEFAULT 0, -- For custom ordering
    is_active INTEGER DEFAULT 1, -- Enable/disable categories
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_designs_category ON designs(category);
CREATE INDEX IF NOT EXISTS idx_designs_style ON designs(style);
CREATE INDEX IF NOT EXISTS idx_designs_colour ON designs(colour);
CREATE INDEX IF NOT EXISTS idx_designs_fabric ON designs(fabric);
CREATE INDEX IF NOT EXISTS idx_designs_occasion ON designs(occasion);
CREATE INDEX IF NOT EXISTS idx_designs_featured ON designs(featured);
CREATE INDEX IF NOT EXISTS idx_designs_status ON designs(status);
CREATE INDEX IF NOT EXISTS idx_designs_title ON designs(title);
CREATE INDEX IF NOT EXISTS idx_designs_created_by ON designs(created_by);
CREATE INDEX IF NOT EXISTS idx_designs_r2_object_key ON designs(r2_object_key);
CREATE INDEX IF NOT EXISTS idx_designs_created_at ON designs(created_at);
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_design_id ON user_favorites(design_id);
CREATE INDEX IF NOT EXISTS idx_design_views_design_id ON design_views(design_id);
CREATE INDEX IF NOT EXISTS idx_design_views_viewed_at ON design_views(viewed_at);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_sort_order ON categories(sort_order);

-- Insert default app settings
INSERT OR IGNORE INTO app_settings (id, allow_screenshots, allow_downloads, watermark_enabled, max_upload_size, supported_formats, gallery_per_page, featured_designs_count, maintenance_mode, app_version) 
VALUES (1, 0, 0, 1, 10485760, 'jpg,jpeg,png,webp', 20, 10, 0, '1.0.0');

-- Insert default admin user (password: admin123)
-- Password hash for 'admin123' using bcrypt with salt rounds 10
INSERT OR IGNORE INTO users (username, password_hash, is_admin, is_approved) 
VALUES ('admin', '$2b$10$bNg5gQ27rPgH3gkaCVBqxuNDdI3eLDG5V/g6SmSVkcr0N1up/Pu1K', 1, 1);

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description, sort_order, is_active) VALUES
('Sarees', 'Traditional Indian sarees in various styles and fabrics', 1, 1),
('Lehengas', 'Elegant lehengas for weddings and special occasions', 2, 1),
('Suits', 'Designer suits and salwar kameez', 3, 1),
('Gowns', 'Western and Indo-western gowns', 4, 1),
('Kurtis', 'Casual and formal kurtis', 5, 1),
('Dupattas', 'Beautiful dupattas and stoles', 6, 1),
('Blouses', 'Designer blouses and crop tops', 7, 1),
('Accessories', 'Jewelry and fashion accessories', 8, 1); 