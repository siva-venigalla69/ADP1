#!/usr/bin/env python3
"""
Create admin user with environment-based password
"""
import os
import bcrypt
from app.core.database import db_manager
from app.core.config import settings

async def create_admin_user():
    """Create admin user from environment variables."""
    
    # Get admin credentials from environment
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if not admin_password:
        print("❌ ADMIN_PASSWORD environment variable not set")
        return False
    
    # Hash password
    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Check if admin already exists
    existing_admin = await db_manager.get_by_field_single("users", "username", admin_username)
    
    if existing_admin:
        # Update existing admin password
        await db_manager.update("users", existing_admin["id"], {
            "password_hash": password_hash
        })
        print(f"✅ Updated admin password for: {admin_username}")
    else:
        # Create new admin
        admin_data = {
            "username": admin_username,
            "password_hash": password_hash,
            "is_admin": True,
            "is_approved": True
        }
        
        await db_manager.create("users", admin_data)
        print(f"✅ Created new admin user: {admin_username}")
    
    return True

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_admin_user()) 