from flask import Flask
from flask_migrate import Migrate
from config import Config
from db import db  

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)  
migrate = Migrate(app, db)

from models import User, LearningPath, Module, Resource, Feedback, Comment, Reply, Challenge, Achievement, Leaderboard, ModuleResource, UserAchievement, UserLearningPath, UserChallenge, QuizContent, QuizSubmission

@app.route("/")
def home():
    return "<h1>Welcome back</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
