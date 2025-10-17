#!/usr/bin/env python3
"""
Shortcut to launch Flask-SocketIO server
"""
from myapp import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", allow_unsafe_werkzeug=True)