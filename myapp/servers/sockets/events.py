from flask_socketio import join_room, leave_room, emit, disconnect
from myapp.extensions import socketio
from flask_login import current_user
from myapp import db
from myapp.models import Message, Membership
from datetime import datetime

@socketio.on('join')
def handle_join(data):
    """Handle user joining a channel room"""
    if not current_user.is_authenticated:
        return False
    
    room = data.get('room')
    if not room:
        return False
    
    # Verify user is a member of the server
    try:
        server_id = int(room.split('_')[0])  # Room format: serverid_channelid
        membership = Membership.query.filter_by(user_id=current_user.id, server_id=server_id).first()
        if not membership:
            return False
    except (ValueError, IndexError):
        return False
    
    join_room(room)
    emit('message', {
        'username': 'System',
        'content': f'{current_user.username} joined the channel.',
        'timestamp': datetime.now().strftime('%H:%M'),
        'type': 'system'
    }, room=room)

@socketio.on('leave')
def handle_leave(data):
    """Handle user leaving a channel room"""
    if not current_user.is_authenticated:
        return False
    
    room = data.get('room')
    if room:
        leave_room(room)
        emit('message', {
            'username': 'System',
            'content': f'{current_user.username} left the channel.',
            'timestamp': datetime.now().strftime('%H:%M'),
            'type': 'system'
        }, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a message to a channel"""
    if not current_user.is_authenticated:
        return False
    
    room = data.get('room')
    content = data.get('content', '').strip()
    
    if not room or not content:
        return False
    
    # Verify user is a member of the server
    try:
        server_id = int(room.split('_')[0])
        membership = Membership.query.filter_by(user_id=current_user.id, server_id=server_id).first()
        if not membership:
            return False
    except (ValueError, IndexError):
        return False
    
    # Save message to database
    try:
        channel_id = int(room.split('_')[1])
        message = Message(
            content=content,
            user_id=current_user.id,
            channel_id=channel_id
        )
        db.session.add(message)
        db.session.commit()
        
        # Emit message to room
        msg_data = {
            'id': message.id,
            'username': current_user.username,
            'content': content,
            'timestamp': message.created_at.strftime('%H:%M'),
            'type': 'user'
        }
        emit('message', msg_data, room=room)
        
    except (ValueError, IndexError):
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnection"""
    # Could add logic here to notify about user going offline
    pass