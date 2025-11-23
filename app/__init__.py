"""
Retail Trends & Opportunity Engine
Flask application initialization
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize extensions
db = SQLAlchemy()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=None):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from app.config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes.trends import trends_bp
    app.register_blueprint(trends_bp, url_prefix='/api/trends')
    
    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    return app
