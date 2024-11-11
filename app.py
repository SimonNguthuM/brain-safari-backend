from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


from models import User, LearningPath, Module, Resource, Feedback, Comment, Reply, Challenge, Achievement, Leaderboard, ModuleResource, UserAchievement, UserLearningPath, UserChallenge, QuizContent, QuizSubmission

if __name__ == '__main__':
    app.run()
