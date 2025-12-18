"""
Database initialization script
Run this script to initialize the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.database import init_db, reset_db, AuthService, SessionLocal
from app.api.models.user import UserRegister
from shared.logger import get_logger

logger = get_logger(__name__)


def create_test_users():
    """Create test users for development"""
    db = SessionLocal()
    try:
        # Create test user
        test_user = UserRegister(
            username="test",
            password="test",
            name="Test",
            lastname="User"
        )
        
        user = AuthService.create_user(db, test_user)
        if user:
            logger.info(f"Test user created: {user.username} (ID: {user.user_id})")
        else:
            logger.warning("Test user already exists")
        
        # Create admin user
        admin_user = UserRegister(
            username="admin",
            password="admin123",
            name="Admin",
            lastname="User"
        )
        
        user = AuthService.create_user(db, admin_user)
        if user:
            logger.info(f"Admin user created: {user.username} (ID: {user.user_id})")
        else:
            logger.warning("Admin user already exists")
            
    finally:
        db.close()


def main():
    """Main initialization function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Behflow database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (drop all tables and recreate)"
    )
    parser.add_argument(
        "--no-test-data",
        action="store_true",
        help="Skip creating test users"
    )
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            logger.warning("Resetting database...")
            reset_db()
        else:
            logger.info("Initializing database...")
            init_db()
        
        if not args.no_test_data:
            logger.info("Creating test users...")
            create_test_users()
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
