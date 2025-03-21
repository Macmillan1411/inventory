from app.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(str(user_id))

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_all_users(cls):
        return cls.query.all()

    @classmethod
    def register(cls, username, password):
        # Check if username already exists
        if cls.get_by_username(username):
            return False

        # Create password hash
        password_hash = generate_password_hash(password)

        # Create new user
        new_user = cls(username=username, password_hash=password_hash)

        # Add to database
        db.session.add(new_user)
        db.session.commit()

        return new_user

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = "products"

    # Available product categories
    CATEGORIES = ["Electronics", "Clothing", "Food", "Books", "Other"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Other")

    def get_value(self):
        """Calculate the total value of this product (price × quantity)"""
        return self.price * self.quantity

    @classmethod
    def get_all(cls):
        """Get all products from the database"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        """Get a product by ID"""
        return cls.query.get(str(id))

    @classmethod
    def get_by_category(cls, category):
        """Get all products in a category"""
        return cls.query.filter_by(category=category).all()

    @classmethod
    def get_categories(cls):
        """Get list of all categories that have products"""
        categories = db.session.query(cls.category).distinct().all()
        categories = [cat[0] for cat in categories]

        # Sort categories (put "Other" last)
        sorted_categories = sorted([c for c in categories if c != "Other"])
        if "Other" in categories:
            sorted_categories.append("Other")

        return sorted_categories

    @classmethod
    def add(cls, name, quantity, price, category):
        """Add a new product"""
        # Validate category
        if not category or category not in cls.CATEGORIES:
            category = "Other"

        new_product = cls(
            name=name, quantity=int(quantity), price=float(price), category=category
        )

        db.session.add(new_product)
        db.session.commit()

        return new_product

    def update(self, name, quantity, price, category):
        """Update this product"""
        self.name = name
        self.quantity = int(quantity)
        self.price = float(price)

        if not category or category not in self.CATEGORIES:
            category = "Other"
        self.category = category

        db.session.commit()

    def delete(self):
        """Delete this product"""
        db.session.delete(self)
        db.session.commit()
