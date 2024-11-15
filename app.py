from functools import wraps
from flask import Flask, request, jsonify, session
from flask_login import current_user, login_required, LoginManager
from flask_restful import Resource as RestResource, Api 
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
from config import Config
from db import db
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

Session(app)

CORS(app)

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

from models import (
    User, LearningPath, Module, Resource, Feedback,Comment,
    Reply, Challenge, Achievement, Leaderboard, ModuleResource,
    UserAchievement, UserLearningPath, UserChallenge,
    QuizContent, QuizSubmission
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    
class AllLearningPaths(RestResource):
    def get(self):
        """Fetches all learning paths."""
        learning_paths = LearningPath.query.all()
        return [{"id": path.id, "name": path.title, "description": path.description} for path in learning_paths], 200

class EnrollLearningPath(RestResource):
    @login_required
    def post(self, learning_path_id):
        """Allows a learner to enroll in a learning path."""
        learning_path = LearningPath.query.get_or_404(learning_path_id)
        
        # Check if user is already enrolled
        if UserLearningPath.query.filter_by(user_id=current_user.id, learning_path_id=learning_path_id).first():
            return {"message": "Already enrolled in this learning path"}, 200
        
        enrollment = UserLearningPath(user_id=current_user.id, learning_path_id=learning_path_id)
        db.session.add(enrollment)
        db.session.commit()

        return {"message": f"Enrolled in {learning_path.name} successfully"}, 201

# Access modules and resources only if the learner is enrolled
class LearningPathModules(RestResource):
    @login_required
    def get(self, learning_path_id):
        """Fetches all modules in an enrolled learning path for the learner."""
        # Verify enrollment
        if not UserLearningPath.query.filter_by(user_id=current_user.id, learning_path_id=learning_path_id).first():
            return {"message": "Enroll in the learning path first"}, 403

        modules = Module.query.filter_by(learning_path_id=learning_path_id).all()
        return [{"id": module.id, "name": module.name} for module in modules], 200

class ModuleResources(RestResource):
    @login_required
    def get(self, module_id):
        """Fetches resources within a specific module."""
        module = Module.query.get_or_404(module_id)
        
        # Ensure learner is enrolled in the learning path
        if not UserLearningPath.query.filter_by(user_id=current_user.id, learning_path_id=module.learning_path_id).first():
            return {"message": "Enroll in the learning path first"}, 403

        resources = Resource.query.filter_by(module_id=module_id).all()
        return [{"id": resource.id, "title": resource.title} for resource in resources], 200

# Contributor permission required for creating learning paths, modules, and resources
def contributor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Contributor':
            return jsonify({"error": "Contributor access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

class CreateLearningPath(RestResource):
    @contributor_required
    def post(self):
        """Allows a contributor to create a new learning path."""
        data = request.json
        name = data.get("name")
        description = data.get("description")

        if not name:
            return {"message": "Name is required"}, 400

        new_path = LearningPath(name=name, description=description)
        db.session.add(new_path)
        db.session.commit()

        return {"message": f"Learning path {name} created successfully"}, 201

class CreateModule(RestResource):
    @contributor_required
    def post(self, learning_path_id):
        """Allows a contributor to create a module within a learning path."""
        learning_path = LearningPath.query.get_or_404(learning_path_id)
        data = request.json
        name = data.get("name")

        if not name:
            return {"message": "Module name is required"}, 400

        new_module = Module(name=name, learning_path_id=learning_path_id)
        db.session.add(new_module)
        db.session.commit()

        return {"message": f"Module {name} created successfully under {learning_path.name}"}, 201

class CreateResource(RestResource):
    @contributor_required
    def post(self, module_id):
        """Allows a contributor to add a resource to a module."""
        module = Module.query.get_or_404(module_id)
        data = request.json
        title = data.get("title")
        content = data.get("content")

        if not (title and content):
            return {"message": "Title and content are required"}, 400

        new_resource = Resource(title=title, content=content, module_id=module_id)
        db.session.add(new_resource)
        db.session.commit()

        return {"message": f"Resource '{title}' created successfully in module '{module.name}'"}, 201


# Feedback Routes
# decorator function to wrap the Feedback function
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
   def post(self):
       if 'user_id' not in session:
           return {"message": "Unauthorized access"}, 401
          
       data = request.json
       content = data.get('content')
      
       if not content:
           return {"message": "Content is required"}, 400
      
       new_comment = Comment(
           content=content,
           user_id=session['user_id']
       )
       db.session.add(new_comment)
       db.session.commit()
      
       return {
           "message": "Comment added successfully",
           "comment": new_comment.to_dict()
       }, 201


   def get(self):
       comments = Comment.query.all()
       return {
           'comments': [comment.to_dict() for comment in comments]
       }, 200
  
   def put(self, comment_id):
       if 'user_id' not in session:
           return {"message": "Unauthorized access"}, 401
          
       comment = Comment.query.get_or_404(comment_id)
      
     
       if comment.user_id != session['user_id']:
           return {"message": "Unauthorized to edit this comment"}, 403
          
       data = request.json
       if not data or not data.get('content'):
           return {'message': 'Content is required'}, 400
      
       comment.content = data['content']
       db.session.commit()


       return {
           'message': 'Comment updated successfully',
           'comment': comment.to_dict()
       }, 200
  
   def delete(self, comment_id):
       if 'user_id' not in session:
           return {"message": "Unauthorized access"}, 401
          
       comment = Comment.query.get_or_404(comment_id)
      
      
       if comment.user_id != session['user_id']:
           return {"message": "Unauthorized to delete this comment"}, 403
          
       db.session.delete(comment)
       db.session.commit()


       return {'message': 'Comment deleted successfully'}, 204
   

class Replies(RestResource):
   def post(self, comment_id):
       if 'user_id' not in session:
           return {"message": "Unauthorized access"}, 401
          
       comment = Comment.query.get_or_404(comment_id)
       data = request.json
      
       if not data or not data.get('content'):
           return {"message": "Content is required"}, 400
      
       new_reply = Reply(
           content=data['content'],
           user_id=session['user_id'],
           comment_id=comment_id
       )
       db.session.add(new_reply)
       db.session.commit()


       return {
           'message': 'Reply added successfully',
           'reply': new_reply.to_dict()
       }, 201
  
   def get(self, comment_id):
       comment = Comment.query.get_or_404(comment_id)
       return {
           'comment_id': comment_id,
           'replies': [reply.to_dict() for reply in comment.replies]
       }, 200
  
   def put(self, comment_id, reply_id):
       if 'user_id' not in session:
           return {"message": "Unauthorized access"}, 401
          
       reply = Reply.query.filter_by(
           comment_id=comment_id,
           id=reply_id
       ).first_or_404()
      
      
       if reply.user_id != session['user_id']:
           return {"message": "Unauthorized to edit this reply"}, 403
          
       data = request.json
       if not data or not data.get('content'):
           return {'message': 'Content is required'}, 400
      
       reply.content = data['content']
       db.session.commit()


       return {
           'message': 'Reply updated successfully',
           'reply': reply.to_dict()
       }, 200
  
   def delete(self, comment_id, reply_id):
       if 'user_id' not in session:
           return {"message": "Unauthorized access"}, 401
          
       reply = Reply.query.filter_by(
           comment_id=comment_id,
           id=reply_id
       ).first_or_404()
      
      
       if reply.user_id != session['user_id']:
           return {"message": "Unauthorized to delete this reply"}, 403
          
       db.session.delete(reply)
       db.session.commit()


       return {'message': 'Reply deleted successfully'}, 204

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

# challenge Routes
# decorator fumction to wrap the challenge function
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

class Challenges(RestResource):
    def get(self, challenge_id):
        """Allows users to view challenge details."""
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return {"error": "Challenge not found"}, 404
        return challenge.to_dict(), 200

    @admin_required
    def put(self, challenge_id):
        """Allows admin to update challenge details."""
        data = request.get_json()
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return {"error": "Challenge not found"}, 404
        try:
            for key, value in data.items():
                setattr(challenge, key, value)
            db.session.commit()
            return challenge.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"error": "Challenge update failed", "message": str(e)}, 400

    @admin_required
    def delete(self, challenge_id):
        """Allows admin to delete a challenge."""
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return {"error": "Challenge not found"}, 404
        db.session.delete(challenge)
        db.session.commit()
        return {"message": "Challenge deleted successfully"}, 204

    @login_required
    def post(self, challenge_id):
        """Allows a logged-in user to mark a challenge as completed."""
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return {"error": "Challenge not found"}, 404

        # Check if user has already marked it as completed
        user_challenge = UserChallenge.query.filter_by(user_id=current_user.id, challenge_id=challenge_id).first()
        if user_challenge and user_challenge.completed:
            return {"message": "Challenge already marked as completed"}, 200

        # Mark challenge as completed
        if not user_challenge:
            user_challenge = UserChallenge(user_id=current_user.id, challenge_id=challenge_id, completed=True)
            db.session.add(user_challenge)
        else:
            user_challenge.completed = True

        db.session.commit()
        return {"message": "Challenge marked as completed"}, 200


class Achievements(RestResource):
    def get(self, user_id):
        # Query all achievements related to a specific user
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
        
        achievements = [
            {
                "id": achievement.achievement.id,
                "name": achievement.achievement.name,
                "description": achievement.achievement.description,
                "icon_url": achievement.achievement.icon_url,
                "points_required": achievement.achievement.points_required
            }
            for achievement in user_achievements
        ]
        
        return jsonify(achievements)

class UserProfile(RestResource):
    def get(self):
        """Fetches the profile details of the currently logged-in user."""
        user_id = current_user.id
        user = User.query.get(user_id)
        
        if not user:
            return {"message": "User not found"}, 404

        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
        return profile_data, 200


api.add_resource(UserProfile, '/profile')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(UpdateRole, '/update_role')
api.add_resource(Logout, '/logout')
api.add_resource(AllLearningPaths, '/learning_paths')
api.add_resource(EnrollLearningPath, '/learning_path/<int:learning_path_id>/enroll')
api.add_resource(LearningPathModules, '/learning_path/<int:learning_path_id>/modules')
api.add_resource(ModuleResources, '/module/<int:module_id>/resources')
api.add_resource(CreateLearningPath, '/contributor/learning_path')
api.add_resource(CreateModule, '/contributor/learning_path/<int:learning_path_id>/module')
api.add_resource(CreateResource, '/contributor/module/<int:module_id>/resource')
api.add_resource(Feedbacks, '/feedbacks')
api.add_resource(FeedbackResource, '/feedback/<int:id>')
api.add_resource(Comments, '/comments', '/comments/<int:comment_id>')
api.add_resource(Replies, '/comments/<int:comment_id>/replies')
api.add_resource(Quizzes, '/modules/<int:module_id>/quizzes')
api.add_resource(QuizContent, '/quizzes/<int:quiz_id>/content')
api.add_resource(QuizSubmission, '/quizzes/<int:quiz_id>/submit')
api.add_resource(Challenges, '/challenge/<int:id>')
api.add_resource(Achievements, '/users/<int:user_id>/achievements')

@app.route("/")
def home():
    return "<h1>Welcome here. You better work!</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
