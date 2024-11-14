from flask import Flask, request, jsonify, session
from flask_login import current_user, login_required
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
   
    """Resource for handling feedback collection."""
    def get(self):
        """Fetches all feedback entries."""
        feedback_list = Feedback.query.all()
        return [feedback.to_dict() for feedback in feedback_list], 200

    @login_required
    def post(self):
        """Creates new feedback for a specific resource."""
        data = request.json
        content = data.get("content")
        resource_id = data.get("resource_id")

        if not content or not resource_id:
            return {"message": "Content and resource_id are required"}, 400

        # Create new feedback
        feedback = Feedback(content=content, resource_id=resource_id, user_id=current_user.id)
        db.session.add(feedback)
        db.session.commit()

        return {"message": "Feedback submitted successfully", "feedback_id": feedback.id}, 201


class FeedbackResource(RestResource):
    """Resource for handling individual feedback actions."""
    def get(self, feedback_id):
        """Fetches feedback by ID."""
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return {"message": "Feedback not found"}, 404
        return feedback.to_dict(), 200

    @login_required
    def put(self, feedback_id):
        """Updates the user's feedback."""
        data = request.json
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return {"message": "Feedback not found"}, 404

        # Ensure the feedback is owned by the current user or is updated by an admin
        if feedback.user_id != current_user.id and current_user.role != "Admin":
            return {"message": "You are not authorized to update this feedback"}, 403

        # Update feedback
        feedback.content = data.get("content", feedback.content)
        db.session.commit()

        return {"message": "Feedback updated successfully", "feedback": feedback.to_dict()}, 200

    @login_required
    def delete(self, feedback_id):
        """Deletes the user's feedback."""
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return {"message": "Feedback not found"}, 404

        # Ensure the feedback is owned by the current user or is deleted by an admin
        if feedback.user_id != current_user.id and current_user.role != "Admin":
            return {"message": "You are not authorized to delete this feedback"}, 403

        db.session.delete(feedback)
        db.session.commit()

        return {"message": "Feedback deleted successfully"}, 204

class Comments(RestResource):
    def get(self):
        return {"message": "Comments"}

# Route for accessing quizzes within a module
class Quizzes(RestResource):
    def get(self, module_id):
        quizzes = QuizContent.query.filter_by(module_id=module_id, type="quiz").all()
        return jsonify([
            {
                "id": quiz.id,
                "title": quiz.content_text, 
                "points": quiz.points,
                "created_at": quiz.created_at
            } for quiz in quizzes
        ])
# Route for accessing quiz questions and options
class QuizContent(RestResource):
    def get(self, quiz_id):
        quiz_content = QuizContent.query.filter_by(parent_id=quiz_id).all()
        return jsonify([
            {
                "id": content.id,
                "type": content.type,
                "content_text": content.content_text,
                "points": content.points,
                "is_correct": content.is_correct,
                "created_at": content.created_at
            } for content in quiz_content
        ])

# Route for submitting a quiz and viewing the score
class QuizSubmission(RestResource):
    def post(self, quiz_id):
        data = request.json
        user_id = data.get("user_id")
        user_answers = data.get("answers")

        if not user_id or not user_answers:
            return jsonify({"error": "user_id and answers are required"}), 400  
        
        score = 0
        for answer_id in user_answers:
            answer = QuizContent.query.get(answer_id)
            if answer and answer.is_correct:
                score += answer.points or 0

        submission = QuizSubmission(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            submitted_at=datetime.utcnow()
        )
        db.session.add(submission)
        db.session.commit()

        return jsonify({"quiz_id": quiz_id, "score": score, "submitted_at": submission.submitted_at})

    def get(self, quiz_id, user_id):
        submission = QuizSubmission.query.filter_by(quiz_id=quiz_id, user_id=user_id).first_or_404()
        return jsonify({
            "quiz_id": submission.quiz_id,
            "user_id": submission.user_id,
            "score": submission.score,
            "submitted_at": submission.submitted_at
        })

class Challenges(RestResource):
    def get(self, id):
        return {"message": f"Challenge {id}"}

# class Achievements(Resource):
#     def get(self, user_id):
#         # Query all achievements related to a specific user
#         user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
        
#         achievements = [
#             {
#                 "id": achievement.achievement.id,
#                 "name": achievement.achievement.name,
#                 "description": achievement.achievement.description,
#                 "icon_url": achievement.achievement.icon_url,
#                 "points_required": achievement.achievement.points_required
#             }
#             for achievement in user_achievements
#         ]
        
#         return jsonify(achievements)

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
api.add_resource(FeedbackResource, '/feedback/<int:id>')
api.add_resource(Comments, '/comments')
api.add_resource(Quizzes, '/modules/<int:module_id>/quizzes')
api.add_resource(QuizContent, '/quizzes/<int:quiz_id>/content')
api.add_resource(QuizSubmission, '/quizzes/<int:quiz_id>/submit')
api.add_resource(Challenges, '/challenge/<int:id>')
# api.add_resource(Achievements, '/users/<int:user_id>/achievements')

@app.route("/")
def home():
    return "<h1>Welcome here. You better work!</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
