from myapp import db
from myapp.models import User, Server, Channel, Membership
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    """Seed the database with sample data"""
    
    # Create sample users
    users = [
        User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('password123')
        ),
        User(
            username='alice',
            email='alice@example.com',
            password_hash=generate_password_hash('password123')
        ),
        User(
            username='bob',
            email='bob@example.com',
            password_hash=generate_password_hash('password123')
        )
    ]
    
    for user in users:
        existing_user = User.query.filter_by(username=user.username).first()
        if not existing_user:
            db.session.add(user)
    
    db.session.commit()
    
    # Create sample server
    admin = User.query.filter_by(username='admin').first()
    if admin:
        server = Server(
            name='Welcome Server',
            description='A sample server to get you started!',
            join_code='WELCOME',
            owner_id=admin.id
        )
        db.session.add(server)
        db.session.flush()
        
        # Create channels
        channels = [
            Channel(name='general', server_id=server.id),
            Channel(name='random', server_id=server.id),
            Channel(name='announcements', server_id=server.id)
        ]
        
        for channel in channels:
            db.session.add(channel)
        
        # Add all users as members
        all_users = User.query.all()
        for user in all_users:
            membership = Membership(
                user_id=user.id,
                server_id=server.id,
                role='member' if user.id != admin.id else 'owner'
            )
            db.session.add(membership)
    
    db.session.commit()
    print("Database seeded successfully!")