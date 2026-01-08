"""
Database initialization script for CovenantIQ production.
Creates all tables in the PostgreSQL database.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from app.database import Base
from app.models import User, LoanAgreement, Covenant, CovenantMeasurement, Alert, BorrowerFinancial

def setup_database(database_url: str):
    """Create all tables in the database"""
    
    print("🔗 Connecting to database...")
    engine = create_engine(database_url)
    
    # Test connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Create all tables
    print("\n📊 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            
        print(f"\n📋 Created {len(tables)} tables:")
        for table in tables:
            print(f"   • {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    # Production database URL
    DATABASE_URL = "postgresql://postgres:awNZpfEFWbgiqdsnNbQDQnhnNyCtcWXK@nozomi.proxy.rlwy.net:14354/railway"
    
    print("=" * 60)
    print("CovenantIQ - Database Setup")
    print("=" * 60)
    
    success = setup_database(DATABASE_URL)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        print("\nYour CovenantIQ database is ready for production.")
        print("You can now deploy your backend to Railway.")
    else:
        print("\n❌ Database setup failed. Please check the errors above.")
        sys.exit(1)
