import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


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
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'], async_mode='threading')
    
    # Setup logging
    from app.utils.logger import setup_logger
    setup_logger(app)
    
    # Setup JWT blacklist
    from app.utils.jwt_blacklist import JWTBlacklist
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return JWTBlacklist.is_token_blacklisted(jti)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.auctions import auctions_bp
    from app.routes.bids import bids_bp
    from app.routes.favorites import favorites_bp
    from app.routes.users import users_bp
    from app.routes.images import images_bp
    from app.routes.notifications import notifications_bp
    from app.routes.comments import comments_bp
    from app.routes.watchlist import watchlist_bp
    from app.routes.ratings import ratings_bp
    from app.routes.advanced import advanced_bp
    from app.routes.sellers import sellers_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(auctions_bp, url_prefix='/api/auctions')
    app.register_blueprint(bids_bp, url_prefix='/api/bids')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(images_bp, url_prefix='/api/images')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(comments_bp, url_prefix='/api/comments')
    app.register_blueprint(watchlist_bp, url_prefix='/api/watchlist')
    app.register_blueprint(ratings_bp, url_prefix='/api/ratings')
    app.register_blueprint(advanced_bp, url_prefix='/api/advanced')
    app.register_blueprint(sellers_bp, url_prefix='/api/sellers')
    
    # Register socket.io events
    from app.events.socket_events import register_socket_events
    register_socket_events(socketio)
    
    # Start auction scheduler
    if not os.getenv('SKIP_SCHEDULER'):
        from app.utils.scheduler import start_scheduler
        start_scheduler(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register CLI commands
    from app.cli import register_cli_commands
    register_cli_commands(app)
    
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
    
    app.logger.info('Application initialized successfully')
    return app
