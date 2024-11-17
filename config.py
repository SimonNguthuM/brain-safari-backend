import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SAMESITE = "None"  
    SESSION_COOKIE_SECURE = True    

    STATIC_FOLDER = os.path.join(os.getcwd(), 'build')