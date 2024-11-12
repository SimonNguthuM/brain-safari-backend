from flask import Flask, request, jsonify
from flask_restful import Resource, Api
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
    User, LearningPath, Module, Resource, Feedback, Comment, 
    Reply, Challenge, Achievement, Leaderboard, ModuleResource, 
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

class Comments(Resource):
    def get(self):
        return {"message": "Comments"}

# Route for accessing quizzes within a module
class Quizzes(Resource):
    def get(self, module_id):
        module = Module.query.get_or_404(module_id)
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
class QuizContent(Resource):
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
class QuizSubmission(Resource):
    def post(self, quiz_id):
        data = request.json
        user_id = data.get("user_id")
        user_answers = data.get("answers")  
        
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

class Challenges(Resource):
    def get(self, id):
        return {"message": f"Challenge {id}"}

class Achievements(Resource):
    def get(self):
        achievements = Achievement.query.all()
        return jsonify([
            {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "badge_icon_url": achievement.badge_icon_url,
                "points": achievement.points,
                "xp_url": achievement.xp_url,
                "created_at": achievement.created_at
            } for achievement in achievements
        ])

api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(LearningPaths, '/learning_paths')
api.add_resource(LearningPathDetail, '/learning_path/<int:id>')
api.add_resource(Modules, '/modules')
api.add_resource(ModuleDetail, '/module/<int:id>')
api.add_resource(Resources, '/resources')
api.add_resource(ResourceDetail, '/resource/<int:id>')
api.add_resource(Feedbacks, '/feedback')
api.add_resource(Comments, '/comments')
api.add_resource(Quizzes, '/modules/<int:module_id>/quizzes')
api.add_resource(QuizContent, '/quizzes/<int:quiz_id>/content')
api.add_resource(QuizSubmission, '/quizzes/<int:quiz_id>/submit')
api.add_resource(QuizSubmission, '/quizzes/<int:quiz_id>/score/<int:user_id>')
api.add_resource(Challenges, '/challenge/<int:id>')
api.add_resource(Achievements, '/achievements')

@app.route("/")
def home():
    return "<h1>Welcome back</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
