from flask import Flask
import os
from app.extensions import db, migrate, socketio
from app.services.sync_manager import SyncManager
from app.services.conflict_resolver import ConflictResolver
from app.routes.socketio_events import register_socketio_events

def create_app():
    """
    Flask application factory.
    Sets up Flask, SQLAlchemy, Flask-Migrate, and registers blueprints.
    """
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Use instance/app.db as the database file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../instance/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    # Import models so Flask-Migrate can detect them
    from app.models import sync_event
    from app.models import sync_audit_log
    from app.models import user

    # Register blueprints (add more as needed)
    from app.routes.sync_routes import sync_bp
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(sync_bp)
    app.register_blueprint(auth_bp)

    # Register SocketIO event handlers
    register_socketio_events(socketio)

    # Initialize core services (can be injected as needed)
    app.sync_manager = SyncManager()
    app.conflict_resolver = ConflictResolver()

    return app
