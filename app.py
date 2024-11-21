from functools import wraps
from flask import Flask, request, jsonify, session, make_response, abort
from flask_login import current_user, login_required, LoginManager, login_user
from flask_restful import Resource as RestResource, Api 
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from db import db
from datetime import datetime
import logging
import json


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

CORS(app, supports_credentials=True)

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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__) 

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    users = User.query.order_by(User.points.desc()).limit(8).all()  
    result = [{"username": user.username.split()[0], "points": user.points} for user in users]
    return jsonify(result)

@app.route('/users/<username>/points', methods=['GET'])
def get_user_points(username):
    user = User.query.filter_by(username=username).first()
    
    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "points": user.points
        })
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/admin/users', methods=['GET'])
@login_required
def get_users():
    """Admin route to fetch all users."""
    if current_user.role != 'Admin':
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return jsonify(user_list), 200


@app.route('/admin/users/<int:user_id>/role', methods=['PATCH'])
@login_required
def update_user_role(user_id):
    """Admin route to update a user's role."""
    if current_user.role != 'Admin':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.get_json()
        new_role = data.get("role")

        valid_roles = ['Learner', 'Contributor']
        if new_role not in valid_roles:
            return jsonify({"error": f"Invalid role. Valid roles are: {', '.join(valid_roles)}"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.role = new_role
        db.session.commit()

        return jsonify({"message": "Role updated successfully", "user": user.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', "Learner")  

        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        valid_roles = ['Learner', 'Contributor', 'Admin']
        if role not in valid_roles:
            return jsonify({"error": f"Invalid role: {role}. Valid roles are: {', '.join(valid_roles)}"}), 400

        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created successfully", "role": user.role}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/login', methods=['POST'])
def login():
    print("Login route accessed")
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)

            session['role'] = user.role

            response_data = {
                "message": "Login successful",
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "points": user.points  
            }

            response = make_response(jsonify(response_data))

            response.set_cookie(
                "session_token",
                value=user.username,
                httponly=True,
                secure=True,  
                samesite="None",
            )
            print("Cookie set:", response.headers) 
            return response
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/authenticate', methods=['GET'])
@login_required
def authenticate():
    print("authenticate route accessed")
    try:
        user = current_user
        if user.is_authenticated:
            return jsonify({
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }), 200
        else:
            return jsonify({"error": "User not authenticated"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    print("Logout route accessed")
    session.pop('user', None)
    response = make_response(jsonify({"message": "Logged out"}))
    response.delete_cookie(
        "session_token", 
        httponly=True, 
        secure=True, 
        samesite="None"  
    )
    response.delete_cookie(
        "session", 
        httponly=True, 
        secure=True, 
        samesite="None"  
    )
    return response

@app.route('/learning-paths/enrolled', methods=['GET'])
@login_required
def get_enrolled_paths():
    user_id = current_user.id
    logger.debug(f"Fetching enrolled paths for user_id: {user_id}")
    
    enrolled_paths = db.session.query(LearningPath).join(
        UserLearningPath, LearningPath.id == UserLearningPath.learning_path_id
    ).filter(UserLearningPath.user_id == user_id).all()
    
    enrolled_paths_dict = [path.to_dict() for path in enrolled_paths]
    logger.debug(f"Enrolled paths: {enrolled_paths_dict}")
    
    return jsonify(enrolled_paths_dict)


@app.route('/learning-paths', methods=['GET'])
@login_required
def get_available_paths():
    user_id = current_user.id
    logger.debug(f"Fetching available learning paths for user_id: {user_id}")
    
    enrolled_paths_ids = db.session.query(UserLearningPath.learning_path_id).filter_by(user_id=user_id).all()
    enrolled_paths_ids = [path_id for (path_id,) in enrolled_paths_ids]
    
    available_paths = LearningPath.query.filter(LearningPath.id.notin_(enrolled_paths_ids)).all()
    
    available_paths_dict = [path.to_dict() for path in available_paths]
    logger.debug(f"Available paths: {available_paths_dict}")
    
    return jsonify(available_paths_dict)


@app.route('/learning-paths/<int:path_id>/enroll', methods=['POST'])
@login_required
def enroll_path(path_id):
    user_id = current_user.id
    logger.debug(f"User {user_id} attempting to enroll in path {path_id}.")
    
    existing_enrollment = UserLearningPath.query.filter_by(user_id=user_id, learning_path_id=path_id).first()
    if existing_enrollment:
        logger.warning(f"User {user_id} is already enrolled in path {path_id}.")
        return jsonify({"error": "Already enrolled"}), 400
    
    new_enrollment = UserLearningPath(user_id=user_id, learning_path_id=path_id)
    db.session.add(new_enrollment)
    db.session.commit()
    logger.info(f"User {user_id} successfully enrolled in path {path_id}.")
    
    enrolled_path = LearningPath.query.get(path_id)
    logger.debug(f"Enrolled path details: {enrolled_path.to_dict()}")
    
    return jsonify({"learning_path": enrolled_path.to_dict()}), 201

@app.route('/learning-paths/<int:path_id>/modules', methods=['GET'])
@login_required
def get_modules_for_learning_path(path_id):
    logger.debug(f"Fetching modules for learning path with ID: {path_id}")
    
    modules = Module.query.filter_by(learning_path_id=path_id).all()
    
    logger.debug(f"Modules found: {[module.to_dict() for module in modules]}")
    
    return jsonify([module.to_dict() for module in modules])


@app.route('/modules/<int:module_id>', methods=['GET'])
@login_required
def get_module_details(module_id):
    logger.debug(f"Fetching details for module with ID: {module_id}")
    
    module = Module.query.get_or_404(module_id)
    
    logger.debug(f"Module details: {module.to_dict()}")
    
    return jsonify(module.to_dict())

@app.route('/modules/<int:module_id>/resources', methods=['GET'])
@login_required
def get_resources_for_module(module_id):
    logger.debug(f"Fetching resources for module with ID: {module_id}")
    
    module_resources = db.session.query(ModuleResource).filter_by(module_id=module_id).all()
    
    resources = [
        {
            "id": module_resource.resource.id,
            "title": module_resource.resource.title,
            "description": module_resource.resource.description,
            "url": module_resource.resource.url,
        }
        for module_resource in module_resources
    ]
    
    logger.debug(f"Resources found for module {module_id}: {resources}")
    
    return jsonify(resources)

@app.route('/learning-paths', methods=['POST'])
@login_required
def create_learning_path():
    if current_user.role != 'Contributor':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    new_path = LearningPath(
        title=data.get("title"),
        description=data.get("description"),
        contributor_id=current_user.id,
    )
    db.session.add(new_path)
    db.session.commit()

    if data.get("modules"):
        for module_data in data.get("modules"):
            new_module = Module(
                title=module_data.get("title"),
                description=module_data.get("description"),
                learning_path_id=new_path.id
            )
            db.session.add(new_module)
            db.session.commit()

            if module_data.get("resources"):
                for resource_data in module_data.get("resources"):
                    new_resource = Resource(
                        title=resource_data.get("title"),
                        url=resource_data.get("url"),
                        type=resource_data.get("type"),
                        description=resource_data.get("description"),
                        contributor_id=current_user.id
                    )
                    db.session.add(new_resource)
                    db.session.commit()

                    module_resource = ModuleResource(
                        module_id=new_module.id,
                        resource_id=new_resource.id
                    )
                    db.session.add(module_resource)

    db.session.commit()
    return jsonify(new_path.to_dict()), 201

@app.route('/created-learning-paths', methods=['GET'])
@login_required
def get_learning_paths():
    learning_paths = LearningPath.query.filter_by(contributor_id=current_user.id).all()
    return jsonify([path.to_dict() for path in learning_paths])

@app.route('/update-learning-path/<int:path_id>', methods=['GET', 'PUT'])
@login_required
def update_learning_path(path_id):
    if current_user.role != 'Contributor':
        return jsonify({"error": "Unauthorized"}), 403

    learning_path = LearningPath.query.get(path_id)
    if not learning_path:
        return jsonify({"error": "Learning path not found"}), 404

    if learning_path.contributor_id != current_user.id:
        return jsonify({"error": "Unauthorized to edit this learning path"}), 403

    if request.method == 'GET':
        return jsonify(learning_path.to_dict()), 200

    if request.method == 'PUT':
        data = request.get_json()

        learning_path.title = data.get("title", learning_path.title)
        learning_path.description = data.get("description", learning_path.description)

        if data.get("modules"):
            for module in learning_path.modules:
                db.session.delete(module)

            for module_data in data.get("modules"):
                new_module = Module(
                    title=module_data.get("title"),
                    description=module_data.get("description"),
                    learning_path_id=learning_path.id
                )
                db.session.add(new_module)

                if module_data.get("resources"):
                    for resource_data in module_data.get("resources"):
                        new_resource = Resource(
                            title=resource_data.get("title"),
                            url=resource_data.get("url"),
                            type=resource_data.get("type"),
                            description=resource_data.get("description"),
                            contributor_id=current_user.id
                        )
                        db.session.add(new_resource)

                        module_resource = ModuleResource(
                            module_id=new_module.id,
                            resource_id=new_resource.id
                        )
                        db.session.add(module_resource)

        db.session.commit()
        return jsonify(learning_path.to_dict()), 200
    
@app.route('/modules/<int:module_id>/quizzes', methods=['POST'])
@login_required
def create_quiz_for_module(module_id):
    if current_user.role != 'Contributor':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    logger.debug(f"Creating quiz for module {module_id} by user {current_user.id}. Data: {data}")

    new_quiz = QuizContent(
        module_id=module_id,
        question=data.get("question"),
        options=json.dumps(data.get("options")),
        correct_option=data.get("correct_option"),
    )
    db.session.add(new_quiz)
    db.session.commit()
    logger.info(f"Quiz created for module {module_id}: {new_quiz.to_dict()}")

    return jsonify(new_quiz.to_dict()), 201


@app.route('/modules/<int:module_id>/quizzes', methods=['GET'])
@login_required
def get_quizzes_for_module(module_id):
    logger.debug(f"Fetching quizzes for module {module_id}")

    quizzes = QuizContent.query.filter_by(module_id=module_id).all()
    quizzes_dict = [quiz.to_dict() for quiz in quizzes]
    logger.debug(f"Quizzes found for module {module_id}: {quizzes_dict}")

    return jsonify(quizzes_dict)


@app.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    data = request.get_json()
    logger.debug(f"Submitting quiz {quiz_id} for user {current_user.id}. Data: {data}")

    quiz = QuizContent.query.get_or_404(quiz_id)

    selected_option = data.get("selected_option")

    score = quiz.points if selected_option == quiz.correct_option else 0

    submission = QuizSubmission(
        user_id=current_user.id,
        quiz_id=quiz_id,
        selected_option=selected_option,
        score=score,
    )

    db.session.add(submission)
    db.session.commit()

    submission.update_user_points()

    logger.info(f"Quiz {quiz_id} submitted by user {current_user.id}: {submission.to_dict()}")

    return jsonify({"message": "Quiz submitted", "score": score}), 200


@app.route('/comments', methods=['POST'])
def create_comment():
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')

    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")

    comment = Comment(user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201

@app.route('/replies', methods=['POST'])
def create_reply():
    data = request.get_json()
    user_id = data.get('user_id')
    comment_id = data.get('comment_id')
    content = data.get('content')

    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")

    comment = Comment.query.get(comment_id)
    if not comment:
        abort(404, description="Comment not found")

    reply = Reply(user_id=user_id, comment_id=comment_id, content=content)
    db.session.add(reply)
    db.session.commit()

    return jsonify(reply.to_dict()), 201

@app.route('/comments', methods=['POST'])
def post_comment():
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')

    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")

    comment = Comment(user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        **comment.to_dict(),
        "username": user.username,
        "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201

@app.route('/replies', methods=['POST'])
def post_reply():
    data = request.get_json()
    user_id = data.get('user_id')
    comment_id = data.get('comment_id')
    content = data.get('content')

    user = User.query.get(user_id)
    if not user:
        abort(404, description="User not found")

    comment = Comment.query.get(comment_id)
    if not comment:
        abort(404, description="Comment not found")

    reply = Reply(user_id=user_id, comment_id=comment_id, content=content)
    db.session.add(reply)
    db.session.commit()

    return jsonify({
        **reply.to_dict(),
        "username": user.username,
        "created_at": reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201

@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    comments_data = []

    for comment in comments:
        replies = Reply.query.filter_by(comment_id=comment.id).all()
        replies_data = [reply.to_dict() for reply in replies]
        comment_data = comment.to_dict()
        comment_data["replies"] = replies_data
        comment_data["replies_count"] = len(replies_data)
        comment_data["username"] = comment.user.username
        comment_data["created_at"] = comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        comments_data.append(comment_data)
    
    return jsonify(comments_data), 200

@app.route('/comments/user/<int:user_id>/replies', methods=['GET'])
def get_user_comments_and_replies(user_id):
    comments = Comment.query.filter_by(user_id=user_id).all()
    comments_data = []

    for comment in comments:
        replies = Reply.query.filter_by(comment_id=comment.id).all()
        replies_data = [reply.to_dict() for reply in replies]
        
        comment_data = comment.to_dict()
        comment_data["replies"] = replies_data
        comment_data["replies_count"] = len(replies_data)
        comment_data["username"] = comment.user.username
        comment_data["created_at"] = comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        comments_data.append(comment_data)

    return jsonify({"comments": comments_data}), 200

@app.route('/feedbacks', methods=['POST'])
def submit_feedback():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 403

    data = request.get_json()

    resource_id = data.get('resource_id')
    comment = data.get('content')
    rating = data.get('rating')

    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({"error": "Resource not found"}), 404

    feedback = Feedback(
        user_id=current_user.id,
        resource_id=resource_id,
        comment=comment,
        rating=rating
    )

    db.session.add(feedback)
    db.session.commit()

    return jsonify({
        "feedback_id": feedback.id,
        "comment": feedback.comment,
        "rating": feedback.rating,
        "resource_id": resource_id,
        "user_id": current_user.id,
    }), 201

@app.route('/resources/<int:resource_id>/feedbacks', methods=['GET'])
def get_feedbacks_for_resource(resource_id):
    """Fetch all feedbacks for a given resource."""
    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({"error": "Resource not found"}), 404

    feedbacks = Feedback.query.filter_by(resource_id=resource_id).all()
    feedback_list = [
        {
            "feedback_id": feedback.id,
            "user_id": feedback.user_id,
            "comment": feedback.comment,
            "rating": feedback.rating,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
        }
        for feedback in feedbacks
    ]

    return jsonify(feedback_list), 200


@app.route('/users/<username>/achievements', methods=['GET'])
def get_user_achievements(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    achievements = Achievement.query.all()
    user_achievements = UserAchievement.query.filter_by(user_id=user.id).all()

    new_achievements = []
    for achievement in achievements:
        if user.points >= achievement.points_required:
            if not any(ua.achievement_id == achievement.id for ua in user_achievements):
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id,
                    earned_at=datetime.utcnow()
                )
                db.session.add(user_achievement)
                db.session.commit()
                new_achievements.append(achievement)

    current_achievements = [
        {
            "id": ua.achievement.id,
            "name": ua.achievement.name,
            "description": ua.achievement.description,
            "icon_url": ua.achievement.icon_url,
            "earned_at": ua.earned_at.isoformat()
        }
        for ua in user_achievements
    ]

    current_achievements.extend([
        {
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "icon_url": achievement.icon_url,
            "earned_at": datetime.utcnow().isoformat()
        }
        for achievement in new_achievements
    ])

    return jsonify(current_achievements)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
