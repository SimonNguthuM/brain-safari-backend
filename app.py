from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_migrate import Migrate
from config import Config
from db import db  

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

from models import (
    User, LearningPath, Module, Resource, 
    Challenge, Achievement, Leaderboard, ModuleResource, 
    UserAchievement, UserLearningPath, UserChallenge, 
    QuizContent, QuizSubmission
)

class Login(Resource):
    def post(self):
        return {"message": "Login successful"}

class Signup(Resource):
    def post(self):
        return {"message": "Signup successful"}

class LearningPaths(Resource):
    def get(self):
        return {"message": "All learning paths"}

class LearningPathDetail(Resource):
    def get(self, id):
        return {"message": f"Learning path {id}"}

class Modules(Resource):
    def get(self):
        return {"message": "All modules"}

class ModuleDetail(Resource):
    def get(self, id):
        return {"message": f"Module {id}"}

class Resources(Resource):
    def get(self):
        return {"message": "All resources"}

class ResourceDetail(Resource):
    def get(self, id):
        return {"message": f"Resource {id}"}

class Feedbacks(Resource):
    def get(self):
        return {"message": "Feedbacks"}

# class Comments(Resource):
#     def get(self):
#         return {"message": "Comments"}

class Quizzes(Resource):
    def get(self, id):
        return {"message": f"Quiz {id}"}

class Challenges(Resource):
    def get(self, id):
        return {"message": f"Challenge {id}"}

class Dashboard(Resource):
    def get(self):
        return {"message": "Dashboard"}

api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(LearningPaths, '/learning_paths')
api.add_resource(LearningPathDetail, '/learning_path/<int:id>')
api.add_resource(Modules, '/modules')
api.add_resource(ModuleDetail, '/module/<int:id>')
api.add_resource(Resources, '/resources')
api.add_resource(ResourceDetail, '/resource/<int:id>')
api.add_resource(Feedbacks, '/feedback')
# api.add_resource(Comments, '/comments')
api.add_resource(Quizzes, '/quiz/<int:id>')
api.add_resource(Challenges, '/challenge/<int:id>')
api.add_resource(Dashboard, '/dashboard')

@app.route("/")
def home():
    return "<h1>Welcome back</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
