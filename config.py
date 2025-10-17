import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///myapp.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Socket.IO settings
    SOCKETIO_ASYNC_MODE = 'threading'