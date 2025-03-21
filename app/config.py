import os


class Config:
    """Application configuration"""

    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
