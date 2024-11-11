from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship

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
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship("User", back_populates="comments")
    replies = db.relationship("Reply", back_populates="comment")

    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, content='{self.content[:20]}...')>"


class Reply(db.Model):
    __tablename__ = 'replies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship("User", back_populates="replies")
    comment = db.relationship("Comment", back_populates="replies")

    def __repr__(self):
        return f"<Reply(id={self.id}, user_id={self.user_id}, comment_id={self.comment_id}, content='{self.content[:20]}...')>"




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
    __tablename__ = 'module_resources'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    module = db.relationship("Module", back_populates="resources")
    resource = db.relationship("Resource", back_populates="modules")

    def __repr__(self):
        return f"<ModuleResource(id={self.id}, module_id={self.module_id}, resource_id={self.resource_id})>"



class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

   
    user = db.relationship("User", back_populates="achievements")
    achievement = db.relationship("Achievement", back_populates="users")
    
    def __repr__(self):
        return f"<UserAchievement(id={self.id}, user_id={self.user_id}, achievement_id={self.achievement_id})>"

class UserLearningPath(db.Model):
    __tablename__ = 'user_learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    progress_percentage = db.Column(db.Integer)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

   
    user = db.relationship("User", back_populates="enrolled_paths")
    learning_path = db.relationship("LearningPath", back_populates="enrolled_users")

    def __repr__(self):
        return f"<UserLearningPath(id={self.id}, user_id={self.user_id}, learning_path_id={self.learning_path_id})>"


class UserChallenge(db.Model):
    __tablename__ = 'user_challenges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    completed_at = db.Column(db.DateTime)

    
    user = db.relationship("User", back_populates="challenges")
    challenge = db.relationship("Challenge", back_populates="users")

    def __repr__(self):
        return f"<UserChallenge(id={self.id}, user_id={self.user_id}, challenge_id={self.challenge_id})>"




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
    

