from dotenv import load_dotenv
import os

load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SAMESITE = "None"  
    SESSION_COOKIE_SECURE = True    

    STATIC_FOLDER = os.path.join(os.getcwd(), 'frontend/build')