# scripts/setup_db.py
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from app.models import Base

def setup_database():
    """Initialize database"""
    print("🔧 Setting up database...")
    
    # Use SQLite for development
    engine = create_engine('sqlite:///./image_selector.db')
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database setup complete!")
    print("📁 Created: image_selector.db")

if __name__ == "__main__":
    setup_database()