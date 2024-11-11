from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    pass

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'

    learning_path_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    rating = db.Column(db.Integer)

    modules = db.relationship('Module', back_populates='learning_path')
    enrolled_users = db.relationship('UserLearningPath', back_populates='learning_path')

class Module(db.Model):
    __tablename__ = 'modules'
    
    module_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    learningpath_id = db.Column(db.Integer, db.ForeignKey('learning_paths.learning_path_id'))

    learning_path = db.relationship('LearningPath', back_populates='modules')
    resources = db.relationship('ModuleResource', back_populates='module')
    quiz_content = db.relationship('QuizContent', back_populates='module')

class Resource(db.Model):
    __tablename__ = 'resources'

    resource_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    type = db.Column(db.Enum('Video', 'Article', 'Tutorial', name='resource_type'))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    feedbacks = db.relationship('Feedback', back_populates='resource')
    modules = db.relationship('ModuleResource', back_populates='resource')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    pass

class Comment(db.Model):
    __tablename__ = 'comments'
    pass

class Reply(db.Model):
    __tablename__ = 'replies'
    pass

class Challenge(db.Model):
    __tablename__ = 'challenges'
    pass

class Achievement(db.Model):
    __tablename__ = 'achievements'
    pass

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    pass

class ModuleResource(db.Model):
    __tablename__ = 'module_resource'
    pass

class UserAchievement(db.Model):
    __tablename__ = 'user_achievement'
    pass

class UserChallenge(db.Model):
    __tablename__ = 'user_challenge'
    pass

class UserLearningPath(db.Model):
    __tablename__ = 'user_learningpath'
    pass

class QuizContent(db.Model):
    __tablename__ = 'quiz_content'
    pass

class QuizSubmission(db.Model):
    __tablename__ = 'quiz_submission'
    pass

