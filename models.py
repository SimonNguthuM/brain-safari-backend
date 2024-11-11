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

    # Relationships with other models
    leaderboard_entry = relationship('Leaderboard', backref='user', uselist=False)  # One-to-one with Leaderboard
    feedback = relationship('Feedback', back_populates='user')  # One-to-many with Feedback
    comments = relationship('Comment', back_populates='user')  # One-to-many with Comments
    replies = relationship('Reply', back_populates='user')  # One-to-many with Replies
    enrolled_paths = relationship('UserLearningPath', back_populates='user')  # Many-to-many with Learning Paths
    challenges = relationship('UserChallenge', back_populates='user')  # Many-to-many with Challenges
    achievements = relationship('UserAchievement', back_populates='user')  # Many-to-many with Achievements
    quiz_submissions = relationship('QuizSubmission', back_populates='user')  # One-to-many with Quiz Submissions


class LearningPath(db.Model):
    __tablename__ = 'learning_paths'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)

    modules = db.relationship('Module', back_populates='learning_path')
    enrolled_users = db.relationship('UserLearningPath', back_populates='learning_path')

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    learningpath_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))

    learning_path = db.relationship('LearningPath', back_populates='modules')
    resources = db.relationship('ModuleResource', back_populates='module')
    quiz_content = db.relationship('QuizContent', back_populates='module')

class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    url = db.Column(db.String(200))
    type = db.Column(db.Enum('Video', 'Article', 'Tutorial', name='resource_type'))
    description = db.Column(db.Text)
    contributor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    feedback = db.relationship('Feedback', back_populates='resource')
    modules = db.relationship('ModuleResource', back_populates='resource')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'))
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)

    # Relationships
    user = db.relationship("User", back_populates="feedback")
    resource = db.relationship("Resource", back_populates="feedback")

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



# challenge model
class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
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
    users = db.relationship("UserAchievement", back_populates="achievement")


class Leaderboard(db.Model, SerializerMixin):
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer, default=0)  # Leaderboard score
    
    # Foreign key relationship with User
    user = relationship('User', back_populates='leaderboard_entry')


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
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=True) 
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_content.id'), nullable=False)  # Refers to a quiz in QuizContent
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='quiz_submissions')  
    quiz = relationship('QuizContent', back_populates='submissions', foreign_keys=[quiz_id])

    def __repr__(self):
        return f"<QuizSubmission(id={self.id}, user_id={self.user_id}, quiz_id={self.quiz_id}, score={self.score})>"
    

