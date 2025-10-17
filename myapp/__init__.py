from flask import Flask
from myapp.extensions import db, login_manager, socketio
from myapp.auth import auth
from myapp.main import main
from myapp.servers import servers

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(servers, url_prefix="/servers")

    return app