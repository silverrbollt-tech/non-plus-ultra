import random
import string
from datetime import datetime, timedelta

def generate_join_code(length=6):
    """Generate a random server join code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_invite_code(length=8):
    """Generate a random invite code"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def format_datetime(dt):
    """Format datetime for display"""
    if not dt:
        return ""
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days == 0:
        return dt.strftime('%H:%M')
    elif diff.days == 1:
        return 'Yesterday'
    elif diff.days < 7:
        return dt.strftime('%A')
    else:
        return dt.strftime('%m/%d/%Y')

def is_valid_server_code(code):
    """Validate server join code format"""
    if not code or len(code) != 6:
        return False
    return code.isalnum() and code.isupper()