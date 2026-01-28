import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()


def create_app(config_name='development'):
    """Application factory"""
    from flask import Flask
    from config import config
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.auctions import auctions_bp
    from app.routes.bids import bids_bp
    from app.routes.favorites import favorites_bp
    from app.routes.users import users_bp
    from app.routes.images import images_bp
    from app.routes.notifications import notifications_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(auctions_bp, url_prefix='/api/auctions')
    app.register_blueprint(bids_bp, url_prefix='/api/bids')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Register socket.io events
    from app.events.socket_events import register_socket_events
    register_socket_events(socketio)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'healthy'}, 200
    
    # Serve uploaded images
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        upload_folder = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), '../uploads'))
        return send_from_directory(upload_folder, filename)
    
    return app
