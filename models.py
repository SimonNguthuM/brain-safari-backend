from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship




class User(db.Model):
    __tablename__ = 'users'
    pass

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    pass

class Module(db.Model):
    __tablename__ = 'modules'
    pass

class Resource(db.Model):
    __tablename__ = 'resources'
    pass

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

