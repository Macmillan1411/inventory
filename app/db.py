from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    app.config.from_object(Config)

    db.init_app(app)

    from app.models import Product, User

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
