#!/usr/bin/env python3
"""
Database initialization script
"""
from myapp import create_app, db
from myapp.utils.seeds import seed_database

def init_database():
    """Initialize the database with tables and sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Seed with sample data
        seed_database()
        
        print("Database initialization complete!")

if __name__ == "__main__":
    init_database()