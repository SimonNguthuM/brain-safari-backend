import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secure session cookie settings
    SESSION_COOKIE_SAMESITE = "None"  # Required for cross-origin cookies
    SESSION_COOKIE_SECURE = True     # Ensures cookies are sent over HTTPS

    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend', 'build')