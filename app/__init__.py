"""Application factory for BookShare Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config_name='default'):
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'testing')
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Register blueprints
    from app.routes import books, borrowers, loans, dashboard, recommendations, admin
    
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(borrowers.bp)
    app.register_blueprint(loans.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(admin.bp)
    
    # Register CLI commands
    from app.utils import cli
    cli.register_commands(app)
    
    # Initialize scheduler for reminders (only in non-testing environments)
    if not app.config.get('TESTING', False):
        from app.utils.scheduler_config import init_scheduler
        init_scheduler(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
