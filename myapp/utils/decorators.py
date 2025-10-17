from functools import wraps
from flask import abort, request
from flask_login import current_user
from myapp.models import Membership

def server_member_required(f):
    """Decorator to ensure user is a member of the server"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        server_id = kwargs.get('server_id')
        if not server_id:
            abort(400)
        
        membership = Membership.query.filter_by(
            user_id=current_user.id, 
            server_id=server_id
        ).first()
        
        if not membership:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def server_admin_required(f):
    """Decorator to ensure user is an admin or owner of the server"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        server_id = kwargs.get('server_id')
        if not server_id:
            abort(400)
        
        membership = Membership.query.filter_by(
            user_id=current_user.id, 
            server_id=server_id
        ).first()
        
        if not membership or membership.role not in ['owner', 'admin']:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def server_owner_required(f):
    """Decorator to ensure user is the owner of the server"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        server_id = kwargs.get('server_id')
        if not server_id:
            abort(400)
        
        membership = Membership.query.filter_by(
            user_id=current_user.id, 
            server_id=server_id
        ).first()
        
        if not membership or membership.role != 'owner':
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function