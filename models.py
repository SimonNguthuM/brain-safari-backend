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

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(200))
    points_required = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship("UserAchievement", back_populates="achievement")


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
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True) 
    parent_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=True)  # Self-referencing foreign key
    type = db.Column(db.String, nullable=False)  # "quiz", "question", or "option"
    content_text = db.Column(db.Text, nullable=False)  # Quiz title, question text, or option text
    points = db.Column(db.Integer, nullable=True)  # Points for questions; NULL for quizzes and options
    is_correct = db.Column(db.Boolean, nullable=True)  # Only for options; true if correct, null otherwise
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship('QuizContent', remote_side=[id], back_populates='children')  # Self-referential relationship
    children = relationship('QuizContent', back_populates='parent')  # Allows nesting (questions under quizzes)

    def __repr__(self):
        return f"<QuizContent(id={self.id}, type={self.type}, content_text='{self.content_text[:20]}...', points={self.points})>"


class QuizSubmission(db.Model):
    __tablename__ = 'quiz_submission'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=False)  # Refers to a quiz in QuizContent
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='quiz_submissions')  
    quiz = relationship('QuizContent', back_populates='submissions', foreign_keys=[quiz_id])

    def __repr__(self):
        return f"<QuizSubmission(id={self.id}, user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score})>"


