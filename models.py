from db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin


class User(db.Model, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Admin, Contributor, Learner
    points = db.Column(db.Integer, default=0)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    leaderboard_entry = relationship('Leaderboard', back_populates='user', uselist=False)
    
    comments = relationship('Comment', back_populates='user', cascade='all, delete-orphan')
   
    enrolled_paths = relationship('UserLearningPath', back_populates='user')
    challenges = relationship('UserChallenge', back_populates='user')
    achievements = relationship('UserAchievement', back_populates='user')
    quiz_submissions = relationship('QuizSubmission', back_populates='user')


class LearningPath(db.Model):
    __tablename__ = 'learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)

    # Relationships
    modules = relationship('Module', back_populates='learning_path')
    enrolled_users = relationship('UserLearningPath', back_populates='learning_path')


class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))

    # Relationships
    learning_path = relationship('LearningPath', back_populates='modules')
    resources = relationship('ModuleResource', back_populates='module')
    quiz_content = relationship('QuizContent', back_populates='module')


class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    type = db.Column(db.Enum('Video', 'Article', 'Tutorial', name='resource_type'))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    feedback = relationship('Feedback', back_populates='resource')
    modules = relationship('ModuleResource', back_populates='resource')
    comments = db.relationship('Comment', back_populates='resource', cascade= 'all, delete-orphan')

# class Response(db.Model):
#     __tablename__ = 'responses'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
#     comment = db.Column(db.Text)
#     rating = db.Column(db.Integer)

#     # Relationships
#     user = db.relationship("User", back_populates="feedback")
#     resource = db.relationship("Resource", back_populates="feedback")
#     replies =db.relationship("Reply", back_populates ="feedback")


# class Reply(db.Model):
#     __tablename__ = 'replies'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
#     content = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime)

#     # Relationships
#     user = db.relationship("User", back_populates="replies")
#     feedback = db.relationship("Feedback", back_populates="replies")

#     def __repr__(self):
#         return f"<Reply(id={self.id}, user_id={self.user_id}, feedback_id={self.feedback_id}, content='{self.content[:20]}...')>"


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_comment_id = db.olumn(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    # Relationships
    user = relationship("User", back_populates="comments")
    resource = db.relationship('Resource', back_populates= 'comments')


class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    resource_id =db.Column(db.Integer, db.ForeignKey('resources.id'))
    description = db.Column(db.Text)
    points_reward = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # Relationships
    users = db.relationship("UserChallenge", back_populates="challenge")


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(200))
    points_required = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("UserAchievement", back_populates="achievement")


class Leaderboard(db.Model, SerializerMixin):
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer, default=0)
    
    # Relationships
    user = relationship('User', back_populates='leaderboard_entry')


class ModuleResource(db.Model):
    __tablename__ = 'module_resources'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="resources")
    resource = relationship("Resource", back_populates="modules")


class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")


class UserLearningPath(db.Model):
    __tablename__ = 'user_learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    progress_percentage = db.Column(db.Integer)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = relationship("User", back_populates="enrolled_paths")
    learning_path = relationship("LearningPath", back_populates="enrolled_users")


class UserChallenge(db.Model):
    __tablename__ = 'user_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = relationship("User", back_populates="challenges")
    challenge = relationship("Challenge", back_populates="users")


class QuizContent(db.Model):
    __tablename__ = 'quiz_content'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=True)
    type = db.Column(db.String, nullable=False)  # "quiz", "question", or "option"
    content_text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    module = relationship("Module", back_populates="quiz_content")
    parent = relationship('QuizContent', remote_side=[id], back_populates='children')
    children = relationship('QuizContent', back_populates='parent')


class QuizSubmission(db.Model):
    __tablename__ = 'quiz_submission'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='quiz_submissions')
    quiz = relationship('QuizContent', back_populates='submissions')
