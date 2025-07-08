#!/usr/bin/env python3
"""
Local Database Setup Script for Design Gallery Backend
Creates a local SQLite database with test data for development
"""

import sqlite3
import bcrypt
import os
from datetime import datetime


def create_local_database():
    """Create local SQLite database with schema and test data."""
    
    # Database file
    db_file = "test_local.db"
    
    # Remove existing database
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing database: {db_file}")
    
    # Create connection
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("📊 Creating local test database...")
    
    # Read and execute schema
    try:
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
        print("✅ Database schema applied")
    except FileNotFoundError:
        print("❌ schema.sql not found. Please run this script from the backend directory.")
        return False
    
    # Create admin user (password: YOUR_CUSTOM_PASSWORD)
    print("👤 Creating admin user...")
    admin_password = "SecureAdmin2024!"  # Your chosen password
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO users (username, password_hash, is_admin, is_approved) VALUES (?, ?, 1, 1)",
        ('admin', password_hash)
    )
    
    # Create test user (password: test123)
    test_user_hash = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO users (username, password_hash, is_admin, is_approved) VALUES (?, ?, 0, 1)",
        ('testuser', test_user_hash)
    )
    
    # Create pending user (password: pending123)
    pending_user_hash = bcrypt.hashpw('pending123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO users (username, password_hash, is_admin, is_approved) VALUES (?, ?, 0, 0)",
        ('pendinguser', pending_user_hash)
    )
    
    print("✅ Test users created")
    
    # Add test designs
    print("🎨 Adding test designs...")
    test_designs = [
        ('Elegant Red Saree', 'Beautiful traditional red saree perfect for weddings', 'Stunning red saree with intricate gold embroidery work', 'Detailed description of this beautiful traditional saree with rich fabric and elegant design...', 'test/saree-red-1.jpg', 'saree', 'traditional', 'red', 'silk', 'wedding', 'S,M,L,XL', '15000-25000', 'traditional,wedding,elegant', 1, 'Priya Designs', 'Wedding Collection', 'winter'),
        
        ('Modern Blue Lehenga', 'Contemporary blue lehenga for special occasions', 'Trendy blue lehenga with modern cut', 'This modern lehenga features contemporary styling with traditional elements...', 'test/lehenga-blue-1.jpg', 'lehenga', 'modern', 'blue', 'georgette', 'party', 'S,M,L', '20000-30000', 'modern,party,trendy', 0, 'Fashion Studio', 'Party Collection', 'summer'),
        
        ('Casual Green Kurti', 'Comfortable daily wear kurti', 'Perfect for everyday comfort and style', 'Light and comfortable kurti suitable for daily wear with elegant design...', 'test/kurti-green-1.jpg', 'kurti', 'casual', 'green', 'cotton', 'daily', 'XS,S,M,L,XL', '1500-3000', 'casual,comfort,daily', 0, 'Cotton Crafts', 'Daily Wear', 'all-season'),
        
        ('Golden Wedding Saree', 'Luxurious golden saree for weddings', 'Premium wedding saree with rich golden work', 'Exquisite wedding saree with intricate golden embroidery and premium fabric...', 'test/saree-golden-1.jpg', 'saree', 'traditional', 'gold', 'silk', 'wedding', 'S,M,L', '35000-50000', 'luxury,wedding,premium', 1, 'Royal Weaves', 'Bridal Collection', 'winter'),
        
        ('Pink Party Dress', 'Stylish pink dress for parties', 'Modern pink dress with elegant design', 'Contemporary party dress with modern styling and comfortable fit...', 'test/dress-pink-1.jpg', 'dress', 'modern', 'pink', 'crepe', 'party', 'S,M,L', '8000-12000', 'modern,party,stylish', 0, 'Urban Fashion', 'Party Wear', 'summer'),
        
        ('Traditional Yellow Saree', 'Classic yellow saree for festivals', 'Bright yellow saree perfect for celebrations', 'Traditional yellow saree with classic design perfect for festivals and celebrations...', 'test/saree-yellow-1.jpg', 'saree', 'traditional', 'yellow', 'cotton', 'festival', 'S,M,L,XL', '5000-8000', 'traditional,festival,bright', 0, 'Heritage Textiles', 'Festival Collection', 'all-season'),
        
        ('Black Evening Gown', 'Elegant black gown for evening events', 'Sophisticated black gown', 'Elegant evening gown with sophisticated design perfect for formal events...', 'test/gown-black-1.jpg', 'gown', 'formal', 'black', 'silk', 'formal', 'S,M,L', '18000-25000', 'formal,evening,elegant', 1, 'Elite Couture', 'Evening Collection', 'all-season'),
        
        ('White Casual Kurti', 'Simple white kurti for everyday wear', 'Clean and simple design', 'Comfortable white kurti with minimalist design perfect for daily wear...', 'test/kurti-white-1.jpg', 'kurti', 'casual', 'white', 'cotton', 'daily', 'XS,S,M,L,XL,XXL', '1200-2500', 'casual,simple,daily', 0, 'Simple Elegance', 'Basics Collection', 'all-season'),
        
        ('Purple Festive Lehenga', 'Rich purple lehenga for festivals', 'Vibrant purple lehenga with traditional work', 'Beautiful purple lehenga with rich embroidery work perfect for festive occasions...', 'test/lehenga-purple-1.jpg', 'lehenga', 'traditional', 'purple', 'silk', 'festival', 'S,M,L', '25000-35000', 'traditional,festival,rich', 1, 'Festive Creations', 'Festival Special', 'winter'),
        
        ('Orange Summer Dress', 'Bright orange dress for summer', 'Light and breezy summer dress', 'Comfortable summer dress with vibrant orange color and breathable fabric...', 'test/dress-orange-1.jpg', 'dress', 'casual', 'orange', 'cotton', 'casual', 'S,M,L,XL', '3000-5000', 'summer,casual,bright', 0, 'Summer Vibes', 'Summer Collection', 'summer')
    ]
    
    for design in test_designs:
        cursor.execute(
            """INSERT INTO designs (title, description, short_description, long_description, r2_object_key, 
               category, style, colour, fabric, occasion, size_available, price_range, tags, featured, 
               designer_name, collection_name, season) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            design
        )
    
    # Add some favorites for test user
    cursor.execute("INSERT INTO user_favorites (user_id, design_id) VALUES (2, 1)")
    cursor.execute("INSERT INTO user_favorites (user_id, design_id) VALUES (2, 4)")
    cursor.execute("INSERT INTO user_favorites (user_id, design_id) VALUES (2, 7)")
    
    # Add app settings
    settings_data = [
        ('app_name', 'Design Gallery', 'Application name'),
        ('app_version', '1.0.0', 'Application version'),
        ('maintenance_mode', 'false', 'Maintenance mode flag'),
        ('max_designs_per_user', '100', 'Maximum designs per user'),
        ('featured_designs_limit', '10', 'Number of featured designs to show')
    ]
    
    for setting in settings_data:
        cursor.execute(
            "INSERT INTO app_settings (key, value, description) VALUES (?, ?, ?)",
            setting
        )
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Test designs added")
    print("✅ User favorites added")
    print("✅ App settings added")
    print(f"\n🎉 Local test database created successfully: {db_file}")
    
    # Print summary
    print("\n📋 Database Summary:")
    print("=" * 40)
    print("👥 Users:")
    print("  • admin / SecureAdmin2024! (Admin, Approved)")
    print("  • testuser / test123 (User, Approved)")  
    print("  • pendinguser / pending123 (User, Pending)")
    print("\n🎨 Designs: 10 test designs with various categories")
    print("❤️ Favorites: 3 favorites for testuser")
    print("⚙️ Settings: 5 app configuration settings")
    
    print(f"\n🔧 To use this database, add to your .env file:")
    print(f"DATABASE_URL=sqlite:///./{db_file}")
    
    return True


if __name__ == "__main__":
    print("🗄️ Design Gallery - Local Database Setup")
    print("=" * 50)
    
    # Check if bcrypt is available
    try:
        import bcrypt
    except ImportError:
        print("❌ bcrypt not found. Install with: pip install bcrypt")
        exit(1)
    
    # Create database
    if create_local_database():
        print("\n✅ Setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Update your .env file with the DATABASE_URL")
        print("2. Start the server: uvicorn app.main:app --reload")
        print("3. Test with: python quick_test.py")
    else:
        print("\n❌ Setup failed!")
        exit(1) 