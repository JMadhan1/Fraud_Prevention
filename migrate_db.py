
from app import app, db
from models import User, OAuth, FraudAlert, Advisor, NetworkConnection, UserReport, AnalysisHistory
import os

def migrate_database():
    """Migrate database to new schema with password authentication"""
    with app.app_context():
        print("Starting database migration...")
        
        # Drop all tables to recreate with new schema
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables with new schema
        print("Creating tables with new schema...")
        db.create_all()
        
        # Initialize sample data
        print("Initializing sample data...")
        from models import init_sample_data
        init_sample_data()
        
        print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
