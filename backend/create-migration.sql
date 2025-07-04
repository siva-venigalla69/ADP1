-- Migration to add new columns to existing designs table
-- Run this after the initial schema.sql to add new fields

-- Add new columns to designs table
ALTER TABLE designs ADD COLUMN short_description TEXT;
ALTER TABLE designs ADD COLUMN long_description TEXT;
ALTER TABLE designs ADD COLUMN r2_object_key TEXT;
ALTER TABLE designs ADD COLUMN style TEXT;
ALTER TABLE designs ADD COLUMN colour TEXT;
ALTER TABLE designs ADD COLUMN fabric TEXT;
ALTER TABLE designs ADD COLUMN occasion TEXT;
ALTER TABLE designs ADD COLUMN size_available TEXT;
ALTER TABLE designs ADD COLUMN price_range TEXT;
ALTER TABLE designs ADD COLUMN featured INTEGER DEFAULT 0;
ALTER TABLE designs ADD COLUMN status TEXT DEFAULT 'active';
ALTER TABLE designs ADD COLUMN view_count INTEGER DEFAULT 0;
ALTER TABLE designs ADD COLUMN like_count INTEGER DEFAULT 0;
ALTER TABLE designs ADD COLUMN designer_name TEXT;
ALTER TABLE designs ADD COLUMN collection_name TEXT;
ALTER TABLE designs ADD COLUMN season TEXT;
ALTER TABLE designs ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Create unique constraint on r2_object_key (will fail if duplicates exist)
-- Note: SQLite doesn't support adding UNIQUE constraints to existing columns directly
-- So we'll create a unique index instead
CREATE UNIQUE INDEX IF NOT EXISTS idx_designs_r2_object_key_unique ON designs(r2_object_key) WHERE r2_object_key IS NOT NULL;

-- Add new columns to app_settings table
ALTER TABLE app_settings ADD COLUMN watermark_enabled INTEGER DEFAULT 1;
ALTER TABLE app_settings ADD COLUMN max_upload_size INTEGER DEFAULT 10485760;
ALTER TABLE app_settings ADD COLUMN supported_formats TEXT DEFAULT 'jpg,jpeg,png,webp';
ALTER TABLE app_settings ADD COLUMN gallery_per_page INTEGER DEFAULT 20;
ALTER TABLE app_settings ADD COLUMN featured_designs_count INTEGER DEFAULT 10;
ALTER TABLE app_settings ADD COLUMN maintenance_mode INTEGER DEFAULT 0;
ALTER TABLE app_settings ADD COLUMN app_version TEXT DEFAULT '1.0.0';

-- Create new tables
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    design_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE,
    UNIQUE(user_id, design_id)
);

CREATE TABLE IF NOT EXISTS design_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_id INTEGER NOT NULL,
    user_id INTEGER,
    ip_address TEXT,
    viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon_url TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create new indexes
CREATE INDEX IF NOT EXISTS idx_designs_style ON designs(style);
CREATE INDEX IF NOT EXISTS idx_designs_colour ON designs(colour);
CREATE INDEX IF NOT EXISTS idx_designs_fabric ON designs(fabric);
CREATE INDEX IF NOT EXISTS idx_designs_occasion ON designs(occasion);
CREATE INDEX IF NOT EXISTS idx_designs_featured ON designs(featured);
CREATE INDEX IF NOT EXISTS idx_designs_status ON designs(status);
CREATE INDEX IF NOT EXISTS idx_designs_updated_at ON designs(updated_at);
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_design_id ON user_favorites(design_id);
CREATE INDEX IF NOT EXISTS idx_design_views_design_id ON design_views(design_id);
CREATE INDEX IF NOT EXISTS idx_design_views_viewed_at ON design_views(viewed_at);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_sort_order ON categories(sort_order);

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

-- Update existing app_settings with new default values
UPDATE app_settings SET 
    watermark_enabled = 1,
    max_upload_size = 10485760,
    supported_formats = 'jpg,jpeg,png,webp',
    gallery_per_page = 20,
    featured_designs_count = 10,
    maintenance_mode = 0,
    app_version = '1.0.0'
WHERE id = 1; 