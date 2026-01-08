"""
Create a test admin user for CovenantIQ
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.utils.security import get_password_hash

DATABASE_URL = "postgresql://postgres:awNZpfEFWbgiqdsnNbQDQnhnNyCtcWXK@nozomi.proxy.rlwy.net:14354/railway"

def create_test_user():
    """Create a test admin user"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "admin@covenantiq.com").first()
        if existing:
            print("✅ Test admin user already exists")
            print(f"   Email: admin@covenantiq.com")
            print(f"   Password: admin123")
            return
        
        # Create admin user
        admin = User(
            email="admin@covenantiq.com",
            hashed_password=get_password_hash("admin123"),
            full_name="CovenantIQ Admin",
            company="CovenantIQ",
            role="admin"
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Test admin user created successfully!")
        print(f"   Email: admin@covenantiq.com")
        print(f"   Password: admin123")
        print(f"   Role: admin")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Creating test admin user...")
    print("=" * 60)
    create_test_user()
    print("=" * 60)
