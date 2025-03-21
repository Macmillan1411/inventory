from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app"""
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Import models to ensure they're registered with SQLAlchemy
    from app.models import Product, User

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
