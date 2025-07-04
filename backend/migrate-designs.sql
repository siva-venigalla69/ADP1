-- Drop the existing designs table
DROP TABLE IF EXISTS designs;

-- Recreate the designs table with the new schema
CREATE TABLE IF NOT EXISTS designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    image_url TEXT NOT NULL, -- URL for the design image
    category TEXT NOT NULL, -- Single category
    tags TEXT, -- Comma-separated tags
    created_by INTEGER DEFAULT 1, -- User ID who created this design
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_designs_category ON designs(category);
CREATE INDEX IF NOT EXISTS idx_designs_title ON designs(title);
CREATE INDEX IF NOT EXISTS idx_designs_created_by ON designs(created_by); 