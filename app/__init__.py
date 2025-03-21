from flask import Flask
from app.config import Config
from flask_login import LoginManager
from app.db import init_db, db

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config["SECRET_KEY"] = (
    "your-secret-key-change-this"  # Change this to a random string
)

# Initialize database
init_db(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# User loader function
@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    return User.get_by_id(user_id)


from app import routes as routes
