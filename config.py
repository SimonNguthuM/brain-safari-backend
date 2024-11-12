import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# import os
# from dotenv import load_dotenv
# from flask import Flask
# from flask_cors import CORS
# from flask_migrate import Migrate
# from flask_restful import Api
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import MetaData

# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)

# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urban_mart.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False

# metadata = MetaData(naming_convention={
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
# })

# # Initialize SQLAlchemy with custom metadata
# db = SQLAlchemy(metadata=metadata)

# # Setup Flask-Migrate for database migrations
# migrate = Migrate(app,db)

# # Initialize Flask-Restful API
# api = Api(app)

# # Enable CORS globally
# CORS(app, supports_credentials=True)

# # Initialize SQLAlchemy with app
# db.init_app(app)