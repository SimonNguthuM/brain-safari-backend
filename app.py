from flask import Flask, request, jsonify, session
from flask_restful import Resource as RestResource, Api 
from flask_migrate import Migrate
from config import Config
from db import db
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

from models import (
    User, LearningPath, Module, Resource, Feedback,
    Reply, Challenge, Achievement, Leaderboard, ModuleResource,
    UserAchievement, UserLearningPath, UserChallenge,
    QuizContent, QuizSubmission
)

class Signup(RestResource):
    def post(self):
        """Registers a new user with a default 'Learner' role."""
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username and email and password):
            return {"message": "All fields are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "User with this email already exists"}, 400

        new_user = User(username=username, email=email, role='Learner')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return {"message": f"User {username} created successfully"}, 201

class Login(RestResource):
    def post(self):
        """Logs in a user and sets session data."""
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return {"message": "Login successful", "user": user.username}, 200
        else:
            return {"message": "Invalid email or password"}, 401

class ProtectedResource(RestResource):
    """Example protected resource that requires user to be logged in."""
    def get(self):
        if 'user_id' not in session:
            return {"message": "Unauthorized access"}, 401
        return {"message": f"Hello, {session['username']}"}

class UpdateRole(RestResource):
    """Allows an Admin to update a user's role."""
    def put(self):
        data = request.json
        email = data.get('email')
        new_role = data.get('role')

        if new_role not in ['Admin', 'Contributor', 'Learner']:
            return {"message": "Invalid role specified"}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "User not found"}, 404

        user.role = new_role
        db.session.commit()

        return {"message": f"User {user.username}'s role updated to {new_role}"}, 200

class Logout(RestResource):
    def post(self):
        session.clear()
        return {"message": "Logged out successfully"}

class LearningPaths(RestResource):
    def get(self):
        return {"message": "All learning paths"}

class LearningPathDetail(RestResource):
    def get(self, id):
        return {"message": f"Learning path {id}"}

class Modules(RestResource):
    def get(self):
        return {"message": "All modules"}

class ModuleDetail(RestResource):
    def get(self, id):
        return {"message": f"Module {id}"}

class Resources(RestResource):
    def get(self):
        return {"message": "All resources"}

class ResourceDetail(RestResource):
    def get(self, id):
        return {"message": f"Resource {id}"}

class Feedbacks(RestResource):
    def get(self):
        return {"message": "Feedbacks"}

class Comments(RestResource):
    def get(self):
        return {"message": "Comments"}

class Quizzes(RestResource):
    def get(self):
        return {"message": "Quizes"}

class QuizContentResource(RestResource):
    def get(self, id):
        return {"message": f"Quiz {id}"}

class QuizSubmissionResource(RestResource):
    def get(self, id):
        return {"message": f"Quiz {id}"}

class Challenges(RestResource):
    def get(self, id):
        return {"message": f"Challenge {id}"}

class Achievements(RestResource):
    def get(self):
        return {"message": "achievement"}

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(UpdateRole, '/update_role')
api.add_resource(Logout, '/logout')
api.add_resource(LearningPaths, '/learning_paths')
api.add_resource(LearningPathDetail, '/learning_path/<int:id>')
api.add_resource(Modules, '/modules')
api.add_resource(ModuleDetail, '/module/<int:id>')
api.add_resource(Resources, '/resources')
api.add_resource(ResourceDetail, '/resource/<int:id>')
api.add_resource(Feedbacks, '/feedback')
api.add_resource(Comments, '/comments')
api.add_resource(Quizzes, '/modules/<int:module_id>/quizzes')
api.add_resource(QuizContentResource, '/quizzes/<int:quiz_id>/content')
api.add_resource(QuizSubmissionResource, '/quizzes/<int:quiz_id>/submit')
api.add_resource(Challenges, '/challenge/<int:id>')
api.add_resource(Achievements, '/achievements')

@app.route("/")
def home():
    return "<h1>Welcome here. You better work!</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
